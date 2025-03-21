from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import Form
from pydantic import BaseModel, EmailStr


class ChangePasswordForm(BaseModel):
    current_password: Annotated[str, Form(...)]
    new_password: Annotated[str, Form(...)]


class Session(BaseModel):
    user_id: UUID | str
    device_type: bool
    device_type: str
    created_at: datetime


class ProfileResponse(BaseModel):
    email: EmailStr
    created_at: datetime
