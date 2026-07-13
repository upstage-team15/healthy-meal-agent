"""
app/services/validator.py
식단 검증. 칼로리·제외음식은 FAIL(엄격), 나트륨은 단계별 등급.
"""

from app.schemas import MealPlan, NutritionTotal, UserConditions, UserProfile, ValidationResult


def validate_meal(
    meal_plan: MealPlan, nutrition: NutritionTotal, conditions: UserConditions, profile: UserProfile
) -> ValidationResult:
    failures = []
    warnings = []
    cause = None

    # ── 1. 칼로리 (FAIL 엄격) ──
    if conditions.target_kcal:
        kcal = nutrition.total_kcal
        if conditions.kcal_mode == "upper":
            if kcal > conditions.target_kcal:
                failures.append(
                    f"목표 {conditions.target_kcal:.0f}kcal 이하인데 {kcal:.0f}kcal로 초과했습니다."
                )
                cause = "compose"
            elif kcal < conditions.target_kcal * 0.75:
                failures.append(f"{kcal:.0f}kcal로 너무 낮아 한 끼로 부실합니다.")
                cause = "compose"
        elif conditions.kcal_mode == "target":
            if not (conditions.target_kcal * 0.9 <= kcal <= conditions.target_kcal * 1.1):
                failures.append(
                    f"목표 {conditions.target_kcal:.0f}kcal ±10% 범위를 벗어났습니다({kcal:.0f}kcal)."
                )
                cause = "compose"

    # ── 2. 제외음식/알레르기 (FAIL 엄격) ──
    excluded = list(profile.allergies) + list(conditions.exclude_foods)
    for food in meal_plan.items:
        for x in excluded:
            if x and x in food.food_name:
                failures.append(f"제외 대상 '{x}'이(가) '{food.food_name}'에 포함됐습니다.")
                cause = "retrieve"  # 후보 검색이 잘못 걸러진 것 → 검색부터 다시

    # ── 3. 나트륨 (단계별 등급) ──
    na = nutrition.total_sodium
    if na <= 767:
        pass
    elif na <= 1000:
        warnings.append("나트륨이 기준보다 약간 높아요.")
    elif na <= 1300:
        warnings.append("나트륨이 다소 높습니다. 저염 대안을 고려해보세요.")
    elif na <= 1500:
        warnings.append("나트륨이 높습니다. 국물을 남기는 것을 권합니다.")
    else:  # 1500 초과 → FAIL
        failures.append(f"나트륨이 {na:.0f}mg으로 과다합니다.")
        cause = "compose"

    # ── 4. 탄단지 에너지비율 (주의만, FAIL 아님) ──
    # 문서 v4 §6: KDRI 에너지적정비율 ±5%p 완충. g이 아니라 "에너지(kcal) 비율"로 판정.
    #   탄수 g×4, 단백 g×4, 지방 g×9 → 각 비율. 이탈 개수 무관하게 warning.
    #   (탄단지는 하루 평균 개념이라 한 끼 엄격 FAIL은 정상식단 과다탈락 → 안전축은 kcal·나트륨·알레르기)
    macro_warnings = _macro_ratio_warnings(nutrition)
    warnings.extend(macro_warnings)

    # ── 판정 ──
    if failures:
        status = "FAIL"
    elif warnings:
        status = "PASS_WITH_WARNING"
    else:
        status = "PASS"

    return ValidationResult(status=status, warnings=warnings, failures=failures, cause=cause)


# ── 탄단지 에너지비율 (문서 v4 §6) ─────────────────────────────
# KDRI 적정비율 ±5%p 완충. 한 끼 검증 범위.
MACRO_RANGES = {
    "탄수화물": (45, 70),
    "단백질": (5, 25),
    "지방": (10, 35),
}


def macro_energy_ratios(nutrition: NutritionTotal) -> dict[str, float]:
    """탄단지를 에너지(kcal) 비율(%)로 환산. 탄4·단4·지9 kcal/g."""
    c_kcal = nutrition.total_carbohydrate * 4
    p_kcal = nutrition.total_protein * 4
    f_kcal = nutrition.total_fat * 9
    total = c_kcal + p_kcal + f_kcal
    if total <= 0:
        return {"탄수화물": 0.0, "단백질": 0.0, "지방": 0.0}
    return {
        "탄수화물": c_kcal / total * 100,
        "단백질": p_kcal / total * 100,
        "지방": f_kcal / total * 100,
    }


def macro_deviation(nutrition: NutritionTotal) -> float:
    """탄단지 3항목이 적정범위에서 벗어난 총량(%p). 0이면 완벽 균형.

    조합기(생성-검증 루프)가 '더 균형 잡힌 조합'을 고르는 점수로 재사용한다.
    """
    ratios = macro_energy_ratios(nutrition)
    dev = 0.0
    for name, (lo, hi) in MACRO_RANGES.items():
        v = ratios[name]
        if v < lo:
            dev += lo - v
        elif v > hi:
            dev += v - hi
    return dev


def _macro_ratio_warnings(nutrition: NutritionTotal) -> list[str]:
    """적정범위를 벗어난 탄단지 항목마다 경고 문구(FAIL 아님)."""
    ratios = macro_energy_ratios(nutrition)
    msgs: list[str] = []
    for name, (lo, hi) in MACRO_RANGES.items():
        v = ratios[name]
        if v > hi:
            msgs.append(f"{name} 비중이 다소 높아요({v:.0f}%).")
        elif v < lo:
            msgs.append(f"{name} 비중이 다소 낮아요({v:.0f}%).")
    return msgs
