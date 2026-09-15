from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime


class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password", min_length=4)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "johndoe@example.com",
                "password": "secret123"
            }
        }
    )



class UserCreate(BaseModel):
    first_name: str = Field(None, description="User's first name")
    last_name: str = Field(None, description="User's last name")
    email: str = Field(..., description="User's email address")
    password: str = Field(..., description="User's password", min_length=4)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "first_name": "John",
                "last_name": "Doe",
                "email": "johndoe@example.com",
                "password": "secret123"
            }
        }
    )
class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, description="User's first name")
    last_name: Optional[str] = Field(None, description="User's last name")
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "first_name": "John",
                "last_name": "Doe",
            }
        }
    )

class UserResponse(BaseModel):
    id: int = Field(..., description="User ID")
    email: str = Field(..., description="User's email address")
    first_name: Optional[str] = Field(None, description="User's first name")
    last_name: Optional[str] = Field(None, description="User's last name")
    is_active: bool = Field(..., description="Indicates if the user is active")
    is_superuser: bool = Field(..., description="Indicates if the user has superuser privileges")
    is_verified: bool = Field(..., description="Indicates if the user's email is verified")
    created_at: datetime = Field(..., description="Timestamp when the user was created")
    updated_at: datetime = Field(..., description="Timestamp when the user was last updated")

    model_config = ConfigDict(from_attributes = True)


class UserChangePassword(BaseModel):
    old_password: str = Field(..., description="Your old password", gt=4)
    new_password: str = Field(..., description="Your new password", gt=4)


class UserForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(..., description="User's email address")


class UserResetPasswordRequest(BaseModel):
    email: EmailStr = Field(..., description="User's email address")
    new_password: str = Field(..., description="User's new password", min_length=4)