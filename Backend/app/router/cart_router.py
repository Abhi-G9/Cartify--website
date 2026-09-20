from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models

router = APIRouter(prefix="/cart", tags=["Cart"])

class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = 1

@router.post("")
@router.post("/")
def add_to_cart(item: CartItemCreate, email: str, db: Session = Depends(get_db)):
   
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    cart = db.query(models.Cart).filter(models.Cart.user_id == user.id, models.Cart.status == "active").first()
    if not cart:
        cart = models.Cart(user_id=user.id, status="active")
        db.add(cart)
        db.commit()
        db.refresh(cart)

    cart_item = db.query(models.CartItem).filter(
        models.CartItem.cart_id == cart.id, 
        models.CartItem.product_id == item.product_id
    ).first()

    if cart_item:
        cart_item.quantity += item.quantity
    else:
        cart_item = models.CartItem(cart_id=cart.id, product_id=item.product_id, quantity=item.quantity)
        db.add(cart_item)

    db.commit()
    return {"message": "Product added to cart successfully"}