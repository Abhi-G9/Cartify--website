# backend/app/schemas.py
from pydantic import BaseModel
from typing import List, Optional

class UserCreate(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class ProductOut(BaseModel):
    id: int
    name: str
    price: float
    description: str
    image: str
    stock: int
    class Config:
        orm_mode = True

class CartItemCreate(BaseModel):
    product_id: int
    quantity: int