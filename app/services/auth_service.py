from datetime import timedelta
from typing import Optional
from app.api.schemas.user import User, UserCreate
from app.core.config import settings
from app.core.exceptions import IncorrectCredentialsException, UserAlreadyExistsException
from app.core.security import create_access_token, get_password_hash, verify_password
from app.db.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def authenticate(self, email: str, password: str) -> Optional[User]:
        user = await self.user_repository.get_by_email(email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def create_access_token(self, user_id: str) -> str:
        return create_access_token(
            subject=user_id,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )

    async def register_new_user(self, user_in: UserCreate) -> User:
        # Check if user exists
        existing_user = await self.user_repository.get_by_email(email=user_in.email)
        if existing_user:
            raise UserAlreadyExistsException()
        
        # Create new user
        user_data = user_in.model_dump(exclude={"password"})
        user_data["hashed_password"] = get_password_hash(user_in.password)
        user = await self.user_repository.create(obj_in=UserCreate(**user_data))
        return user

    async def login(self, email: str, password: str) -> str:
        user = await self.authenticate(email=email, password=password)
        if not user:
            raise IncorrectCredentialsException()
        
        return await self.create_access_token(str(user.id))