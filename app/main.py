from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db.lifespan import lifespan
from .core.config import settings
from .routes import auth
from .routes import user


app = FastAPI(
    app_name = settings.APP_NAME,
    lifespan = lifespan,
    docs_url="/api/docs",
)

cors_origins = [
    origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(user.router)
@app.get("/health")
async def health():
    return {
        "status": "ok"
    }
    
@app.get("/")
def root():
    return {
        "message": "Welcome to fastapi API",
        "docs": "/api/docs",
    }