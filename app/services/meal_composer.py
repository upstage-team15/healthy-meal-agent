"""
app/services/meal_composer.py
후보 안에서만 식단 조합. 오늘은 규칙 기반(LLM 아님).
- 한그릇: 한그릇 음식 1개
- 백반: 밥1 + 국물0~1 + 반찬1~2
재시도 시 이전 실패를 피하도록 다른 조합 선택.
"""

import random
from app.schemas import MealPlan, FoodItem, UserConditions


def compose_meal(
    candidates: dict, conditions: UserConditions, meal_type: str = None, seed: int = None
) -> MealPlan:
    """
    candidates: retrieve_foods 결과 (역할별 dict)
    meal_type: "한그릇" or "백반" (None이면 자동 결정)
    seed: 재시도 시 다른 조합을 뽑기 위한 시드
    """
    rng = random.Random(seed)

    # 식사 형태 결정
    if meal_type is None:
        if conditions.meal_style == "백반":
            meal_type = "백반"
        elif conditions.meal_style == "한그릇":
            meal_type = "한그릇"
        else:
            # 한그릇 후보가 있으면 한그릇 우선 (칼로리 맞추기 쉬움)
            meal_type = "한그릇" if candidates.get("한그릇") else "백반"

    items: list[FoodItem] = []

    if meal_type == "한그릇":
        pool = candidates.get("한그릇", [])
        if pool:
            items.append(rng.choice(pool))
    else:  # 백반
        if candidates.get("밥"):
            items.append(rng.choice(candidates["밥"]))
        if candidates.get("국물"):
            items.append(rng.choice(candidates["국물"]))
        sides = candidates.get("반찬", [])
        n_side = min(2, len(sides))
        if n_side:
            items.extend(rng.sample(sides, n_side))

    reason = f"{meal_type} 형태로, 조건({', '.join(conditions.preferences) or '기본'})에 맞춰 구성했습니다."
    return MealPlan(meal_type=meal_type, items=items, reason=reason)
