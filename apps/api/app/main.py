"""Nullify API — FastAPI entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import chat, health, scan

from app.auth import shutdown_pool
from app.tools import tool_registry
from app.agents import agent_registry



@asynccontextmanager
async def lifespan(_app: FastAPI):
    tool_registry.discover_and_register()
    available = tool_registry.list_available()
    print(f"[Nullify] {len(tool_registry.list_all())} tools registered, {len(available)} available")
    for t in available:
        print(f"  + {t.name}")

    agent_registry.discover_and_register()
    agents = agent_registry.list_all()
    print(f"[Nullify] {len(agents)} agents registered")
    for a in agents:
        print(f"  > {a.name}: {a.description[:60]}")
    yield
    await shutdown_pool()


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
)

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Nullify API",
        "update_msg": "Réinstallation des outils compromis. 3"
    }

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(chat.router)
app.include_router(scan.router)
