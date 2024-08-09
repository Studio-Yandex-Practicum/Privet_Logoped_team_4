from pydantic import BaseModel
from typing import Optional


class UserCreate(BaseModel):
    user_id: int
    role: str
    is_admin: Optional[int] = 0


class UserGet(BaseModel):
    user_id: int
    role: Optional[str]
    is_admin: Optional[int] = 0


class AdminRequest(BaseModel):
    user_id: int
    is_admin: int = 1


class LinkCreate(BaseModel):
    link: str
    link_name: str
    link_type: str
    to_role: Optional[str] = None


class PromocodeCreate(BaseModel):
    promocode: str
    file_path: str


class PromocodeGetFilepath(BaseModel):
    promocode: str
    file_path: Optional[str]
