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

    # ── 4. 탄단지 비율 (주의만) ──
    total_g = nutrition.total_carbohydrate + nutrition.total_protein + nutrition.total_fat
    if total_g > 0:
        carb_pct = nutrition.total_carbohydrate / total_g * 100
        if carb_pct > 70:
            warnings.append("탄수화물 비중이 다소 높아요.")

    # ── 판정 ──
    if failures:
        status = "FAIL"
    elif warnings:
        status = "PASS_WITH_WARNING"
    else:
        status = "PASS"

    return ValidationResult(status=status, warnings=warnings, failures=failures, cause=cause)
