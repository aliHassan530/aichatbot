# from fastapi import FastAPI

# app = FastAPI()

# @app.get("/")
# def root():
#     return {"message": "NGO API is running"}
from fastapi import FastAPI


from src.routers.auth import router as auth_router

app = FastAPI(
    title="Examination System API",
    description="API for user signup, login, and examination system",
    version="0.1.0"
)

# Include routers
app.include_router(auth_router, prefix="/", tags=["auth"])

# Optional: root endpoint for testing
@app.get("/")
def read_root():
    return {"message": "Examination System API is running"}