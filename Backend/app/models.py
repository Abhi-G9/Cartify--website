from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True)
    password_hash = Column(String(255))

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)
    category = Column(String(50))
    price = Column(Float)
    description = Column(String(500))
    image = Column(String(255))
    stock = Column(Integer)

class Cart(Base):
    __tablename__ = "carts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String(20), default="active")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    items = relationship("CartItem", back_populates="cart")

class CartItem(Base):
    __tablename__ = "cart_items"
    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("carts.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, default=1)
    cart = relationship("Cart", back_populates="items")
    product = relationship("Product")

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    total_amount = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
class AbandonedCartEvent(Base):
    __tablename__ = "abandoned_cart_events"
    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("carts.id"), unique=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    detected_at = Column(DateTime, default=datetime.utcnow)
    email_sent = Column(Integer, default=0) 
    email_sent_at = Column(DateTime, nullable=True)
    recovered = Column(Integer, default=0)
    recovered_at = Column(DateTime, nullable=True)

class AIConversation(Base):
    __tablename__ = "ai_conversations"
    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("carts.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    customer_message = Column(String(1000))
    ai_response = Column(String(2000))
    created_at = Column(DateTime, default=datetime.utcnow)