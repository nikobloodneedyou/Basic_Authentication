from app.repository.user_repo import UserRepository
from app.security.pwd_hash import hash_password, verify_password
from app.models.user import User
from app.schemas.user import UserCreateRequest
from app.services.jwt_service import create_access_token, decode_token
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

user_repo = UserRepository()


class AuthenticationService:
    async def register_service(self, user: UserCreateRequest, session: AsyncSession) -> JSONResponse:
        existing = await user_repo.get_user_by_email(session, user.email)
        if existing:
            return JSONResponse(content={"message": "User already exists"}, status_code=400)

        password_hash = hash_password(user.password)
        new_user = User(
            username=user.username,
            user_code=user.user_code,
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
        response = JSONResponse(content={"access_token": token})
        response.set_cookie("access_token", token, httponly=True, secure=False, samesite="lax", max_age=60 * 60)
        return response

    async def logout_service(self, session: AsyncSession) -> JSONResponse:
        response = JSONResponse(content={"message": "Logged out successfully"})
        response.delete_cookie("access_token")
        return response

    async def get_current_user(self, token: str, session: AsyncSession) -> User:
        try:
            payload = decode_token(token)
            email: str = payload.get("sub")
            if email is None:
                return None
            user = await user_repo.get_user_by_email(session, email)
            return user
        except Exception:
            return None