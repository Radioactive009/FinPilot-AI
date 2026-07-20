import uuid
from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate
from app.models.user import User


class UserService:
    def __init__(self, db: Session):
        self.repository = UserRepository(db)

    def create_user(self, schema_in: UserCreate) -> User:
        db_obj = User(
            full_name=schema_in.full_name,
            email=schema_in.email,
            hashed_password=schema_in.password,  # Placeholder for hashing service
            role=schema_in.role,
            is_active=schema_in.is_active,
        )
        return self.repository.create(db_obj)

    def get_user(self, user_id: uuid.UUID) -> User | None:
        return self.repository.get(user_id)

    def get_by_email(self, email: str) -> User | None:
        return self.repository.get_by_email(email)
