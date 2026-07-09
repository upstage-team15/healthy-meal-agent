from app.schemas import FoodItem, NutritionSummary


def calculate_total_nutrition(foods: list[FoodItem]) -> NutritionSummary:
    return NutritionSummary(
        kcal=round(sum(food.kcal for food in foods), 1),
        carbohydrate=round(sum(food.carbohydrate for food in foods), 1),
        protein=round(sum(food.protein for food in foods), 1),
        fat=round(sum(food.fat for food in foods), 1),
        sugar=round(sum(food.sugar for food in foods), 1),
        sodium=round(sum(food.sodium for food in foods), 1),
    )
