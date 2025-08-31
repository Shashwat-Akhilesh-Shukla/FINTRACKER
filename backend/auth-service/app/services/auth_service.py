# app/services/auth_service.py
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timedelta

from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.core.security import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    create_refresh_token,
    verify_token
)
from app.core.exceptions import (
    AuthenticationError, 
    UserAlreadyExistsError, 
    UserNotFoundError,
    InvalidTokenError
)
from app.core.config import settings

class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def login(self, login_data: LoginRequest) -> TokenResponse:
        user = self.authenticate_user(login_data.email, login_data.password)
        if not user:
            raise AuthenticationError("Incorrect email or password")
        
        if not user.is_active:
            raise AuthenticationError("Account is deactivated")

        # Update last login
        user.last_login = datetime.utcnow()
        self.db.commit()

        # Create tokens
        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

    def register(self, register_data: RegisterRequest) -> TokenResponse:
        # Check if user exists
        existing_user = self.db.query(User).filter(
            User.email == register_data.email
        ).first()
        
        if existing_user:
            raise UserAlreadyExistsError("Email already registered")

        # Create new user
        hashed_password = get_password_hash(register_data.password)
        db_user = User(
            email=register_data.email,
            hashed_password=hashed_password,
            first_name=register_data.first_name,
            last_name=register_data.last_name,
        )

        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)

        # Create tokens
        access_token = create_access_token(subject=db_user.id)
        refresh_token = create_refresh_token(subject=db_user.id)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

    def refresh_token(self, refresh_token: str) -> TokenResponse:
        user_id = verify_token(refresh_token, token_type="refresh")
        if not user_id:
            raise InvalidTokenError("Invalid refresh token")

        user = self.db.query(User).filter(User.id == int(user_id)).first()
        if not user or not user.is_active:
            raise UserNotFoundError("User not found or inactive")

        # Create new tokens
        access_token = create_access_token(subject=user.id)
        new_refresh_token = create_refresh_token(subject=user.id)

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

    def get_current_user(self, token: str) -> User:
        user_id = verify_token(token, token_type="access")
        if not user_id:
            raise InvalidTokenError("Invalid access token")

        user = self.db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            raise UserNotFoundError("User not found")
        
        if not user.is_active:
            raise AuthenticationError("Account is deactivated")

        return user
