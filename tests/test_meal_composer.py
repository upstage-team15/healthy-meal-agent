"""
tests/test_meal_composer.py
조합기(생성-검증 루프) 테스트. 외부 의존 없이 CSV 후보로 결정론적으로 검증한다.
핵심: 조합 합계가 목표 칼로리 예산을 지키는지(예전 '740kcal 백반' 버그 회귀 방지).
"""

from app.schemas import UserConditions, UserProfile
from app.services.food_retriever import load_foods, retrieve_foods
from app.services.meal_composer import compose_meal
from app.services.nutrition_calculator import calculate_nutrition
from app.services.validator import macro_deviation, validate_meal


def _compose(conditions, seed=0):
    cand = retrieve_foods(conditions, UserProfile(), foods=load_foods())
    return compose_meal(cand, conditions, seed=seed)


def test_bansang_respects_upper_kcal_budget():
    """백반 조합 합계가 upper 목표를 넘지 않는지 (740kcal 초과 버그 회귀 방지)"""
    cond = UserConditions(target_kcal=400, kcal_mode="upper", meal_style="백반")
    mp = _compose(cond)
    total = calculate_nutrition(mp).total_kcal
    assert total <= 400, f"백반 합계 {total}kcal가 목표 400 초과"
    assert len(mp.items) >= 1


def test_onebowl_respects_upper_kcal_budget():
    """한그릇 조합도 upper 목표 예산을 지키는지"""
    cond = UserConditions(target_kcal=500, kcal_mode="upper", meal_style="한그릇")
    mp = _compose(cond)
    total = calculate_nutrition(mp).total_kcal
    assert total <= 500


def test_composed_meal_passes_validator():
    """조합 결과가 우리 건강 기준 검증(validator)을 통과하는지 (kcal 축)"""
    cond = UserConditions(target_kcal=400, kcal_mode="upper", meal_style="백반")
    mp = _compose(cond)
    nut = calculate_nutrition(mp)
    result = validate_meal(mp, nut, cond, UserProfile())
    # 칼로리 초과/부실로 인한 FAIL은 없어야 한다
    assert result.status in ("PASS", "PASS_WITH_WARNING"), result.failures


def test_target_mode_stays_within_range():
    """target 모드(정도)는 ±10% 범위 안에서 조합되는지"""
    cond = UserConditions(target_kcal=600, kcal_mode="target", meal_style="백반")
    mp = _compose(cond)
    total = calculate_nutrition(mp).total_kcal
    assert 600 * 0.9 <= total <= 600 * 1.1, f"{total}kcal가 600±10% 밖"


def test_prefers_balanced_macro_combo():
    """조합기가 탄단지 균형이 더 나은 쪽을 고르는지 (밥 단독보다 밥+반찬 선호)"""
    cond = UserConditions(target_kcal=500, kcal_mode="upper", meal_style="백반")
    mp = _compose(cond)
    dev = macro_deviation(calculate_nutrition(mp))
    # 밥만 담으면 탄수 100%로 이탈량이 큼. 조합기가 균형 맞춰 이탈량을 억제해야 함.
    assert dev < 60, f"탄단지 이탈량 {dev}가 과도(균형 조합 실패)"


def test_low_sodium_combo_keeps_sodium_low():
    """저염 요청 시 조합 합계 나트륨도 낮게 유지되는지 (검색 필터 + 조합 채점)"""
    cond = UserConditions(target_kcal=400, kcal_mode="upper", nutrition_goals=["저염"])
    mp = _compose(cond)
    na = calculate_nutrition(mp).total_sodium
    assert na <= 1000, f"저염 요청인데 조합 나트륨 {na}mg"
