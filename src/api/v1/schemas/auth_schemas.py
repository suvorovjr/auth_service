from typing import Annotated

from fastapi import Form
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterForm(BaseModel):
    email: Annotated[EmailStr, Form(...)]
    password: Annotated[str, Form(...)]
    confirm_password: Annotated[str, Form(...)]


class UserResponse(BaseModel):
    email: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class LoginForm(BaseModel):
    email: Annotated[EmailStr, Form(...)]
    password: Annotated[str, Form(...)]


class LoginResponse(BaseModel):
    refresh_token: str
    access_token: str
    token_type: str = Field(default="jwt")
