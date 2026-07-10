"""
app/agents/meal_agent.py
실제 식단 추천 에이전트의 공개 진입점.
"""

from app.agents.graph import run_agent as run_agent
from app.schemas import AgentState


def build_final_response(state: AgentState) -> str:
    mp = state.meal_plan
    nt = state.nutrition_total
    vr = state.validation_result

    lines = [f"[{mp.meal_type}] 추천 식단"]
    for food in mp.items:
        lines.append(f"  · {food.food_name} ({food.kcal:.0f}kcal, 나트륨 {food.sodium:.0f}mg)")
    lines.append(
        f"\n총 {nt.total_kcal:.0f}kcal · 나트륨 {nt.total_sodium:.0f}mg "
        f"· 탄{nt.total_carbohydrate:.0f}/단{nt.total_protein:.0f}/지{nt.total_fat:.0f}g"
    )
    lines.append(f"\n{mp.reason}")
    if vr.warnings:
        lines.append("주의: " + " ".join(vr.warnings))
    return "\n".join(lines)
