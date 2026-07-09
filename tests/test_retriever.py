from pathlib import Path

from app.services.food_retriever import retrieve_foods


def test_retrieve_foods_filters_by_query_and_calories(tmp_path: Path) -> None:
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

    foods = retrieve_foods(query="salad", target_kcal=120, data_path=data_path)

    assert len(foods) == 1
    assert foods[0].food_name == "green salad"
