from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from routes.auth_routes import router as auth_router
from routes.meeting_routes import router as meeting_router
from routes.live_meeting_routes import router as live_router
from routes.live_ws_routes import router as ws_router
from routes.qa_routes import router as qa_router


# =====================================================
# LIFESPAN (STARTUP TASKS)
# =====================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    folders = [
        "uploads",
        "temp",
        "vector_db",
        "transcripts"
    ]

    for f in folders:
        os.makedirs(f, exist_ok=True)

    yield


# =====================================================
# APP INIT
# =====================================================
app = FastAPI(
    title="Whisp AI Backend",
    version="1.0.0",
    lifespan=lifespan
)


# =====================================================
# CORS (PRODUCTION SAFE BASE CONFIG)
# =====================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================================================
# ROUTERS (CLEAN PREFIX ARCHITECTURE)
# =====================================================
app.include_router(auth_router, prefix="/api/v1/auth")
app.include_router(meeting_router, prefix="/api/v1/meetings")
app.include_router(live_router, prefix="/api/v1/live")

# WebSocket routes should NOT get API prefix unless intentional
app.include_router(ws_router, prefix="/api/v1/live")

app.include_router(qa_router, prefix="/api/v1/qa")


# =====================================================
# ROOT
# =====================================================
@app.get("/")
def root():
    return {
        "service": "Whisp Backend",
        "status": "running"
    }


# =====================================================
# HEALTH CHECK (IMPORTANT FOR DEPLOYMENT)
# =====================================================
@app.get("/health")
def health():
    return {
        "status": "ok"
    }