from datetime import datetime, timedelta, timezone
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .database import SessionLocal, get_db
from . import models, auth
from .router import auth_router, product_router, cart_router
from .services import email_service, ai_service

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router, prefix="/api")
app.include_router(product_router.router, prefix="/api")
app.include_router(cart_router.router, prefix="/api")

# --- 3. ABANDONED CART SCHEDULER ---
ABANDONED_CART_DELAY_MINUTES = 1  

def check_abandoned_carts():
    db = SessionLocal()
    try:
        threshold_time = datetime.now(timezone.utc) - timedelta(minutes=ABANDONED_CART_DELAY_MINUTES)
        
        abandoned_carts = db.query(models.Cart).filter(
            models.Cart.status == "active",
            models.Cart.updated_at <= threshold_time
        ).all()

        for cart in abandoned_carts:
            
            event = db.query(models.AbandonedCartEvent).filter(
                models.AbandonedCartEvent.cart_id == cart.id
            ).first()

            
            if event and event.email_sent >= 1:
                continue

            user = db.query(models.User).filter(models.User.id == cart.user_id).first()
            items = db.query(models.CartItem).filter(models.CartItem.cart_id == cart.id).all()
            
            if not user or not items:
                continue

            main_product = db.query(models.Product).filter(models.Product.id == items[0].product_id).first()
            if not main_product:
                continue

            token = auth.create_access_token(data={"sub": user.email, "cart_id": cart.id})

            print(f"📧 Sending exactly ONE recovery email to: {user.email}...")
            try:
                success = email_service.send_recovery_email(
                    to_email=user.email,
                    customer_name=user.email.split('@')[0],
                    product_name=main_product.name,
                    product_price=main_product.price,
                    image_url=main_product.image,
                    token=token
                )
            except Exception as mail_err:
                print(f"❌ Email sending error: {mail_err}")
                success = False

            
            if not event:
                new_event = models.AbandonedCartEvent(
                    cart_id=cart.id, 
                    user_id=user.id, 
                    email_sent=1 if success else 0,
                    email_sent_at=datetime.utcnow() if success else None
                )
                db.add(new_event)
            else:
                if success:
                    event.email_sent = 1
                    event.email_sent_at = datetime.utcnow()

            db.commit()
            print(f"✅ Email recorded. No more emails will be sent for Cart #{cart.id}.")

    except Exception as e:
        print(f"⚠️ Scheduler Error: {e}")
    finally:
        db.close()

@app.on_event("startup")
def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_abandoned_carts, 'interval', minutes=1)
    scheduler.start()

# --- 4. PRODUCTS & AI CHAT ENDPOINTS ---
@app.get("/api/products")
def get_products(db: Session = Depends(get_db)):
    return db.query(models.Product).all()

class ChatRequest(BaseModel):
    message: str
    cart_id: int = None

@app.post("/api/ai-support")
def ai_support_chat(req: ChatRequest, db: Session = Depends(get_db)):
    cart = db.query(models.Cart).filter(models.Cart.status == "active").first()
    if not cart:
        return {"reply": "Your cart is currently empty."}

    items = db.query(models.CartItem).filter(models.CartItem.cart_id == cart.id).all()
    if not items:
        return {"reply": "Your cart is empty."}
        
    main_product = db.query(models.Product).filter(models.Product.id == items[0].product_id).first()
    product_data = {
        "name": main_product.name,
        "price": main_product.price,
        "category": main_product.category,
        "stock": main_product.stock,
        "description": main_product.description
    }

    history = db.query(models.AIConversation).filter(models.AIConversation.cart_id == cart.id).order_by(models.AIConversation.created_at).all()
    ai_reply = ai_service.get_product_support_response(product_data, req.message, history)

    new_chat = models.AIConversation(cart_id=cart.id, user_id=cart.user_id, customer_message=req.message, ai_response=ai_reply)
    db.add(new_chat)
    db.commit()

    return {"reply": ai_reply}