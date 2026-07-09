from app.schemas import MealPlan, ValidationResult

DEFAULT_MAX_SODIUM_MG = 2000.0


def validate_meal(
    meal_plan: MealPlan,
    target_kcal: float | None = None,
    max_sodium_mg: float = DEFAULT_MAX_SODIUM_MG,
) -> ValidationResult:
    reasons: list[str] = []

    if not meal_plan.foods:
        reasons.append("No foods were selected.")

    if target_kcal is not None and meal_plan.total_nutrition.kcal > target_kcal:
        reasons.append("Total calories exceed the target.")

    if meal_plan.total_nutrition.sodium > max_sodium_mg:
        reasons.append("Total sodium exceeds the recommended mock limit.")

    is_valid = not reasons
    if is_valid:
        reasons.append("Meal passed basic mock validation.")

    return ValidationResult(is_valid=is_valid, reasons=reasons)
