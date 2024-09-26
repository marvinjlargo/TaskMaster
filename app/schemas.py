# app/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class TodoBase(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False
    due_date: Optional[datetime] = None
    category: Optional[str] = None

class TodoCreate(TodoBase):
    pass

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    due_date: Optional[datetime] = None
    category: Optional[str] = None

class Todo(TodoBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool = True
    todos: List[Todo] = []

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None