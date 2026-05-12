"""Auth endpoints: register, login, me."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import create_access_token, get_current_user, hash_password, verify_password
from app.database import get_session
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest, UserOut

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _user_to_out(row) -> UserOut:
    m = row._mapping
    return UserOut(
        id=m["id"],
        email=m["email"],
        display_name=m["display_name"],
        created_at=m["created_at"],
    )


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    body: RegisterRequest,
    session: AsyncSession = Depends(get_session),
) -> AuthResponse:
    """Register a new user. Returns the user object plus a JWT."""
    existing = await session.execute(
        text("SELECT id FROM users WHERE email = :email"),
        {"email": body.email.lower()},
    )
    if existing.fetchone() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    pw_hash = hash_password(body.password)
    result = await session.execute(
        text(
            "INSERT INTO users (email, display_name, password_hash, auth_provider) "
            "VALUES (:email, :display_name, :password_hash, 'local') "
            "RETURNING id, email, display_name, created_at"
        ),
        {
            "email": body.email.lower(),
            "display_name": body.display_name,
            "password_hash": pw_hash,
        },
    )
    row = result.fetchone()
    await session.commit()

    user = _user_to_out(row)
    token = create_access_token(user.id)
    return AuthResponse(user=user, token=token)


@router.post("/login", response_model=AuthResponse)
async def login(
    body: LoginRequest,
    session: AsyncSession = Depends(get_session),
) -> AuthResponse:
    """Verify credentials and return a JWT."""
    result = await session.execute(
        text(
            "SELECT id, email, display_name, password_hash, created_at "
            "FROM users WHERE email = :email"
        ),
        {"email": body.email.lower()},
    )
    row = result.fetchone()
    if row is None or row._mapping["password_hash"] is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )
    if not verify_password(body.password, row._mapping["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    user = _user_to_out(row)
    token = create_access_token(user.id)
    return AuthResponse(user=user, token=token)


@router.get("/me", response_model=UserOut)
async def me(
    user_id: UUID = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> UserOut:
    """Return the current authenticated user."""
    result = await session.execute(
        text("SELECT id, email, display_name, created_at FROM users WHERE id = :id"),
        {"id": str(user_id)},
    )
    row = result.fetchone()
    if row is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return _user_to_out(row)
