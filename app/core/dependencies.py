from typing import Generator

from fastapi import Depends, HTTPException, status
# Import "fastapi" could not be resolved
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
# Import "jose" could not be resolved from sourcePylance
from sqlalchemy.ext.asyncio import AsyncSession
# Import "sqlalchemy.ext.asyncio" could not be resolvedPylancereportMissingImports

from app.core.config import settings
from app.db.base import get_db
from app.db.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(current_user = Depends(get_current_user)):
    return current_user


async def get_admin_user(current_user = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    user_repository = UserRepository(db)
    return AuthService(user_repository=user_repository)