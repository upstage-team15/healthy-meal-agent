"""
app/services/meal_composer.py
후보 안에서만 식단 조합. 규칙 기반(LLM 아님).

생성-검증 루프(2026-07-14 개선):
  이전에는 밥+국+반찬2를 무작정 담아 합계 칼로리를 안 봐서 "400 이하 요청에 740kcal 백반"
  같은 초과 조합이 나왔다. 이제는 여러 조합 후보를 생성한 뒤, 우리가 정의한 건강 기준
  (칼로리·나트륨·탄단지, docs/건강식_기준_재정의_v4)으로 채점해 가장 좋은 조합을 고른다.
  즉 검증 기준을 "채점"만이 아니라 "생성 기준"으로 끌어올렸다.

조합 형태:
  - 한그릇: 한그릇 1개 (+ 목표 미달 시 반찬 곁들임)
  - 백반: 밥1 + (국0~1) + (반찬0~2)  → 밥+α 조합을 여러 개 만들어 최적 선택
재시도(seed)마다 동점 조합 중 다른 것을 고른다.
"""

import random

from app.schemas import FoodItem, MealPlan, NutritionTotal, UserConditions
from app.services.validator import macro_deviation

MAIN_MIN_RATIO = 0.75  # 목표 칼로리의 이 비율 미만이면 한그릇/조합이 부실 (validator 하한과 동일)
SODIUM_SOFT_MAX = 1500  # 이 값 초과 조합은 validator에서 FAIL → 후보 채점에서 강한 감점
_CANDIDATE_POOL = 6  # 각 역할에서 조합 생성에 쓸 상위 후보 수(너무 많으면 조합 폭발)


def compose_meal(
    candidates: dict, conditions: UserConditions, meal_type: str = None, seed: int = None
) -> MealPlan:
    """
    candidates: retrieve_foods 결과 (역할별 dict)
    meal_type: "한그릇" or "백반" (None이면 자동 결정)
    seed: 재시도 시 다른 조합을 뽑기 위한 시드

    여러 조합 후보를 생성→건강 기준으로 채점→최적 조합을 MealPlan으로 반환.
    통과 조합이 하나도 없으면 그중 '가장 덜 나쁜' 조합을 반환한다(최종 판정은 validator가 함).
    """
    rng = random.Random(seed)

    if meal_type is None:
        if conditions.meal_style in ("백반", "한그릇"):
            meal_type = conditions.meal_style
        else:
            meal_type = "한그릇" if candidates.get("한그릇") else "백반"

    combos = _generate_combos(candidates, conditions, meal_type, rng)
    if not combos:
        # 후보가 아예 없으면 빈 식단(그래프가 후보없음으로 처리)
        return MealPlan(meal_type=meal_type, items=[], reason=_reason(meal_type, conditions))

    # 각 조합을 건강 기준으로 채점해 최적 선택 (낮을수록 좋음)
    best = min(combos, key=lambda items: _score(items, conditions))
    return MealPlan(meal_type=meal_type, items=best, reason=_reason(meal_type, conditions))


def _generate_combos(
    candidates: dict, conditions: UserConditions, meal_type: str, rng: random.Random
) -> list[list[FoodItem]]:
    """식사 형태에 맞는 여러 조합 후보(밥+α 등)를 생성한다."""
    combos: list[list[FoodItem]] = []

    if meal_type == "한그릇":
        pool = candidates.get("한그릇", [])[:_CANDIDATE_POOL]
        sides = candidates.get("반찬", [])[:_CANDIDATE_POOL]
        for main in pool:
            combos.append([main])  # 단독
            for side in sides:  # 곁들임 1개
                combos.append([main, side])
    else:  # 백반: 밥 + 국(0~1) + 반찬(0~2)
        rices = candidates.get("밥", [])[:_CANDIDATE_POOL]
        soups = candidates.get("국물", [])[:_CANDIDATE_POOL]
        sides = candidates.get("반찬", [])[:_CANDIDATE_POOL]
        # 밥이 없으면 국/반찬만으로도 조합(데이터 편차 방어)
        rice_opts = rices or [None]
        for rice in rice_opts:
            base = [rice] if rice else []
            soup_opts = [None] + soups
            for soup in soup_opts:
                cur = base + ([soup] if soup else [])
                # 반찬 0/1/2개
                combos.append(list(cur))
                for s1 in sides:
                    combos.append(cur + [s1])
                    for s2 in sides:
                        if s2 is not s1:
                            combos.append(cur + [s1, s2])

    # 빈 조합 제거 + 재시도 다양성을 위해 셔플(동점일 때 seed로 다른 선택)
    combos = [c for c in combos if c]
    rng.shuffle(combos)
    return combos


def _nutrition_of(items: list[FoodItem]) -> NutritionTotal:
    """조합의 영양 합산(경량). validator/calculator와 동일 로직."""
    t = NutritionTotal()
    for f in items:
        t.total_kcal += _safe(f.kcal)
        t.total_carbohydrate += _safe(f.carbohydrate)
        t.total_protein += _safe(f.protein)
        t.total_fat += _safe(f.fat)
        t.total_sodium += _safe(f.sodium)
    return t


def _score(items: list[FoodItem], conditions: UserConditions) -> float:
    """조합의 '나쁜 정도' 점수. 낮을수록 좋음.

    우선순위(가중치): 칼로리 위반 ≫ 나트륨 FAIL ≫ 탄단지 이탈.
    - 칼로리: upper 초과/부실, target ±10% 이탈을 강하게 벌점(FAIL 축).
    - 나트륨: 1500 초과(FAIL)는 강한 벌점, 그 아래는 약한 벌점.
    - 탄단지: 적정범위 이탈량(%p)을 약한 벌점(경고 축).
    """
    nut = _nutrition_of(items)
    penalty = 0.0
    target = conditions.target_kcal

    # 1) 칼로리 (안전축, 최우선)
    if target:
        kcal = nut.total_kcal
        if conditions.kcal_mode == "upper":
            if kcal > target:
                penalty += (kcal - target) * 100  # 초과는 절대 안 됨 → 매우 강한 벌점
            elif kcal < target * MAIN_MIN_RATIO:
                penalty += (target * MAIN_MIN_RATIO - kcal) * 20  # 부실도 벌점(덜 강함)
        elif conditions.kcal_mode == "target":
            lo, hi = target * 0.9, target * 1.1
            if kcal < lo:
                penalty += (lo - kcal) * 50
            elif kcal > hi:
                penalty += (kcal - hi) * 50

    # 2) 나트륨 (안전축)
    na = nut.total_sodium
    if na > SODIUM_SOFT_MAX:
        penalty += (na - SODIUM_SOFT_MAX) * 10  # FAIL 구간 → 강한 벌점
    elif na > 767:
        penalty += (na - 767) * 0.5  # 경고 구간 → 약한 벌점

    # 3) 탄단지 균형 (경고축, 약한 벌점) — 준우 요청: 밥+α로 비율 맞추기
    penalty += macro_deviation(nut) * 2

    # 4) 아주 약한 다양성 유도: 음식 수가 지나치게 적은 것보다 2~3개 조합 선호
    if len(items) == 1:
        penalty += 5

    return penalty


def _reason(meal_type: str, conditions: UserConditions) -> str:
    pref = ", ".join(conditions.preferences) or "기본"
    return f"{meal_type} 형태로, 조건({pref})에 맞춰 구성했습니다."


def _safe(x) -> float:
    try:
        if x is None or x != x:
            return 0.0
        return float(x)
    except (TypeError, ValueError):
        return 0.0
