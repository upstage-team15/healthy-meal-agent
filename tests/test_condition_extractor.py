"""
tests/test_condition_extractor.py
조건 추출 폴백(stub)의 정규화 로직 테스트.
실제 LLM 없이 결정적으로 검증한다(CI-safe). LLM 경로는 프롬프트로 동일 규칙을 지시한다.
"""

from app.services.condition_extractor import extract_conditions_stub


# ── 나트륨 관련 다양한 표현 → 표준 태그 "저염"으로 정규화 ────────────────
def test_stub_normalizes_sodium_expressions_to_low_sodium():
    for msg in ["저염으로", "나트륨 낮게", "싱겁게 먹고싶어", "덜 짜게", "짜지 않은 반찬"]:
        cond = extract_conditions_stub(msg)
        assert "저염" in cond.nutrition_goals, f"실패: {msg} → {cond.nutrition_goals}"


def test_stub_normalizes_protein_expressions():
    cond = extract_conditions_stub("고단백 위주로")
    assert "고단백" in cond.nutrition_goals


def test_stub_no_nutrition_goal_when_absent():
    # 맛 조건만 있으면 nutrition_goals는 비어 있어야 한다(오탐 방지)
    cond = extract_conditions_stub("칼칼한 거 추천해줘")
    assert cond.nutrition_goals == []


def test_stub_still_extracts_kcal():
    # 기존 기능(칼로리 추출)이 회귀하지 않았는지
    cond = extract_conditions_stub("400kcal 이하로 저염 담백하게")
    assert cond.target_kcal == 400
    assert cond.kcal_mode == "upper"
    assert "저염" in cond.nutrition_goals
