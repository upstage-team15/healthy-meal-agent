from app.agents.meal_agent import run_agent
from app.schemas import UserProfile
from app.services import food_retriever
from app.services.food_retriever import load_foods, retrieve_foods


def test_end_to_end_scenario(monkeypatch):
    """핵심 시나리오가 최종 응답까지 도달하는지.

    retrieve는 CSV 경로로 고정해 외부(Supabase/Upstage) 의존 없이 결정론적으로 돈다.
    """

    # retrieve_foods를 항상 CSV 후보로 돌게 고정 (Supabase 호출 차단)
    def csv_retrieve(conditions, profile, foods=None, relax=False):
        return retrieve_foods(conditions, profile, foods=load_foods(), relax=relax)

    monkeypatch.setattr(food_retriever, "retrieve_foods", csv_retrieve)
    # graph 모듈이 import한 참조도 교체
    monkeypatch.setattr("app.agents.graph.retrieve_foods", csv_retrieve)

    msg = "400kcal 이하로, 계란은 빼고 야채 많은 한 끼 추천해줘"
    state = run_agent(msg, UserProfile(allergies=[]))

    # 조건이 추출됐는지
    assert state.conditions.target_kcal == 400
    assert state.conditions.kcal_mode == "upper"

    # 최종 응답이 생성됐는지
    assert state.final_response != ""

    # 검증 결과가 있는지
    assert state.validation_result is not None
    print("\n" + state.final_response)  # -s 옵션으로 보임
