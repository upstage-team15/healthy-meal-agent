"""
app/services/nutrition_lookup.py
영양 조회(nutrition_query) 처리. "김치찌개 나트륨 얼마야?" 같은 요청에 답한다.

"판단은 LLM, 사실은 코드":
  - 어떤 음식을 묻는지 이름 추출은 단순 매칭(필요 시 LLM 확장 가능).
  - 실제 영양 수치는 반드시 DB(CSV)의 값을 그대로 쓴다. LLM이 숫자를 지어내지 않는다.
"""

from app.schemas import FoodItem
from app.services.food_retriever import load_foods


def _find_food(user_message: str, foods: list[FoodItem]) -> FoodItem | None:
    """문장에 음식명이 포함돼 있으면 가장 길게(구체적으로) 매칭되는 음식을 찾는다."""
    text = user_message.replace(" ", "")
    matches = [f for f in foods if f.food_name.replace(" ", "") in text]
    if not matches:
        return None
    # 이름이 가장 긴 것 = 가장 구체적인 매칭 (예: "된장찌개"가 "된장"보다 우선)
    return max(matches, key=lambda f: len(f.food_name))


def answer_nutrition_query(user_message: str, foods: list[FoodItem] | None = None) -> str:
    """영양 조회 응답 문자열을 만든다. 수치는 전부 DB 실제값."""
    if foods is None:
        foods = load_foods()

    food = _find_food(user_message, foods)
    if food is None:
        return (
            "어떤 음식의 영양 정보를 알려드릴까요? "
            "저희 DB에 있는 음식명을 정확히 말씀해 주시면 실제 성분값으로 답해드려요."
        )

    return (
        f"[{food.food_name}] 1인분({food.serving_size:.0f}g) 기준\n"
        f"  · 칼로리 {food.kcal:.0f}kcal\n"
        f"  · 탄수화물 {food.carbohydrate:.0f}g / 단백질 {food.protein:.0f}g / 지방 {food.fat:.0f}g\n"
        f"  · 당류 {food.sugar:.0f}g / 나트륨 {food.sodium:.0f}mg\n"
        f"(식약처 통합식품영양성분 DB 기준)"
    )
