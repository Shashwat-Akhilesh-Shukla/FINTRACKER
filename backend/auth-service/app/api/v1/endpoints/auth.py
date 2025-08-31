# app/api/v1/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.auth import (
    LoginRequest, 
    RegisterRequest, 
    TokenResponse,
    RefreshTokenRequest
)
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService
from app.api.deps import get_current_active_user
from app.models.user import User

router = APIRouter()

@router.post("/login", response_model=TokenResponse)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """Authenticate user and return JWT tokens"""
    auth_service = AuthService(db)
    return auth_service.login(login_data)

@router.post("/register", response_model=TokenResponse)
def register(
    register_data: RegisterRequest,
    db: Session = Depends(get_db)
):
    """Register new user and return JWT tokens"""
    auth_service = AuthService(db)
    return auth_service.register(register_data)

@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token"""
    auth_service = AuthService(db)
    return auth_service.refresh_token(refresh_data.refresh_token)

@router.post("/logout")
def logout(response: Response):
    """Logout user (client should discard tokens)"""
    # In a more sophisticated setup, you might want to blacklist tokens
    # For now, we just return success and let client handle token removal
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user profile"""
    return current_user

@router.get("/verify")
def verify_token(
    current_user: User = Depends(get_current_active_user)
):
    """Verify if token is valid"""
    return {
        "valid": True,
        "user_id": current_user.id,
        "email": current_user.email
    }
