from app.schemas import FoodItem


def compose_meal(
    candidates: list[FoodItem],
    target_kcal: float | None = None,
    max_items: int = 3,
) -> list[FoodItem]:
    selected: list[FoodItem] = []
    total_kcal = 0.0

    for food in candidates:
        if len(selected) >= max_items:
            break

        next_total = total_kcal + food.kcal
        if target_kcal is not None and selected and next_total > target_kcal:
            continue

        selected.append(food)
        total_kcal = next_total

    return selected
