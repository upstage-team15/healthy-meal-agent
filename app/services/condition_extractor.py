"""
app/services/condition_extractor.py
자연어 입력 → UserConditions 변환.
Solar로 조건 JSON 추출, 실패 시 stub 폴백.
"""

import json

from dotenv import load_dotenv

from app.schemas import UserConditions

load_dotenv()

EXTRACT_PROMPT = """당신은 사용자의 식사 요청에서 조건을 추출하는 도구입니다.
아래 문장에서 조건을 추출해 JSON으로만 답하세요. 설명 없이 JSON만.

추출할 필드:
- target_kcal: 목표 칼로리 숫자 (없으면 null)
- kcal_mode: "upper"(이하/안으로/넘지않게) / "target"(정도/쯤) / null
- preferences: 맛·식감 선호 리스트 (예: ["담백한", "칼칼한", "야채 많은"], 없으면 [])
    · 맛/느낌을 나타내는 형용사만. 구체적 음식명은 여기가 아니라 wanted_foods에 넣는다.
- wanted_foods: 사용자가 콕 집어 넣어 달라는 '구체적 음식명' 리스트 (없으면 [])
    · 예: "김치찌개 넣어서", "비빔밥으로", "된장찌개랑 불고기" → 그 음식명들.
    · '칼칼한/담백한' 같은 맛 형용사는 여기 넣지 않는다(그건 preferences).
- nutrition_goals: 영양/건강 목표를 아래 표준 태그로 정규화해서 넣기 (없으면 [])
    · 나트륨 관련(저염/나트륨 낮게/싱겁게/덜 짜게/짜지 않게) → "저염"
    · 단백질 관련(고단백/단백질 많이/단백질 위주) → "고단백"
    · 운동/헬스/근육/PT/웨이트 맥락(예: "운동하는데", "헬스해서") → "고단백"
  주의: 이 표현들은 맛이 아니라 영양 목표이므로 preferences가 아니라 nutrition_goals에 넣는다.
- exclude_foods: 빼달라는 음식 (예: ["계란"], 없으면 [])
- meal_style: "한그릇" / "백반" / null

예시 입력: "400kcal 이하로 계란 빼고 야채 많은 한 끼 추천해줘"
예시 출력: {"target_kcal": 400, "kcal_mode": "upper", "preferences": ["야채 많은"], "wanted_foods": [], "nutrition_goals": [], "exclude_foods": ["계란"], "meal_style": "한그릇"}

예시 입력: "나트륨 낮게 담백한 점심 추천해줘"
예시 출력: {"target_kcal": null, "kcal_mode": null, "preferences": ["담백한"], "wanted_foods": [], "nutrition_goals": ["저염"], "exclude_foods": [], "meal_style": null}

예시 입력: "김치찌개 넣어서 식단 구성해줘"
예시 출력: {"target_kcal": null, "kcal_mode": null, "preferences": [], "wanted_foods": ["김치찌개"], "nutrition_goals": [], "exclude_foods": [], "meal_style": null}

사용자 문장: """


def extract_conditions_llm(user_message: str) -> UserConditions:
    """Solar로 조건 추출. 실패 시 stub 폴백."""
    try:
        from app.services.llm_client import complete

        # Solar(메인) 실패 시 OpenAI로 자동 Fallback (litellm Router). 둘 다 실패하면 stub.
        raw = complete(
            [{"role": "user", "content": EXTRACT_PROMPT + user_message}],
            temperature=0,
        ).strip()
        # 앞뒤에 텍스트 붙어도 { } 사이만 파싱
        data = json.loads(raw[raw.find("{") : raw.rfind("}") + 1])
        return _apply_context_rules(UserConditions(**data), user_message)
    except Exception as e:
        print(f"[조건추출 LLM 실패 → stub 폴백] {e}")
        return extract_conditions_stub(user_message)


# 운동·헬스 맥락 신호어 → "고단백" 목표로 연결 (결정론적 코드 안전망).
# LLM 프롬프트에도 같은 규칙을 넣되, LLM이 놓쳐도 코드가 보장한다(intent 가드레일과 동일 패턴).
_WORKOUT_HINTS = ("운동", "헬스", "근육", "근력", "단백질", "벌크", "pt", "웨이트", "헬창")


def _apply_context_rules(cond: UserConditions, user_message: str) -> UserConditions:
    """자연어 맥락을 표준 영양목표로 보정한다. 지금은 운동→고단백만."""
    text = user_message.lower()
    if any(h in text for h in _WORKOUT_HINTS) and "고단백" not in cond.nutrition_goals:
        cond.nutrition_goals.append("고단백")
    return cond


def extract_conditions_stub(user_message: str) -> UserConditions:
    """정규식 폴백 (LLM 실패 시)."""
    import re

    target_kcal = None
    kcal_mode = None
    m = re.search(r"(\d+)\s*kcal", user_message)
    if m:
        target_kcal = float(m.group(1))
        kcal_mode = "upper" if re.search(r"이하|안으로|미만|넘지", user_message) else "target"
    preferences = ["야채 많은"] if "야채" in user_message else []
    # 나트륨 관련 표현을 표준 태그 "저염"으로 정규화 (LLM 없을 때 폴백)
    nutrition_goals = []
    if any(k in user_message for k in ("저염", "나트륨", "싱겁", "덜 짜", "짜지 않", "안 짜")):
        nutrition_goals.append("저염")
    if any(k in user_message for k in ("고단백", "단백질")):
        nutrition_goals.append("고단백")
    exclude_foods = []
    m2 = re.search(r"(\S+?)\s*빼", user_message)
    if m2:
        exclude_foods.append(re.sub(r"[은는을를]$", "", m2.group(1)))
    meal_style = "한그릇" if "한 끼" in user_message else None
    cond = UserConditions(
        target_kcal=target_kcal,
        kcal_mode=kcal_mode,
        preferences=preferences,
        nutrition_goals=nutrition_goals,
        exclude_foods=exclude_foods,
        meal_style=meal_style,
    )
    return _apply_context_rules(cond, user_message)
