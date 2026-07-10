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
    IntentType,
    MealPlan,
    NutritionTotal,
    UserConditions,
    UserProfile,
    ValidationResult,
)
from app.services.condition_extractor import extract_conditions_stub
from app.services.food_retriever import retrieve_foods
from app.services.intent_router import classify_intent_stub
from app.services.meal_composer import compose_meal
from app.services.nutrition_calculator import calculate_nutrition
from app.services.nutrition_lookup import answer_nutrition_query
from app.services.validator import validate_meal

MAX_RETRY = 2

# 추천이 아닌 분기에서 돌려줄 정해진 응답 (환각 없이 코드가 안내)
RISKY_RESPONSE = (
    "건강을 해칠 수 있는 요청은 도와드리기 어려워요. "
    "저는 균형 잡힌 한 끼를 추천하는 서비스예요. "
    "칼로리나 영양 목표를 알려주시면 건강한 식단으로 도와드릴게요."
)
OUT_OF_SCOPE_RESPONSE = (
    "저는 건강한 한 끼 식단을 추천하는 서비스예요. "
    "드시고 싶은 느낌(예: 담백한, 얼큰한)이나 칼로리 목표를 말씀해 주시면 추천해드릴게요."
)
NEED_MORE_INFO_RESPONSE = (
    "어떤 한 끼를 원하세요? "
    "예를 들어 '400kcal 이하로 담백하게', '얼큰한 국물 요리'처럼 "
    "칼로리·맛·제외할 재료를 알려주시면 딱 맞게 추천해드릴게요."
)


class GraphState(TypedDict, total=False):
    user_message: str
    profile: UserProfile
    intent: IntentType | None
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


def create_graph(
    extractor: Callable[[str], UserConditions],
    classifier: Callable[[str], IntentType] = classify_intent_stub,
):
    """StateGraph를 생성한다. extractor/classifier는 stub/Solar를 호출부에서 주입한다."""

    def route_node(state: GraphState) -> GraphState:
        intent = classifier(state["user_message"])
        # 어떤 분기로 갔는지 서버 로그로 확인 (디버깅·시연용)
        print(f"[intent] '{state['user_message']}' → {intent}")
        return {"intent": intent}

    def nutrition_query_node(state: GraphState) -> GraphState:
        # 수치는 코드가 DB에서 조회 (LLM이 숫자를 지어내지 않음)
        return {"final_response": answer_nutrition_query(state["user_message"])}

    def risky_node(state: GraphState) -> GraphState:
        return {"final_response": RISKY_RESPONSE}

    def out_of_scope_node(state: GraphState) -> GraphState:
        return {"final_response": OUT_OF_SCOPE_RESPONSE}

    def need_more_info_node(state: GraphState) -> GraphState:
        return {"final_response": NEED_MORE_INFO_RESPONSE}

    def extract_node(state: GraphState) -> GraphState:
        conditions = extractor(state["user_message"])
        print(
            f"[conditions] kcal={conditions.target_kcal}({conditions.kcal_mode}) "
            f"선호={conditions.preferences} 제외={conditions.exclude_foods} "
            f"형태={conditions.meal_style}"
        )
        return {"conditions": conditions}

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

    def route_by_intent(
        state: GraphState,
    ) -> Literal["extract", "nutrition_query", "risky", "out_of_scope", "need_more_info"]:
        # meal_recommend만 추천 파이프라인(extract~)으로, 나머지는 각 응답 노드로 종료
        intent = state.get("intent")
        if intent == "meal_recommend":
            return "extract"
        return intent or "extract"

    builder = StateGraph(GraphState)
    builder.add_node("route", route_node)
    builder.add_node("nutrition_query", nutrition_query_node)
    builder.add_node("risky", risky_node)
    builder.add_node("out_of_scope", out_of_scope_node)
    builder.add_node("need_more_info", need_more_info_node)
    builder.add_node("extract", extract_node)
    builder.add_node("retrieve", retrieve_node)
    builder.add_node("compose", compose_node)
    builder.add_node("calculate", calculate_node)
    builder.add_node("validate", validate_node)

    builder.add_edge(START, "route")
    builder.add_conditional_edges(
        "route",
        route_by_intent,
        {
            "extract": "extract",
            "nutrition_query": "nutrition_query",
            "risky": "risky",
            "out_of_scope": "out_of_scope",
            "need_more_info": "need_more_info",
        },
    )
    # 추천이 아닌 분기는 응답만 세팅하고 즉시 종료
    builder.add_edge("nutrition_query", END)
    builder.add_edge("risky", END)
    builder.add_edge("out_of_scope", END)
    builder.add_edge("need_more_info", END)
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
    classifier: Callable[[str], IntentType] = classify_intent_stub,
) -> AgentState:
    """공개 진입점. 요청 분류(intent) → 분기 → (추천이면) 파이프라인. 반환형은 기존과 동일."""
    initial_state = AgentState(user_message=user_message, profile=profile or UserProfile())
    graph = create_graph(extractor, classifier)
    result = graph.invoke(initial_state.__dict__.copy())
    return AgentState.model_validate(result)
