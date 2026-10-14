from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.database import init_db
from app.routers.authentication_route import router as auth_router
@asynccontextmanager
async def lifecycle(app: FastAPI):
    await init_db()
    yield
    # Perform any cleanup tasks here if needed
app = FastAPI(title = "Basic Authentication", version = "1.0", debug = True, lifespan=lifecycle)
app.include_router(auth_router)
@app.get("/")
async def root():
    return {"message": "Hello Welcome to FastAPI Basic Authentication!"}
