from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db, init_db
from app.routers.authentication_route import router as auth_router
from app.services.auth_service import AuthenticationService

BASE_DIR = Path(__file__).resolve().parent.parent
auth_service = AuthenticationService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Basic Authentication",
    version="1.0",
    debug=True,
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.include_router(auth_router)


@app.get("/")
async def root():
    return RedirectResponse(url="/login", status_code=302)


@app.get("/login", response_class=HTMLResponse)
async def render_login(request: Request, session: AsyncSession = Depends(get_db)):
    # Already logged in → go straight to dashboard
    user = await auth_service.get_current_user_from_cookie(request, session)
    if user:
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse(request, "login.html", {"request": request})


@app.get("/register", response_class=HTMLResponse)
async def render_register(request: Request, session: AsyncSession = Depends(get_db)):
    # Already logged in → go straight to dashboard
    user = await auth_service.get_current_user_from_cookie(request, session)
    if user:
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse(request, "register.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse)
async def render_dashboard(request: Request, session: AsyncSession = Depends(get_db)):
    # Not logged in → back to login
    user = await auth_service.get_current_user_from_cookie(request, session)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse(request, "dashboard.html", {"request": request})
