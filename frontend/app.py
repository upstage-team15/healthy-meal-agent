"""NutriAgent AI 영양사 — Streamlit version.

healthy-meal-agent FastAPI 백엔드(SSE /api/v1/chat)와 연동된 채팅 UI.
Run with:  streamlit run frontend/app.py
먼저 백엔드를 실행해야 한다:  uvicorn backend.main:app --reload --port 8000
"""

import streamlit as st

from styles import CUSTOM_CSS
from api_client import stream_chat
from chat_state import (
    get_active_conversation,
    init_conversations,
    select_conversation,
    touch_conversation,
    update_conversation_title,
)
from components.sidebar import render_sidebar
from components.cards import (
    meal_card_html,
    danger_alert_card_html,
    clarification_card_html,
    sodium_warning_card_html,
)

st.set_page_config(page_title="NutriAgent AI 영양사", page_icon="🥗", layout="wide")
st.html(CUSTOM_CSS)

QUICK_REPLIES = [
    "400kcal 안으로 야채 많은 점심 추천해줘",
    "500kcal 이하 도시락 메뉴 알려줘",
    "저염 저녁 메뉴 추천해줘",
    "김치찌개 나트륨 얼마야?",
]


def init_state() -> None:
    defaults = {"gender": "female", "age_group": "19-29", "allergens": [], "target_kcal": 0}
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)
    init_conversations()


init_state()
render_sidebar()

# ---------- Top bar ----------
top_left, top_right = st.columns([3, 1])
with top_left:
    st.html(
        """
        <div class="topbar-brand">
          <span class="status-dot"></span>
          <span class="topbar-title">NutriAgent AI 영양사</span>
          <span class="badge badge-sage">KDRI 2025</span>
        </div>
        """
    )
with top_right:
    active_tab = st.radio(
        "보기",
        ["💬 채팅", "📋 히스토리"],
        horizontal=True,
        label_visibility="collapsed",
        key="active_tab",
    )

st.divider()


def render_response_body(response: dict) -> None:
    """ChatResponse(dict)를 intent에 맞는 카드/텍스트로 렌더링. chat_message 컨테이너 안에서 호출."""
    intent = response.get("intent")
    final_response = response.get("final_response", "")

    if intent == "risky":
        st.html(danger_alert_card_html(final_response))
    elif intent == "need_more_info":
        st.html(clarification_card_html(final_response))
    elif intent in ("nutrition_query", "out_of_scope"):
        st.markdown(final_response)
    else:  # meal_recommend (또는 intent 없이 온 과거형 응답 대비 기본값)
        if response.get("items"):
            st.html(meal_card_html(response, st.session_state.target_kcal))
            sodium_warning = next((w for w in response.get("warnings", []) if "나트륨" in w), None)
            if sodium_warning:
                st.html(sodium_warning_card_html(sodium_warning))
        else:
            st.markdown(final_response)


def render_message(msg: dict) -> None:
    role = msg["role"]
    avatar = "🥗" if role == "assistant" else None
    with st.chat_message(role, avatar=avatar):
        if role == "assistant":
            st.html('<div class="agent-label">🥗 NutriAgent AI 영양사</div>')

        mtype = msg["type"]
        if mtype == "text":
            st.markdown(msg["content"])
        elif mtype == "response":
            render_response_body(msg["content"])
        elif mtype == "error":
            st.error(msg["content"])


def build_profile_payload() -> dict:
    allergens = st.session_state.allergens
    return {
        "gender": st.session_state.gender,
        "age_group": st.session_state.age_group,
        "allergies": [] if allergens == ["없음"] else allergens,
    }


def process_message(text: str) -> None:
    conversation = get_active_conversation()
    update_conversation_title(conversation, text)
    conversation["messages"].append({"role": "user", "type": "text", "content": text})

    with st.chat_message("assistant", avatar="🥗"):
        st.html('<div class="agent-label">🥗 NutriAgent AI 영양사</div>')

        status_box = st.status("요청을 분석하고 있어요...", expanded=False)
        final_payload = None
        error_message = None

        for event, data in stream_chat(text, build_profile_payload()):
            if event == "status":
                status_box.update(label=data.get("message", ""))
            elif event == "result":
                final_payload = data
            elif event == "error":
                error_message = data.get("message", "알 수 없는 오류가 발생했어요.")

        if error_message:
            status_box.update(label="오류 발생", state="error")
            st.error(error_message)
            conversation["messages"].append(
                {"role": "assistant", "type": "error", "content": error_message}
            )
        elif final_payload is not None:
            status_box.update(label="완료 ✓", state="complete")
            render_response_body(final_payload)
            conversation["messages"].append(
                {"role": "assistant", "type": "response", "content": final_payload}
            )

    touch_conversation(conversation)
    st.rerun()


def _switch_conversation(conversation_id: str) -> None:
    # st.session_state["active_tab"]는 위젯이 이미 인스턴스화된 뒤엔 직접 못 바꾸므로,
    # 위젯 재실행 전에 도는 on_click 콜백 안에서 설정한다.
    select_conversation(conversation_id)
    st.session_state["active_tab"] = "💬 채팅"


def render_history_tab() -> None:
    conversations = st.session_state.conversations
    query = st.text_input(
        "대화 검색", key="history_search", placeholder="대화 검색", label_visibility="collapsed"
    ).strip()
    filtered = [c for c in conversations if query.lower() in c["title"].lower()]

    if not filtered:
        st.info("검색 결과가 없습니다.")
        return

    for conversation in filtered:
        user_turns = sum(1 for m in conversation["messages"] if m["role"] == "user")
        is_active = conversation["id"] == st.session_state.active_conversation_id
        cols = st.columns([5, 1])
        with cols[0]:
            label = ("🟢 " if is_active else "") + conversation["title"]
            st.button(
                label,
                key=f"history_{conversation['id']}",
                use_container_width=True,
                on_click=_switch_conversation,
                args=(conversation["id"],),
            )
        with cols[1]:
            st.caption(f"{user_turns}건")


# ---------- Main body ----------
if active_tab == "📋 히스토리":
    render_history_tab()
else:
    active_conversation = get_active_conversation()
    for message in active_conversation["messages"]:
        render_message(message)

# ---------- Quick replies ----------
qr_cols = st.columns(len(QUICK_REPLIES))
for col, quick_reply in zip(qr_cols, QUICK_REPLIES):
    with col:
        if st.button(quick_reply, key=f"quick_{quick_reply}", use_container_width=True):
            process_message(quick_reply)

# ---------- Chat input ----------
prompt = st.chat_input(
    "원하시는 식사를 말씀해 주세요... (예: 400kcal 안으로 야채 많은 점심 추천해줘)"
)
if prompt:
    process_message(prompt)

st.caption("NutriAgent는 의료 진단을 대신하지 않습니다 · 2025 KDRI 기준 적용 중")
