from typing import Optional
from uuid import UUID

from pydantic import BaseModel, conint


class User(BaseModel):
    id: UUID
    display_name: str
    banned: bool = False
    group: bool = False
    contact_info: dict = {}
    user_settings: dict = {}
    tokens_quota: conint(ge=0) = 80000
    tokens_used: Optional[conint(ge=0)] = 0


class Shape(BaseModel):
    id: UUID
    name: str
    enabled: bool
    description: str
    other_info: dict = {}


class ShapeUpdate(BaseModel):
    name: str
    enabled: bool
    description: str
    other_info: dict = {}


class Message(BaseModel):
    shape_id: UUID
    user_id: UUID
    sender_id: Optional[UUID] = None
    message: str
    extras: Optional[dict] = None
    user_blocks: list


class Reply(BaseModel):
    shape_id: UUID
    user_id: UUID
    sender_id: Optional[UUID] = None
    shape_blocks: list
    reply: str


class WackOutput(BaseModel):
    user_id: UUID
    shape_id: UUID
    ts: int


class Error(BaseModel):
    code: int
    message: str
