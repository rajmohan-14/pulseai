from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import create_token, decode_token, hash_password, verify_password
from app.models.user import User
from app.schemas.user import LoginRequest, TokenResponse, UserCreate, UserResponse


class AuthError(Exception):
    def __init__(self, message: str, status_code: int = 401):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class AuthService:

    @staticmethod
    async def register(data: UserCreate, db: AsyncSession) -> UserResponse:
        # Check email not taken
        result = await db.execute(select(User).where(User.email == data.email))
        if result.scalar_one_or_none():
            raise AuthError("Email already registered", status_code=400)

        # Check username not taken
        result = await db.execute(select(User).where(User.username == data.username))
        if result.scalar_one_or_none():
            raise AuthError("Username already taken", status_code=400)

        # Create user with hashed password
        user = User(
            email=data.email,
            username=data.username,
            hashed_password=hash_password(data.password),
            role=data.role,
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)
        return UserResponse.model_validate(user)

    @staticmethod
    async def login(data: LoginRequest, db: AsyncSession) -> TokenResponse:
        # Find user
        result = await db.execute(select(User).where(User.email == data.email))
        user = result.scalar_one_or_none()

        # Vague error — don't reveal if email exists or not
        if not user or not verify_password(data.password, user.hashed_password):
            raise AuthError("Invalid email or password")

        if not user.is_active:
            raise AuthError("Account is deactivated", status_code=403)

        # Create both tokens
        token_data = {"sub": str(user.id), "role": user.role.value}
        return TokenResponse(
            access_token=create_token(token_data, token_type="access"),
            refresh_token=create_token(token_data, token_type="refresh"),
            user=UserResponse.model_validate(user),
        )

    @staticmethod
    async def refresh_tokens(refresh_token: str, db: AsyncSession) -> TokenResponse:
        from jose import JWTError
        try:
            payload = decode_token(refresh_token)
        except JWTError:
            raise AuthError("Invalid or expired refresh token")

        if payload.get("type") != "refresh":
            raise AuthError("Invalid token type")

        user_id = int(payload.get("sub"))
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            raise AuthError("User not found or deactivated")

        token_data = {"sub": str(user.id), "role": user.role.value}
        return TokenResponse(
            access_token=create_token(token_data, token_type="access"),
            refresh_token=create_token(token_data, token_type="refresh"),
            user=UserResponse.model_validate(user),
        )