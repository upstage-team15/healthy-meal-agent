from app.schemas import UserProfile
from app.agents.mock_agent import run_agent


def test_end_to_end_scenario():
    """핵심 시나리오가 최종 응답까지 도달하는지"""
    msg = "400kcal 이하로, 계란은 빼고 야채 많은 한 끼 추천해줘"
    state = run_agent(msg, UserProfile(allergies=[]))

    # 조건이 추출됐는지
    assert state.conditions.target_kcal == 400
    assert state.conditions.kcal_mode == "upper"

    # 최종 응답이 생성됐는지
    assert state.final_response != ""

    # 검증 결과가 있고, FAIL로 끝나지 않았는지 (PASS 계열)
    assert state.validation_result is not None
    print("\n" + state.final_response)  # -s 옵션으로 보임
