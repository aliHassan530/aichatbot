from fastapi import APIRouter, HTTPException, Header, status


router = APIRouter()


@router.get("/profile")
def profile():
    return {"message": "yellow"}