"""Sidebar: 건강 프로필(성별/연령/알레르기).

Ports ``src/components/Sidebar.tsx``.
"""

import streamlit as st

from chat_state import conversation_has_started, create_new_chat, get_active_conversation

ALLERGEN_TAGS = ["대두", "밀가루", "우유", "땅콩", "계란", "새우", "복숭아"]

# 하루 에너지필요추정량(kcal/일). 출처: 프로젝트/에너지 및 다량영양소 섭취기준.csv
# ("65+" 구간은 원본의 65-74세 값을 사용 — 75세이상은 별도 구간을 두지 않음)
DAILY_KCAL_MAP = {
    "male": {"15-18": 2700, "19-29": 2600, "30-49": 2500, "50-64": 2200, "65+": 2000},
    "female": {"15-18": 2000, "19-29": 2000, "30-49": 1900, "50-64": 1700, "65+": 1600},
}

AGE_GROUPS = ["15-18", "19-29", "30-49", "50-64", "65+"]


def _start_new_chat() -> None:
    # st.session_state["active_tab"]는 위젯이 이미 인스턴스화된 뒤엔 직접 못 바꾸므로,
    # 위젯 재실행 전에 도는 on_click 콜백 안에서 설정한다.
    create_new_chat()
    st.session_state["active_tab"] = "💬 채팅"


def render_sidebar() -> None:
    reset_token = st.session_state.get("profile_reset_token", 0)

    with st.sidebar:
        st.html(
            """
            <div class="brand-row">
              <div class="brand-icon">🥗</div>
              <div>
                <div class="brand-title">NutriAgent</div>
                <div class="brand-sub">AI 영양사 v2.5</div>
              </div>
            </div>
            """
        )

        st.html('<div class="section-label">나의 건강 프로필</div>')

        profile_locked = conversation_has_started(get_active_conversation())
        if profile_locked:
            st.html(
                '<div class="validator-note">'
                "🔒 이미 시작된 대화에서는 프로필을 수정할 수 없어요. "
                "'+ 새 대화'를 누르면 다시 설정할 수 있습니다."
                "</div>"
            )

        st.html('<div class="field-label">성별</div>')
        gender_label = st.radio(
            "성별",
            ["남성", "여성"],
            horizontal=True,
            label_visibility="collapsed",
            index=0 if st.session_state.gender == "male" else 1,
            key=f"gender_radio_{reset_token}",
            disabled=profile_locked,
        )
        st.session_state.gender = "male" if gender_label == "남성" else "female"

        st.html('<div class="field-label">연령대</div>')
        age_group = st.selectbox(
            "연령대",
            AGE_GROUPS,
            index=AGE_GROUPS.index(st.session_state.age_group),
            label_visibility="collapsed",
            format_func=lambda a: f"{a}세",
            key=f"age_group_select_{reset_token}",
            disabled=profile_locked,
        )
        st.session_state.age_group = age_group

        daily_kcal = DAILY_KCAL_MAP[st.session_state.gender].get(age_group, 2000)
        meal_kcal = round(daily_kcal / 3)
        # 세션에는 "한 끼" 목표를 저장한다 (하루 필요량 자체가 아님) —
        # components/cards.py의 meal_card_html이 이 값을 그대로 끼니 목표로 사용한다.
        st.session_state.target_kcal = meal_kcal

        gender_kr = "여성" if st.session_state.gender == "female" else "남성"
        st.html(
            f"""
            <div class="kdri-box">
              <div class="kdri-label">2025 KDRI 한 끼 목표 열량</div>
              <div class="kdri-value">{meal_kcal:,} <span>kcal/끼</span></div>
              <div class="kdri-sub">{gender_kr} {age_group}세 · 하루 {daily_kcal:,}kcal ÷ 3</div>
            </div>
            """
        )

        st.divider()
        st.html('<div class="section-label">알레르기 · 식이 제한</div>')
        st.html(
            """
            <div class="validator-note">
              🛡️ <strong>Validator</strong>가 식품의약품안전처 DB를 기반으로 설정된 알레르기를 실시간 검증합니다.
            </div>
            """
        )

        no_allergy = st.checkbox(
            "해당 없음",
            value=st.session_state.allergens == ["없음"],
            key=f"no_allergy_checkbox_{reset_token}",
            disabled=profile_locked,
        )
        selected = st.multiselect(
            "알레르기 성분 선택",
            options=ALLERGEN_TAGS,
            default=[a for a in st.session_state.allergens if a in ALLERGEN_TAGS],
            label_visibility="collapsed",
            placeholder="해당하는 알레르기 성분을 선택하세요",
            key=f"allergen_multiselect_{reset_token}",
            disabled=no_allergy or profile_locked,
        )
        st.session_state.allergens = ["없음"] if no_allergy else selected

        st.divider()
        st.button("＋ 새 대화", use_container_width=True, on_click=_start_new_chat)
