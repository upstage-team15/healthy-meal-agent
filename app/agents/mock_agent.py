"""
app/agents/mock_agent.py
전체 흐름 연결 (지휘자). LangGraph 없이 순차 호출 + 재시도 루프.
나중에 이 흐름을 그대로 LangGraph 노드로 감싸면 됨.
"""

from app.schemas import AgentState, UserProfile
from app.services.condition_extractor import extract_conditions_stub
from app.services.food_retriever import retrieve_foods
from app.services.meal_composer import compose_meal
from app.services.nutrition_calculator import calculate_nutrition
from app.services.validator import validate_meal

MAX_RETRY = 2


def run_agent(user_message: str, profile: UserProfile = None) -> AgentState:
    state = AgentState(user_message=user_message, profile=profile or UserProfile())

    # ① 조건 추출
    state.conditions = extract_conditions_stub(user_message)

    # ② 후보 검색
    candidates = retrieve_foods(state.conditions, state.profile)
    state.candidates = [f for lst in candidates.values() for f in lst]

    # 후보 충분한지 체크
    if not any(candidates.values()):
        state.final_response = "조건에 맞는 음식을 찾지 못했습니다. 조건을 완화해 주세요."
        return state

    # ③~⑤ 조합 → 계산 → 검증, 실패 시 재시도
    for attempt in range(MAX_RETRY + 1):
        state.retry_count = attempt

        # ③ 조합 (재시도마다 seed 바꿔 다른 조합)
        state.meal_plan = compose_meal(candidates, state.conditions, seed=attempt)

        # ④ 계산
        state.nutrition_total = calculate_nutrition(state.meal_plan)

        # ⑤ 검증
        state.validation_result = validate_meal(
            state.meal_plan, state.nutrition_total, state.conditions, state.profile
        )

        vr = state.validation_result

        # 통과 or 주의 → 종료
        if vr.status in ("PASS", "PASS_WITH_WARNING"):
            state.final_response = build_final_response(state)
            return state

        # FAIL & 재시도 여지 → cause 보고 분기
        if attempt < MAX_RETRY:
            if vr.cause == "retrieve":
                candidates = retrieve_foods(state.conditions, state.profile, relax=True)
            # cause=="compose"면 seed만 바꿔 재조합 (다음 루프)
            continue

    # 재시도 다 써도 실패 → fallback
    state.final_response = (
        "조건을 모두 만족하는 식단을 찾지 못했어요. 칼로리나 제외 조건을 조금 완화해 주시겠어요?"
    )
    return state


def build_final_response(state: AgentState) -> str:
    mp = state.meal_plan
    nt = state.nutrition_total
    vr = state.validation_result

    lines = [f"[{mp.meal_type}] 추천 식단"]
    for f in mp.items:
        lines.append(f"  · {f.food_name} ({f.kcal:.0f}kcal, 나트륨 {f.sodium:.0f}mg)")
    lines.append(
        f"\n총 {nt.total_kcal:.0f}kcal · 나트륨 {nt.total_sodium:.0f}mg "
        f"· 탄{nt.total_carbohydrate:.0f}/단{nt.total_protein:.0f}/지{nt.total_fat:.0f}g"
    )
    lines.append(f"\n{mp.reason}")
    if vr.warnings:
        lines.append("주의: " + " ".join(vr.warnings))
    return "\n".join(lines)
