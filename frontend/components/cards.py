"""HTML builders for the rich chat cards.

backend의 실제 ``ChatResponse``(backend/schemas.py) 데이터를 받아 렌더링한다.
가짜 고정값은 쓰지 않는다 — 여기 없는 정보(예: 사용자가 말한 목표kcal 원문)는
API 응답에 없으므로 표시하지 않거나 근사치임을 명시한다.
"""

# app/services/validator.py의 나트륨 PASS 기준선(767mg 이하)과 동일하게 맞춘다.
SODIUM_PASS_MAX = 767

STATUS_LABEL = {"PASS": "PASS ✓", "PASS_WITH_WARNING": "주의 ⚠", "FAIL": "FAIL ✕"}
STATUS_COLOR = {
    "PASS": "var(--pass)",
    "PASS_WITH_WARNING": "var(--warning)",
    "FAIL": "var(--danger)",
}


def _macro_rows(carb: float, protein: float, fat: float) -> str:
    """실제 탄단지 그램 수치로 에너지 비율(%)을 계산한다 (validator.py와 동일한 방식)."""
    kcal_from_macro = carb * 4 + protein * 4 + fat * 9
    if kcal_from_macro <= 0:
        return ""

    macros = [
        {"label": "탄수화물", "pct": round(carb * 4 / kcal_from_macro * 100), "color": "#5A7A5A"},
        {"label": "단백질", "pct": round(protein * 4 / kcal_from_macro * 100), "color": "#E8874A"},
        {"label": "지방", "pct": round(fat * 9 / kcal_from_macro * 100), "color": "#A8B898"},
    ]
    return "".join(
        f"""
        <div>
          <div class="macro-row-top">
            <span class="macro-name">{m["label"]}</span>
            <span class="macro-pct">{m["pct"]}%</span>
          </div>
          <div class="macro-bar-track">
            <div class="macro-bar-fill" style="width:{m["pct"]}%; background:{m["color"]};"></div>
          </div>
        </div>
        """
        for m in macros
    )


def meal_card_html(response: dict, target_kcal: int) -> str:
    """meal_recommend 응답(품목 1개 이상)을 카드로 렌더링."""
    items = response.get("items") or []
    nutrition = response.get("nutrition") or {}
    meal_type = response.get("meal_type") or "추천 식단"
    reason = response.get("reason") or ""
    status = response.get("status") or "PASS"
    warnings = response.get("warnings") or []

    total_kcal = nutrition.get("total_kcal", 0)
    total_sodium = nutrition.get("total_sodium", 0)
    total_carb = nutrition.get("total_carbohydrate", 0)
    total_protein = nutrition.get("total_protein", 0)
    total_fat = nutrition.get("total_fat", 0)

    # 사이드바가 이미 "하루 KDRI 필요량 ÷ 3"으로 계산해 넘기는 끼니당 추정 목표.
    single_target = target_kcal or 0
    kcal_pct = min(round(total_kcal / single_target * 100), 100) if single_target else 0
    sodium_pct = min(round(total_sodium / SODIUM_PASS_MAX * 100), 100)

    item_rows = "".join(
        f"""
        <div class="meal-item-row">
          <span class="meal-item-role">{it.get("meal_role", "")}</span>
          <span class="meal-item-name">{it.get("food_name", "")}</span>
          <span class="meal-item-kcal">{it.get("kcal", 0):.0f}kcal</span>
        </div>
        """
        for it in items
    )

    tag_chips = f'<span class="tag-pill" style="color:{STATUS_COLOR.get(status, "var(--sage)")}; background:var(--sage-pale);">{meal_type}</span>'
    tag_chips += "".join(
        f'<span class="tag-pill" style="color:#8B5E3C; background:var(--amber-pale);">⚠ {w}</span>'
        for w in warnings
    )

    reason_section = (
        f"""
        <div class="info-section">
          <div class="info-title"><span>💡</span> 추천 이유</div>
          <div class="info-body">{reason}</div>
        </div>
        """
        if reason
        else ""
    )

    return f"""
    <div class="na-card">
      <div class="na-card-header">
        <span style="font-size:20px;">🍱</span>
        <div>
          <div class="na-card-title">{meal_type}</div>
          <div class="na-card-subtitle">{len(items)}개 품목 추천</div>
        </div>
        <span class="pass-badge" style="color:{STATUS_COLOR.get(status, "var(--pass)")};">{STATUS_LABEL.get(status, status)}</span>
      </div>
      <div class="na-card-body">
        <div class="meal-item-list">{item_rows}</div>

        <div class="nutri-grid">
          <div class="nutri-cell">
            <div class="nutri-cell-label">칼로리</div>
            <div class="nutri-cell-value">{total_kcal:.0f}<span>kcal</span></div>
            <div class="nutri-cell-sub">끼니당 추정 목표 {single_target}kcal</div>
            <div class="nutri-bar-track"><div class="nutri-bar-fill" style="width:{kcal_pct}%; background:var(--sage);"></div></div>
          </div>
          <div class="nutri-cell">
            <div class="nutri-cell-label">나트륨</div>
            <div class="nutri-cell-value">{total_sodium:.0f}<span>mg</span></div>
            <div class="nutri-cell-sub">기준 {SODIUM_PASS_MAX}mg 이하</div>
            <div class="nutri-bar-track"><div class="nutri-bar-fill" style="width:{sodium_pct}%; background:var(--amber);"></div></div>
          </div>
          <div class="macro-box">
            <div class="macro-box-title">다량영양소 (실측)</div>
            {_macro_rows(total_carb, total_protein, total_fat)}
            <div class="macro-box-foot">KDRI 2025 검증은 서버에서 수행</div>
          </div>
        </div>

        <div class="tag-row">{tag_chips}</div>

        <div class="na-divider"></div>
        {reason_section}

        <div class="disclaimer-box">
          ⚠️ 본 서비스는 의료 진단이나 처방을 대신하지 않습니다. 특정 질환이 있는 경우 반드시 전문의 또는 영양사와 상담하시기 바랍니다.
        </div>
      </div>
    </div>
    """


def danger_alert_card_html(body: str) -> str:
    """intent == 'risky' 응답용. body는 실제 final_response 텍스트."""
    options = ["저칼로리 균형 식단 추천받기", "간헐적 단식 가이드 보기", "주치의 상담 안내"]
    chips = "".join(f'<span class="suggestion-chip">{o}</span>' for o in options)
    return f"""
    <div class="na-card alert-card-danger">
      <div class="alert-card-header-danger">
        <span style="font-size:18px;">🚨</span>
        <div>
          <div class="alert-title-danger">입력 차단 — 안전하지 않은 요청</div>
          <div class="alert-body-danger">{body}</div>
        </div>
      </div>
      <div style="padding:12px 16px;">
        <div class="suggestion-lead" style="margin:0 0 10px;">대신 이런 건강한 대안은 어떨까요?</div>
        <div class="suggestion-row" style="padding:0;">{chips}</div>
      </div>
    </div>
    """


def clarification_card_html(body: str) -> str:
    """intent == 'need_more_info' 응답용. body는 실제 final_response 텍스트."""
    options = [
        ("🎯", "목표 칼로리 설정"),
        ("🥘", "먹고 싶은 음식 지정"),
        ("🌿", "선호 식단 스타일 선택"),
    ]
    chips = "".join(
        f'<span class="suggestion-chip suggestion-chip-sage">{icon} {label}</span>'
        for icon, label in options
    )
    return f"""
    <div class="na-card">
      <div class="suggestion-header">
        <div class="suggestion-header-title">조금 더 알려주시면 정확하게 추천할 수 있어요 😊</div>
        <div class="suggestion-header-sub">{body}</div>
      </div>
      <div class="suggestion-row">{chips}</div>
    </div>
    """


def sodium_warning_card_html(warning_text: str) -> str:
    """meal_recommend 응답의 warnings 중 나트륨 관련 문구가 있을 때 meal card 아래 추가로 붙인다."""
    options = ["저염 버전으로 변경", "국물 제외 옵션", "나트륨 낮은 유사 메뉴"]
    chips = "".join(
        f'<span class="suggestion-chip suggestion-chip-amber">{o}</span>' for o in options
    )
    return f"""
    <div class="na-card alert-card-sodium">
      <div class="alert-card-header-sodium">
        <span style="font-size:18px;">⚠️</span>
        <div>
          <div class="alert-title-sodium">나트륨 주의</div>
          <div class="alert-body-sodium">{warning_text}</div>
        </div>
      </div>
      <div style="padding:12px 16px;">
        <div class="suggestion-lead" style="margin:0 0 10px;">대안 제안</div>
        <div class="suggestion-row" style="padding:0;">{chips}</div>
      </div>
    </div>
    """
