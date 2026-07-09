from app.schemas import UserConditions, UserProfile
from app.services.food_retriever import retrieve_foods, load_foods


def test_load_foods():
    """CSV 로딩되고 음식이 있는지"""
    foods = load_foods()
    assert len(foods) > 0


def test_retrieve_returns_candidates():
    """조건 검색 시 후보가 나오는지"""
    cond = UserConditions(target_kcal=400, kcal_mode="upper", preferences=["야채 많은"])
    result = retrieve_foods(cond, UserProfile())
    total = sum(len(v) for v in result.values())
    assert total > 0


def test_allergy_excluded():
    """알레르기 음식이 후보에서 빠지는지"""
    cond = UserConditions(target_kcal=400, kcal_mode="upper")
    prof = UserProfile(allergies=["계란"])
    result = retrieve_foods(cond, prof)
    for foods in result.values():
        for f in foods:
            assert "계란" not in f.food_name
