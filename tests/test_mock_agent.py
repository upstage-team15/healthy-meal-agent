from pathlib import Path

from app.agents.mock_agent import run_mock_agent
from app.schemas import MealRequest


def test_run_mock_agent_returns_valid_basic_plan(tmp_path: Path) -> None:
    data_path = tmp_path / "foods.csv"
    data_path.write_text(
        "\n".join(
            [
                "food_id,food_name,meal_role,serving_g,kcal,carbohydrate,protein,fat,sugar,sodium",
                "1,brown rice,rice,200,300,66,6,2,1,5",
                "2,green salad,side,120,90,10,4,3,4,180",
            ]
        ),
        encoding="utf-8",
    )

    result = run_mock_agent(MealRequest(query="salad", target_kcal=500), data_path=data_path)

    assert result.validation.is_valid is True
    assert result.meal_plan.foods[0].food_name == "green salad"
    assert result.meal_plan.total_nutrition.kcal == 90
