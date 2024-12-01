from fastapi import APIRouter, Depends, HTTPException
from db.models import UserCreate
from services.auth import AuthService
from api.dependencies import get_user_service, create_access_token

router = APIRouter()


@router.post("/signup/")
async def sign_up(user: UserCreate, user_service: AuthService = Depends(get_user_service)):
    try:
        response = await user_service.create_user(user.username, user.password)
        authenticated_user = await user_service.authenticate_user(user.username, user.password)
        access_token = create_access_token(data={"user_id": authenticated_user.id})
        return {"message": response["message"], "user_id": authenticated_user.id, "access_token": access_token}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login/")
async def log_in(user: UserCreate, user_service: AuthService = Depends(get_user_service)):
    try:
        authenticated_user = await user_service.authenticate_user(user.username, user.password)
        access_token = create_access_token(data={"user_id": authenticated_user.id})
        return {"message": "Login successful", "user_id": authenticated_user.id, "access_token": access_token}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
