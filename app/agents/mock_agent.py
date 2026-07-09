from pathlib import Path

from app.schemas import MealPlan, MealRequest, MockAgentResult
from app.services.food_retriever import DEFAULT_FOOD_DATA_PATH, retrieve_foods
from app.services.meal_composer import compose_meal
from app.services.nutrition_calculator import calculate_total_nutrition
from app.services.validator import validate_meal


def run_mock_agent(
    request: MealRequest,
    data_path: Path = DEFAULT_FOOD_DATA_PATH,
) -> MockAgentResult:
    candidates = retrieve_foods(
        query=request.query,
        target_kcal=request.target_kcal,
        limit=request.limit,
        data_path=data_path,
    )
    selected_foods = compose_meal(candidates, target_kcal=request.target_kcal)
    total_nutrition = calculate_total_nutrition(selected_foods)
    meal_plan = MealPlan(
        foods=selected_foods,
        total_nutrition=total_nutrition,
        notes=["This is a mock pipeline result. LLM and RAG logic are not implemented yet."],
    )
    validation = validate_meal(meal_plan, target_kcal=request.target_kcal)

    return MockAgentResult(
        request=request,
        candidates=candidates,
        meal_plan=meal_plan,
        validation=validation,
    )
