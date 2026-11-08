from fastapi import APIRouter, Depends, HTTPException , status 

from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.core.security import hash_password

#  adding the imports for login and token response

from fastapi.security import OAuth2PasswordRequestForm

from app.schemas.auth import LoginRequest, TokenResponse

from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
#  enabling the router for authentication endpoints
router = APIRouter(
    prefix = "/auth"
    , tags = ["Authentication"]
)



@router.post("/register",response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register (user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_data.email).first()

    if existing_user  :
        raise HTTPException(
            status_code  =status.HTTP_400_BAD_REQUEST,
            detail = "Email already exists"
        )
    
    hashed_password = hash_password(
        user_data.password
    )

    user = User(
            name=user_data.name,
            email=user_data.email,
            password_hash=hashed_password,
            role= user_data.role,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user



@router.post(
    "/login",
    response_model=TokenResponse
)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.email == login_data.email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not verify_password(
        login_data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "role": user.role
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }