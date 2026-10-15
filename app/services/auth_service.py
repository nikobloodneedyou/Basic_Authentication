from app.repository.user_repo import UserRepository
from app.security.pwd_hash import hash_password, verify_password
from app.models.user import User
from app.schemas.user import UserCreateRequest
from app.services.jwt_service import create_access_token, decode_token, ACCESS_TOKEN_EXPIRE_MINUTES
from fastapi.responses import JSONResponse
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

user_repo = UserRepository()

COOKIE_MAX_AGE = ACCESS_TOKEN_EXPIRE_MINUTES * 60  # seconds


class AuthenticationService:
    async def register_service(self, user: UserCreateRequest, session: AsyncSession) -> JSONResponse:
        existing = await user_repo.get_user_by_email(session, user.email)
        if existing:
            return JSONResponse(content={"message": "User already exists"}, status_code=400)

        password_hash = hash_password(user.password)
        username = user.username or user.email.split("@")[0]
        user_code = user.user_code or user.email.split("@")[0]
        new_user = User(
            username=username,
            user_code=user_code,
            email=user.email,
            password=password_hash,
            age=user.age,
            role=user.role,
        )
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return JSONResponse(content={"message": "User registered successfully"}, status_code=201)

    async def login_service(self, email: str, password: str, session: AsyncSession) -> JSONResponse:
        user = await user_repo.get_user_by_email(session, email)
        if not user:
            return JSONResponse(status_code=400, content={"message": "User not found"})
        if not verify_password(password, user.password):
            return JSONResponse(status_code=400, content={"message": "Invalid password"})
        token = create_access_token(data={"sub": user.email, "role": user.role})
        response = JSONResponse(content={"access_token": token, "message": "Login successful"})
        response.set_cookie(
            "access_token",
            token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=COOKIE_MAX_AGE,
        )
        return response

    async def logout_service(self, session: AsyncSession) -> JSONResponse:
        response = JSONResponse(content={"message": "Logged out successfully"})
        response.delete_cookie("access_token")
        return response

    async def get_current_user(self, token: str, session: AsyncSession) -> User | None:
        try:
            payload = decode_token(token)
            email: str = payload.get("sub")
            if email is None:
                return None
            return await user_repo.get_user_by_email(session, email)
        except (JWTError, Exception):
            return None

    async def get_current_user_from_cookie(self, request, session: AsyncSession) -> User | None:
        token = request.cookies.get("access_token")
        if not token:
            return None
        return await self.get_current_user(token, session)