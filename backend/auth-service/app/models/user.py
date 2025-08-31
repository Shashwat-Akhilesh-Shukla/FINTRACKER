# app/models/user.py
from sqlalchemy import Boolean, Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    avatar = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Profile information
    phone = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    
    # Account verification
    email_verified = Column(Boolean, default=False)
    verification_token = Column(String, nullable=True)
    
    # Password reset
    reset_token = Column(String, nullable=True)
    reset_token_expires = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
