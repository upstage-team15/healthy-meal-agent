"""
app/services/condition_extractor.py
자연어 입력 → UserConditions 변환. 오늘은 LLM 없이 stub(고정 규칙).
나중에 이 함수 내부만 Solar Pro 호출로 바꾸면 됨. 반환 형태는 동일 유지.
"""

from app.schemas import UserConditions


def extract_conditions_stub(user_message: str) -> UserConditions:
    """
    오늘의 핵심 시나리오 입력을 규칙으로 파싱.
    "400kcal 이하로, 계란은 빼고 야채 많은 한 끼 추천해줘"
    """
    import re

    target_kcal = None
    kcal_mode = None
    # "400kcal", "400 kcal" 등에서 숫자 추출
    m = re.search(r"(\d+)\s*kcal", user_message)
    if m:
        target_kcal = float(m.group(1))
        # "이하/안으로/미만" → upper, 그 외 → target
        kcal_mode = "upper" if re.search(r"이하|안으로|미만|넘지", user_message) else "target"

    preferences = []
    for pref in ["야채 많은", "담백한", "얼큰한", "든든한"]:
        key = pref.replace(" 많은", "").replace("한", "")  # 느슨한 매칭
        if key in user_message or pref in user_message:
            preferences.append(pref)
    # "야채" 단독으로도 잡기
    if "야채" in user_message and "야채 많은" not in preferences:
        preferences.append("야채 많은")

    exclude_foods = []
    m2 = re.search(r"(\S+?)(?:은|는|을|를)?\s*빼", user_message)
    if m2:
        exclude_foods.append(m2.group(1).replace("은", "").replace("는", ""))

    meal_style = None
    if "한 끼" in user_message or "한그릇" in user_message:
        meal_style = "한그릇"
    elif "백반" in user_message or "차려" in user_message:
        meal_style = "백반"

    return UserConditions(
        target_kcal=target_kcal,
        kcal_mode=kcal_mode,
        preferences=preferences,
        exclude_foods=exclude_foods,
        meal_style=meal_style,
    )
