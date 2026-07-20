import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate
from app.models.user import User
from app.core.security import get_password_hash, verify_password


class UserService:
    def __init__(self, db: Session):
        self.repository = UserRepository(db)

    def create_user(self, schema_in: UserCreate) -> User:
        # Check if email is unique
        existing_user = self.repository.get_by_email(schema_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )
        
        hashed_password = get_password_hash(schema_in.password)
        db_obj = User(
            full_name=schema_in.full_name,
            email=schema_in.email,
            hashed_password=hashed_password,
            role=schema_in.role,
            is_active=schema_in.is_active,
        )
        return self.repository.create(db_obj)

    def get_user(self, user_id: uuid.UUID) -> User | None:
        return self.repository.get(user_id)

    def get_by_email(self, email: str) -> User | None:
        return self.repository.get_by_email(email)

    def authenticate_user(self, email: str, password: str) -> User | None:
        user = self.get_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
