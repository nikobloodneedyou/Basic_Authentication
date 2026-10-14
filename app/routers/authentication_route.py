from app.services.auth_service import AuthenticationService
from app.core.database import get_db
from fastapi.routing import APIRouter
from app.schemas.user import UserCreateRequest
from fastapi import Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/auth", tags=["Authentication"])
auth_service = AuthenticationService()


@router.post("/register")
async def register(user: UserCreateRequest, session: AsyncSession = Depends(get_db)):
    return await auth_service.register_service(user, session)


@router.post("/login")
async def login(email: str, password: str, session: AsyncSession = Depends(get_db)):
    return await auth_service.login_service(email, password, session)


@router.post("/logout")
async def logout(session: AsyncSession = Depends(get_db)):
    return await auth_service.logout_service(session)
