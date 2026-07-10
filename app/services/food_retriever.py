"""
app/services/food_retriever.py
음식 후보 검색. CSV 로딩 + 조건 필터 + 알레르기/제외 제거.
"""

from pathlib import Path
import pandas as pd
from app.schemas import FoodItem

CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "foods_clean.csv"

PREFERENCE_KEYWORDS = {
    "야채 많은": ["나물", "무침", "채소", "샐러드", "숙주", "시금치", "콩나물", "비빔", "쌈"],
    "담백한": ["찜", "구이", "삶", "죽"],
    "얼큰한": ["김치", "찌개", "탕", "매운", "육개장"],
    "든든한": ["밥", "덮밥", "국밥"],
}

_FOODS_CACHE = None


def load_foods() -> list[FoodItem]:
    """CSV → FoodItem 리스트 (한 번 읽고 캐시)."""
    global _FOODS_CACHE
    if _FOODS_CACHE is not None:
        return _FOODS_CACHE

    df = pd.read_csv(CSV_PATH)
    if "food_id" not in df.columns:  # 수정사항 3
        df["food_id"] = df.index + 1

    foods = []
    for _, row in df.iterrows():
        foods.append(
            FoodItem(
                food_id=int(row["food_id"]),
                food_name=str(row["food_name"]),
                meal_role=str(row["meal_role"]),
                serving_size=float(row["serving_size"]),
                kcal=float(row["kcal"]),
                carbohydrate=float(row["carbohydrate"]),
                protein=float(row["protein"]),
                fat=float(row["fat"]),
                sugar=float(row["sugar"]),
                sodium=float(row["sodium"]),
            )
        )
    _FOODS_CACHE = foods
    return foods


def _is_excluded(food: FoodItem, excluded: list[str]) -> bool:
    return any(x and x in food.food_name for x in excluded)


def _matches_preference(food: FoodItem, preferences: list[str]) -> bool:
    if not preferences:
        return True
    for pref in preferences:
        keywords = PREFERENCE_KEYWORDS.get(pref, [pref])
        if any(kw in food.food_name for kw in keywords):
            return True
    return False


def retrieve_foods(conditions, profile, foods=None, relax=False) -> dict:
    """역할별 후보 반환: {"밥":[], "국물":[], "반찬":[], "한그릇":[]}"""
    if foods is None:
        foods = load_foods()

    excluded = list(profile.allergies) + list(conditions.exclude_foods)  # 수정사항 1

    kcal_ceiling = conditions.target_kcal if (conditions.target_kcal and not relax) else None

    result = {"밥": [], "국물": [], "반찬": [], "한그릇": []}
    for food in foods:
        if food.meal_role == "기타":  # 수정사항 2
            continue
        if _is_excluded(food, excluded):
            continue
        if kcal_ceiling and food.kcal > kcal_ceiling:
            continue
        if not relax and not _matches_preference(food, conditions.preferences):
            if food.meal_role in ("반찬", "한그릇"):
                continue
        result[food.meal_role].append(food)
    return result
