from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, auth

router = APIRouter(prefix="/auth", tags=["Auth"])

class UserAuth(BaseModel):
    email: str
    password: str

@router.post("/login")
def login(credentials: UserAuth, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == credentials.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid email or password"
        )

    if not auth.verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid email or password"
        )

    token = auth.create_access_token(data={"sub": user.email, "user_id": user.id})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/signup")
@router.post("/register")
def signup(credentials: UserAuth, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == credentials.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Email already registered"
        )
    
    hashed_pwd = auth.get_password_hash(credentials.password)
    new_user = models.User(email=credentials.email, password_hash=hashed_pwd)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully"}