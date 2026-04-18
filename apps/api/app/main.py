"""Nullify API — FastAPI entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import chat, health, scan

from app.auth import shutdown_pool
from app.tools import tool_registry
from app.tools.httpx_tool import HttpxTool
from app.tools.nmap import NmapTool
from app.tools.nuclei import NucleiTool
from app.tools.subfinder import SubfinderTool


def _register_tools() -> None:
    tool_registry.register(NmapTool())
    tool_registry.register(SubfinderTool())
    tool_registry.register(HttpxTool())
    tool_registry.register(NucleiTool())



@asynccontextmanager
async def lifespan(_app: FastAPI):
    _register_tools()
    available = tool_registry.list_available()
    print(f"[Nullify] {len(tool_registry.list_all())} tools registered, {len(available)} available")
    for t in available:
        print(f"  + {t.name}")
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
        "update_msg": "ml test"
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
