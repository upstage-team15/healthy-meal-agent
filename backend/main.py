"""
backend/main.py
FastAPI 앱 생성 + 라우터 등록만 담당한다(정문).
실제 로직은 routers/ 와 app/ 에 있다.
"""

from fastapi import FastAPI

from backend.routers import chat, health

app = FastAPI(title="Healthy Meal Agent API")

app.include_router(health.router)
app.include_router(chat.router)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Healthy Meal Agent API is initialized."}
