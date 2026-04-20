from fastapi import APIRouter, HTTPException, Header, status


router = APIRouter()


@router.get("/deleteAccount")
def deleteAccount():
    return {"message": "Detete Account endpoint"}