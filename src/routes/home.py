from fastapi import APIRouter, HTTPException, Header, status


router = APIRouter()


@router.get("/yellow")
def yellow():
    return {"message": "yellow"}