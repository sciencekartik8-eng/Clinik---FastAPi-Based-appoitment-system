from fastapi import Depends , HTTPException , status 
from fastapi.security import  HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from  jose import JWTError, jwt
from  sqlalchemy.orm import Session


from app.core.config import settings
from app.db.database import get_db
from app.models.user import User


# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

security = HTTPBearer()
#  this tells fastapi that the token will be sent in the Authorization header as a Bearer token. and passes into the get_current_user function as a dependency.
#  this is casuing the problem 
# def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )

#     try:
#         payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
#         user_id: int = payload.get("sub")
#         if user_id is None:
#             raise credentials_exception

#     except JWTError:
#         raise credentials_exception

#     user = (
#         db.query(User)
#         .filter(User.id == int(user_id))
#         .first()

#     )

#     if user is None:
#         raise credentials_exception

#     if not user.is_active:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="User is inactive",
#         )

#     return user 

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:

    token = credentials.credentials

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = (
        db.query(User)
        .filter(User.id == int(user_id))
        .first()
    )

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    return user


#  adding role based authorization
# 1.) patient role 
def require_patient(
        current_user: User = Depends(get_current_user)
) -> User:
    if current_user.role.casefold() != "patient":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have the required role"
        )
    return current_user

# 2.) doctor role

def require_doctor(
        current_user: User = Depends(get_current_user)
) -> User:
    if current_user.role.casefold() != "doctor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have the required role"
        )
    return current_user


#  3.) admin role
def require_admin(
        current_user: User = Depends(get_current_user)
) -> User:
    if current_user.role.casefold() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have the required role"
        )
    return current_user


# dependencies.py

# security
#    │
#    └── HTTPBearer

# get_current_user()
#    │
#    ├── Validate JWT
#    ├── Extract user ID
#    └── Get User from DB
#           │
#           ├── require_patient()
#           ├── require_doctor()
#           └── require_admin()