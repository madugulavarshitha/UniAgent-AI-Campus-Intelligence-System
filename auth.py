from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.security.jwt import verify_password, create_access_token
from app.api.dependencies import get_current_user
from app.crud.user import get_user_by_email, create_user
from app.schemas.auth import UserCreate, UserLogin, Token, UserResponse
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, user_in.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    return create_user(db, user_in)

@router.post("/login", response_model=Token)
def login(login_in: UserLogin, db: Session = Depends(get_db)):
    user = get_user_by_email(db, login_in.email)
    if not user or not verify_password(login_in.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
    
    access_token = create_access_token(subject=user.id, role=user.role)
    user_res = UserResponse(
        id=user.id,
        email=user.email,
        role=user.role,
        full_name=user.full_name
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_res
    }

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
