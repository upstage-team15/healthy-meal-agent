"""
app/agents/graph.py
추천 흐름을 LangGraph StateGraph로 관리한다.
services는 그대로 호출하고, 이 파일은 노드 연결과 재시도 라우팅만 담당한다.
"""

from collections.abc import Callable
from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph

from app.schemas import (
    AgentState,
    FoodItem,
    MealPlan,
    NutritionTotal,
    UserConditions,
    UserProfile,
    ValidationResult,
)
from app.services.condition_extractor import extract_conditions_stub
from app.services.food_retriever import retrieve_foods
from app.services.meal_composer import compose_meal
from app.services.nutrition_calculator import calculate_nutrition
from app.services.validator import validate_meal

MAX_RETRY = 2


class GraphState(TypedDict, total=False):
    user_message: str
    profile: UserProfile
    conditions: UserConditions | None
    candidates_by_role: dict[str, list[FoodItem]]
    candidates: list[FoodItem]
    meal_plan: MealPlan | None
    nutrition_total: NutritionTotal | None
    validation_result: ValidationResult | None
    retry_count: int
    final_response: str


def _flatten_candidates(candidates_by_role: dict[str, list[FoodItem]]) -> list[FoodItem]:
    return [food for foods in candidates_by_role.values() for food in foods]


def _has_candidates(candidates_by_role: dict[str, list[FoodItem]]) -> bool:
    return any(candidates_by_role.values())


def create_graph(extractor: Callable[[str], UserConditions]):
    """추천 StateGraph를 생성한다. extractor는 stub/Solar를 호출부에서 주입한다."""

    def extract_node(state: GraphState) -> GraphState:
        return {"conditions": extractor(state["user_message"])}

    def retrieve_node(state: GraphState) -> GraphState:
        conditions = state["conditions"]
        profile = state.get("profile") or UserProfile()
        validation_result = state.get("validation_result")
        relax = (
            validation_result is not None
            and validation_result.cause == "retrieve"
            and state.get("retry_count", 0) > 0
        )

        candidates_by_role = retrieve_foods(conditions, profile, relax=relax)
        updates: GraphState = {
            "candidates_by_role": candidates_by_role,
            "candidates": _flatten_candidates(candidates_by_role),
        }
        if not _has_candidates(candidates_by_role):
            updates["final_response"] = "조건에 맞는 음식을 찾지 못했습니다. 조건을 완화해 주세요."
        return updates

    def compose_node(state: GraphState) -> GraphState:
        meal_plan = compose_meal(
            state.get("candidates_by_role", {}),
            state["conditions"],
            seed=state.get("retry_count", 0),
        )
        return {"meal_plan": meal_plan}

    def calculate_node(state: GraphState) -> GraphState:
        return {"nutrition_total": calculate_nutrition(state["meal_plan"])}

    def validate_node(state: GraphState) -> GraphState:
        validation_result = validate_meal(
            state["meal_plan"],
            state["nutrition_total"],
            state["conditions"],
            state.get("profile") or UserProfile(),
        )
        updates: GraphState = {"validation_result": validation_result}

        if validation_result.status in ("PASS", "PASS_WITH_WARNING"):
            from app.agents.meal_agent import build_final_response

            final_state = AgentState.model_validate({**state, **updates})
            updates["final_response"] = build_final_response(final_state)
            return updates

        retry_count = state.get("retry_count", 0)
        if retry_count < MAX_RETRY:
            updates["retry_count"] = retry_count + 1
            return updates

        updates["final_response"] = (
            "조건을 모두 만족하는 식단을 찾지 못했어요. 칼로리나 제외 조건을 조금 완화해 주시겠어요?"
        )
        return updates

    def route_after_retrieve(state: GraphState) -> Literal["compose", "end"]:
        return "compose" if _has_candidates(state.get("candidates_by_role", {})) else "end"

    def route_after_validate(state: GraphState) -> Literal["retrieve", "compose", "end"]:
        validation_result = state.get("validation_result")
        if validation_result is None or validation_result.status in ("PASS", "PASS_WITH_WARNING"):
            return "end"
        if state.get("final_response"):
            return "end"
        return "retrieve" if validation_result.cause == "retrieve" else "compose"

    builder = StateGraph(GraphState)
    builder.add_node("extract", extract_node)
    builder.add_node("retrieve", retrieve_node)
    builder.add_node("compose", compose_node)
    builder.add_node("calculate", calculate_node)
    builder.add_node("validate", validate_node)

    builder.add_edge(START, "extract")
    builder.add_edge("extract", "retrieve")
    builder.add_conditional_edges(
        "retrieve",
        route_after_retrieve,
        {"compose": "compose", "end": END},
    )
    builder.add_edge("compose", "calculate")
    builder.add_edge("calculate", "validate")
    builder.add_conditional_edges(
        "validate",
        route_after_validate,
        {"retrieve": "retrieve", "compose": "compose", "end": END},
    )
    return builder.compile()


def run_agent(
    user_message: str,
    profile: UserProfile = None,
    extractor: Callable[[str], UserConditions] = extract_conditions_stub,
) -> AgentState:
    """추천 파이프라인 공개 진입점. 반환 형태는 기존 AgentState와 동일하다."""
    initial_state = AgentState(user_message=user_message, profile=profile or UserProfile())
    graph = create_graph(extractor)
    result = graph.invoke(initial_state.__dict__.copy())
    return AgentState.model_validate(result)
