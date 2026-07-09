import csv
from pathlib import Path

from app.schemas import FoodItem

DEFAULT_FOOD_DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "foods_clean.csv"


def load_foods(data_path: Path = DEFAULT_FOOD_DATA_PATH) -> list[FoodItem]:
    with data_path.open(encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        return [FoodItem.model_validate(row) for row in reader]


def retrieve_foods(
    query: str = "",
    target_kcal: float | None = None,
    limit: int = 10,
    data_path: Path = DEFAULT_FOOD_DATA_PATH,
) -> list[FoodItem]:
    foods = load_foods(data_path)
    normalized_query = query.strip().lower()

    if normalized_query:
        foods = [
            food
            for food in foods
            if normalized_query in food.food_name.lower()
            or normalized_query in food.meal_role.lower()
        ]

    if target_kcal is not None:
        foods = [food for food in foods if food.kcal <= target_kcal]

    return foods[:limit]
