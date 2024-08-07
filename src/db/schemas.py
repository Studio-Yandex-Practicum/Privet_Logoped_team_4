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


class LinkCreate(BaseModel):
    link_id: Optional[int]
    link: str
    link_name: str
    link_type: str
    to_role: Optional[str] = None


class PromocodeCreate(BaseModel):
    promocode_id: Optional[int]
    promocode: str
    file_path: str


class PromocodeGetFilepath(BaseModel):
    promocode_id: Optional[int]
    promocode: str
    file_path: Optional[str]
