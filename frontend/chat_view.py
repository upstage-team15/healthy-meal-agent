from __future__ import annotations

import html
import json
import re
from typing import Any

import streamlit as st

from constants import EXAMPLE_PROMPTS


def render_app_header(service_name: str, message_count: int = 0) -> None:
    count_label = f"{message_count} messages" if message_count else "ready"
    st.html(
        f"""
        <div class="app-header">
            <div class="brand-row">
                <div class="brand-mark" aria-hidden="true">H</div>
                <div>
                    <div class="service-name">{html.escape(service_name)}</div>
                    <div class="service-caption">건강한 한 끼를 빠르게 정리합니다</div>
                </div>
            </div>
            <div class="header-meta">
                <span class="status-dot" aria-hidden="true"></span>
                <span>{html.escape(count_label)}</span>
            </div>
        </div>
        """,
    )


def render_empty_state() -> None:
    st.html(
        """
        <section class="empty-state">
            <div class="empty-kicker">AI meal planner</div>
            <h1>오늘 한 끼를 어떻게 맞출까요?</h1>
            <p>칼로리, 제외할 재료, 선호하는 맛을 말하면 바로 식단과 영양 정보를 정리해드릴게요.</p>
        </section>
        """,
    )


def render_suggestion_buttons() -> str | None:
    return st.pills(
        "추천 질문",
        EXAMPLE_PROMPTS,
        selection_mode="single",
        key="example_prompt_choice",
        label_visibility="collapsed",
        width="stretch",
    )


def render_message(message: dict) -> None:
    role = message.get("role", "assistant")
    role_label = "나" if role == "user" else "Healthy Meal Agent"
    created_at = message.get("created_at", "")
    content = message.get("content", "")
    attachments = message.get("attachments", [])
    message_id = re.sub(r"[^A-Za-z0-9_]", "_", f"copy_{message.get('id', '')}")

    attachment_html = ""
    if attachments:
        chips = "".join(
            f'<span class="attachment-chip">{html.escape(name)}</span>' for name in attachments
        )
        attachment_html = f'<div class="attachment-list">{chips}</div>'

    st.html(
        f"""
        <div class="message-row {html.escape(role)}">
            <div class="message-stack">
                <div class="message-meta">
                    <span>{html.escape(role_label)}</span>
                    <span class="message-actions">
                        <span>{html.escape(created_at)}</span>
                        <button id="{message_id}" class="copy-btn" type="button">복사</button>
                    </span>
                </div>
                <div class="message-bubble">
                    {_markdownish_to_html(content)}
                    {attachment_html}
                </div>
            </div>
        </div>
        <script>
        (() => {{
          const btn = document.getElementById({json.dumps(message_id)});
          if (!btn) return;
          btn.addEventListener('click', async () => {{
            await navigator.clipboard.writeText({json.dumps(content)});
            btn.textContent = '복사됨';
            setTimeout(() => {{ btn.textContent = '복사'; }}, 1000);
          }});
        }})();
        </script>
        """,
        unsafe_allow_javascript=True,
    )

    if role == "assistant":
        render_meal_card(message.get("agent"))


def render_typing_indicator() -> None:
    st.html(
        """
        <div class="typing-row" aria-live="polite" aria-label="답변 생성 중">
            <div class="typing-bubble">
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
            </div>
        </div>
        """,
    )


def render_meal_card(agent_payload: dict | None) -> None:
    if not agent_payload:
        return

    meal_plan = agent_payload.get("meal_plan")
    nutrition = agent_payload.get("nutrition_total")
    validation = agent_payload.get("validation_result") or {}
    if not meal_plan or not nutrition:
        return

    items = meal_plan.get("items", [])
    warnings = validation.get("warnings", [])
    status = validation.get("status", "PASS")
    status_class = (
        "warning" if status == "PASS_WITH_WARNING" else "fail" if status == "FAIL" else ""
    )
    status_label = {
        "PASS": "적합",
        "PASS_WITH_WARNING": "주의",
        "FAIL": "조정 필요",
    }.get(status, "분석")

    food_rows = "".join(
        f"""
        <div class="food-row">
            <span>{html.escape(item.get("food_name", "음식"))}</span>
            <span>{_num(item.get("kcal"))}kcal · 나트륨 {_num(item.get("sodium"))}mg</span>
        </div>
        """
        for item in items
    )
    warning_html = ""
    if warnings:
        warning_html = (
            '<div class="warning-list">'
            + "<br>".join(html.escape(warning) for warning in warnings)
            + "</div>"
        )

    st.html(
        f"""
        <div class="meal-card">
            <div class="meal-card-title">
                <strong>{html.escape(meal_plan.get("meal_type", "추천 식단"))} 추천 식단</strong>
                <span class="status-pill {status_class}">{html.escape(status_label)}</span>
            </div>
            <div class="nutrition-grid">
                {_nutrition_item("총 열량", _num(nutrition.get("total_kcal")), "kcal")}
                {_nutrition_item("탄수화물", _num(nutrition.get("total_carbohydrate")), "g")}
                {_nutrition_item("단백질", _num(nutrition.get("total_protein")), "g")}
                {_nutrition_item("나트륨", _num(nutrition.get("total_sodium")), "mg")}
            </div>
            <div class="food-list">{food_rows}</div>
            {warning_html}
        </div>
        """,
    )


def _nutrition_item(label: str, value: str, unit: str) -> str:
    return f"""
    <div class="nutrition-item">
        <div class="nutrition-label">{html.escape(label)}</div>
        <div class="nutrition-value">{html.escape(value)}{html.escape(unit)}</div>
    </div>
    """


def _num(value: Any) -> str:
    try:
        return f"{float(value):.0f}"
    except (TypeError, ValueError):
        return "0"


def _markdownish_to_html(text: str) -> str:
    if not text:
        return ""

    parts = re.split(r"```", text)
    rendered: list[str] = []
    for index, part in enumerate(parts):
        if index % 2 == 0:
            rendered.append(_text_to_html(part))
        else:
            rendered.append(_code_to_html(part))
    return "".join(rendered)


def _text_to_html(text: str) -> str:
    escaped = html.escape(text.strip("\n"))
    return escaped.replace("\n", "<br>")


def _code_to_html(block: str) -> str:
    lines = block.strip("\n").splitlines()
    if lines and re.fullmatch(r"[A-Za-z0-9_+.#-]{1,24}", lines[0].strip()):
        code = "\n".join(lines[1:])
    else:
        code = "\n".join(lines)
    return f"<pre><code>{html.escape(code)}</code></pre>"
