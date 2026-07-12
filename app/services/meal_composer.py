"""
app/services/meal_composer.py
후보 안에서만 식단 조합. 오늘은 규칙 기반(LLM 아님).
- 한그릇: 한그릇 음식 1개 (+ 목표 대비 부족하면 반찬 1개 곁들임)
- 백반: 밥1 + 국물0~1 + 반찬1~2
재시도 시 이전 실패를 피하도록 다른 조합 선택.

한그릇 곁들임 배경(2026-07-12): 삼삼한 밥상 데이터는 저염 건강식이라 일품(한그릇)이
대부분 300~400kcal로 가볍다. 단독이면 validator의 "목표 75% 미만=부실 FAIL"에 자주 걸린다.
→ 한그릇이 목표에 못 미치면 반찬을 예산 안에서 1개 곁들여 한 끼 분량·영양 균형을 맞춘다.
(validator 기준은 그대로. composer가 조합으로 해결.)
"""

import random
from app.schemas import MealPlan, FoodItem, UserConditions

MAIN_MIN_RATIO = (
    0.75  # 목표 칼로리의 이 비율 미만이면 한그릇에 반찬을 곁들인다 (validator 하한과 동일)
)


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
            main = rng.choice(pool)
            items.append(main)
            # 한그릇이 목표에 못 미치면 반찬 1개를 예산 안에서 곁들인다.
            _add_side_if_light(items, main, candidates, conditions, rng)
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


def _add_side_if_light(
    items: list[FoodItem],
    main: FoodItem,
    candidates: dict,
    conditions: UserConditions,
    rng: random.Random,
) -> None:
    """한그릇이 목표 대비 가벼우면 반찬 1개를 곁들인다(제자리 수정).

    - 목표 칼로리가 없으면(자유 추천) 곁들이지 않는다 — 단독으로 충분.
    - 한그릇 kcal이 목표의 MAIN_MIN_RATIO 이상이면 이미 충분 → 그대로.
    - 곁들일 반찬은 '목표를 넘기지 않는' 것 중에서 고른다(upper 모드 초과 방지).
    """
    target = conditions.target_kcal
    if not target:
        return
    if main.kcal >= target * MAIN_MIN_RATIO:
        return

    remaining = target - main.kcal
    sides = [s for s in candidates.get("반찬", []) if s.kcal <= remaining]
    if not sides:
        return
    # 남은 예산을 잘 채우는 순으로 상위 후보 중 하나(재시도 시 seed로 흔들림)
    sides.sort(key=lambda s: s.kcal, reverse=True)
    top = sides[: min(5, len(sides))]
    items.append(rng.choice(top))
