"""
Recovery Brain – FastAPI application entry point.

Wires together:
  - FastAPI app with CORS
  - All API routers (recovery, health, dashboard)
  - SQLite database initialisation
  - Optional MCP server mount (at /mcp) when mcp[cli] is installed
  - Structured JSON logging
"""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import load_settings
from app.core.database import init_db
from app.core.logging import setup_logging
from app.api.routes import health
from app.api.routes import recovery
from app.api.routes import dashboard

# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------

setup_logging()
init_db()

settings = load_settings()
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "AI Revenue Recovery Brain — detects revenue at risk, diagnoses "
        "payment failures, and executes bounded recovery workflows with "
        "full audit trails."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Restrict to your frontend origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# API routers
# ---------------------------------------------------------------------------

app.include_router(health.router)                           # /health
app.include_router(recovery.router)                        # /recovery/*
app.include_router(dashboard.router, prefix="/api/v1")     # /api/v1/dashboard/*

# ---------------------------------------------------------------------------
# Optional MCP server mount
# ---------------------------------------------------------------------------

try:
    from app.mcp.server import create_mcp_app
    mcp_app = create_mcp_app()
    if mcp_app is not None:
        # Mount as a sub-application so it lives at /mcp/*
        app.mount("/mcp", mcp_app)
        logger.info("MCP server mounted at /mcp")
    else:
        logger.info("MCP SDK not installed — /mcp endpoint unavailable")
except Exception as _mcp_err:  # pragma: no cover
    logger.warning("Could not mount MCP server: %s", _mcp_err)

# ---------------------------------------------------------------------------
# Startup / shutdown events
# ---------------------------------------------------------------------------

@app.on_event("startup")
async def on_startup() -> None:
    logger.info(
        "Recovery Brain starting up (env=%s, version=%s)",
        settings.environment,
        settings.app_version,
    )


@app.on_event("shutdown")
async def on_shutdown() -> None:
    logger.info("Recovery Brain shutting down")
