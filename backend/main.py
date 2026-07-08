from fastapi import FastAPI

app = FastAPI(title="Healthy Meal Agent API")


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Healthy Meal Agent API is initialized."}


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
