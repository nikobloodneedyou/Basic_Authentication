from uuid import uuid4

from fastapi import Depends, HTTPException, Request
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.user import UserCreateRequest
from app.services.auth_service import AuthenticationService

router = APIRouter(prefix="/auth", tags=["Authentication"])
auth_service = AuthenticationService()


async def _extract_payload(request: Request) -> dict:
    content_type = request.headers.get("content-type", "").lower()
    try:
        if "application/json" in content_type:
            return await request.json()
        if "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
            form = await request.form()
            return dict(form)
    except Exception:
        return {}
    return {}


@router.post("/register")
async def register(request: Request, session: AsyncSession = Depends(get_db)):
    payload = await _extract_payload(request)
    if not payload:
        raise HTTPException(status_code=400, detail="Registration payload is required")

    email = payload.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

    password = payload.get("password")
    if not password:
        raise HTTPException(status_code=400, detail="Password is required")

    user_data = {
        "username": payload.get("username") or email.split("@")[0],
        "user_code": payload.get("user_code") or uuid4().hex[:12],
        "email": email,
        "password": password,
        "age": int(payload.get("age") or 18),
        "role": payload.get("role") or "user",
    }

    return await auth_service.register_service(UserCreateRequest(**user_data), session)


@router.post("/login")
async def login(request: Request, session: AsyncSession = Depends(get_db)):
    payload = await _extract_payload(request)
    # Accept both "email" and "username" keys (form sends "username" field)
    email = payload.get("email") or payload.get("username")
    password = payload.get("password")

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    return await auth_service.login_service(email, password, session)


@router.post("/logout")
async def logout(session: AsyncSession = Depends(get_db)):
    return await auth_service.logout_service(session)


@router.get("/me")
async def get_me(request: Request, session: AsyncSession = Depends(get_db)):
    """Return the current logged-in user's profile (reads httponly cookie)."""
    user = await auth_service.get_current_user_from_cookie(request, session)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "age": user.age,
        "user_code": user.user_code,
    }
