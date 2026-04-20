from fastapi import FastAPI
from .routes.auth import router as auth_router

app = FastAPI(title="Simple API")


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(auth_router, prefix="/auth", tags=["auth"])
