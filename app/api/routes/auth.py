from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.user import Token, User, UserCreate
from app.core.dependencies import get_auth_service
from app.db.base import get_db
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/signup", response_model=User, status_code=status.HTTP_201_CREATED)
async def signup(
    user_in: UserCreate,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Create new user.
    """
    user = await auth_service.register_new_user(user_in=user_in)
    return user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    token = await auth_service.login(email=form_data.username, password=form_data.password)
    return {"access_token": token, "token_type": "bearer"}