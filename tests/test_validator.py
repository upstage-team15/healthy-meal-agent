from app.schemas import FoodItem, MealPlan
from app.services.nutrition_calculator import calculate_total_nutrition
from app.services.validator import validate_meal


def test_validate_meal_rejects_calorie_overage() -> None:
    food = FoodItem(
        food_id=1,
        food_name="rice",
        meal_role="rice",
        serving_g=200,
        kcal=300,
        carbohydrate=66,
        protein=6,
        fat=2,
        sugar=1,
        sodium=5,
    )
    meal_plan = MealPlan(foods=[food], total_nutrition=calculate_total_nutrition([food]))

    result = validate_meal(meal_plan, target_kcal=250)

    assert result.is_valid is False
    assert "Total calories exceed the target." in result.reasons
