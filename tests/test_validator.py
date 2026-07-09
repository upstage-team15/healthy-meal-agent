from app.schemas import MealPlan, FoodItem, NutritionTotal, UserConditions, UserProfile
from app.services.validator import validate_meal


def _food(name="김밥", kcal=300, sodium=500):
    return FoodItem(
        food_id=1,
        food_name=name,
        meal_role="한그릇",
        serving_size=200,
        kcal=kcal,
        carbohydrate=40,
        protein=10,
        fat=8,
        sugar=3,
        sodium=sodium,
    )


def test_calorie_over_fails():
    """칼로리 초과 → FAIL"""
    mp = MealPlan(meal_type="한그릇", items=[_food(kcal=600)])
    nt = NutritionTotal(total_kcal=600, total_sodium=300)
    cond = UserConditions(target_kcal=400, kcal_mode="upper")
    vr = validate_meal(mp, nt, cond, UserProfile())
    assert vr.status == "FAIL"


def test_sodium_over_1500_fails():
    """나트륨 1500 초과 → FAIL"""
    mp = MealPlan(meal_type="한그릇", items=[_food(sodium=1600)])
    nt = NutritionTotal(total_kcal=350, total_sodium=1600)
    cond = UserConditions(target_kcal=400, kcal_mode="upper")
    vr = validate_meal(mp, nt, cond, UserProfile())
    assert vr.status == "FAIL"


def test_sodium_warning():
    """나트륨 900 → PASS_WITH_WARNING"""
    mp = MealPlan(meal_type="한그릇", items=[_food(sodium=900)])
    nt = NutritionTotal(total_kcal=350, total_sodium=900)
    cond = UserConditions(target_kcal=400, kcal_mode="upper")
    vr = validate_meal(mp, nt, cond, UserProfile())
    assert vr.status == "PASS_WITH_WARNING"


def test_allergy_included_fails():
    """알레르기 음식 포함 → FAIL"""
    mp = MealPlan(meal_type="한그릇", items=[_food(name="계란볶음밥")])
    nt = NutritionTotal(total_kcal=350, total_sodium=300)
    cond = UserConditions(target_kcal=400, kcal_mode="upper")
    prof = UserProfile(allergies=["계란"])
    vr = validate_meal(mp, nt, cond, prof)
    assert vr.status == "FAIL"
