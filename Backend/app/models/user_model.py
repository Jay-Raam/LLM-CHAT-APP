from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserInDB(BaseModel):
    id: Optional[str]
    email: EmailStr
    hashed_password: str
    created_at: datetime
