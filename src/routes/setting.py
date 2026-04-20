from fastapi import APIRouter
router = APIRouter()

@router.get("/setting")
def setting():
    return {"message": "setting"}
