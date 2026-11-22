from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.db.session import get_db
from app.models.organization import Organization
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
import uuid
import jwt

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    normalized_email = payload.email.lower().strip()
    org_name = payload.organization_name.strip()

    existing_user = db.scalar(
        select(User).where(User.email == normalized_email)
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered",
        )

    organization = db.scalar(
        select(Organization).where(
            func.lower(Organization.name) == org_name.lower()
        )
    )
    if organization is None:
        organization = Organization(name=org_name)
        db.add(organization)
        db.flush()  # Assigns organization.id inside the same transaction

    user = User(
        organization_id=organization.id,
        email=normalized_email,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = create_access_token(
        user_id=str(user.id), organization_id=str(user.organization_id)
    )
    refresh_token = create_refresh_token(
        user_id=str(user.id), organization_id=str(user.organization_id)
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    normalized_email = payload.email.lower().strip()
    user = db.scalar(select(User).where(User.email == normalized_email))

    # Return the same generic error whether email or password is wrong
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(
        user_id=str(user.id), organization_id=str(user.organization_id)
    )
    refresh_token = create_refresh_token(
        user_id=str(user.id), organization_id=str(user.organization_id)
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user),
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_tokens(
    payload: RefreshTokenRequest, db: Session = Depends(get_db)
):
    invalid_token_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired refresh token",
    )
    try:
        decoded = decode_token(payload.refresh_token)
        if decoded.get("type") != "refresh":
            raise invalid_token_exc
        user_id = uuid.UUID(decoded["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise invalid_token_exc

    user = db.get(User, user_id)
    if user is None:
        raise invalid_token_exc

    new_access = create_access_token(
        user_id=str(user.id), organization_id=str(user.organization_id)
    )
    new_refresh = create_refresh_token(
        user_id=str(user.id), organization_id=str(user.organization_id)
    )

    return TokenResponse(
        access_token=new_access,
        refresh_token=new_refresh,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user