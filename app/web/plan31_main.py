"""Main FastAPI application for Plan 31 Web API.

Composes all routes and wires dependencies via dependency injection.
"""

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI

from app.web.routes.orchestrator import router as orchestrator_router, set_dependencies as set_orchestrator_deps
from app.web.routes.messaging import router as messaging_router, set_dependencies as set_messaging_deps
from app.web.routes.auth import router as auth_router, set_dependencies as set_auth_deps
from app.web.routes.trace import router as trace_router, set_dependencies as set_trace_deps
from app.web.routes.options import router as options_router, set_options_dependencies
from app.web.sse_broker import SSEBroker


# Global dependencies
sse_broker = None
orchestrator = None
inter_department_bus = None
trace_producer = None
lifecycle_producer = None
audit_db = None
users_store = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    global sse_broker, orchestrator, inter_department_bus, trace_producer, lifecycle_producer, audit_db, users_store
    
    # Initialize SSE broker
    sse_broker = SSEBroker()
    await sse_broker.start()
    
    # Initialize placeholder dependencies
    # These will be replaced with real implementations in future phases
    orchestrator = None
    inter_department_bus = None
    trace_producer = None
    lifecycle_producer = None
    audit_db = None
    users_store = None
    
    # Wire dependencies
    set_orchestrator_deps(orchestrator, sse_broker)
    set_messaging_deps(inter_department_bus)
    set_auth_deps(audit_db, users_store)
    set_trace_deps(trace_producer, lifecycle_producer, sse_broker)
    set_options_dependencies(None)
    
    yield
    
    # Shutdown
    if sse_broker:
        await sse_broker.stop()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="SovereignAI Web API",
        description="Plan 31 Web API Layer",
        version="0.1.0",
        lifespan=lifespan,
    )
    
    # Include all routers
    app.include_router(orchestrator_router)
    app.include_router(messaging_router)
    app.include_router(auth_router)
    app.include_router(trace_router)
    app.include_router(options_router)
    
    # Health check endpoint
    @app.get("/health")
    async def health_check() -> dict[str, Any]:
        """Health check endpoint."""
        return {
            "status": "healthy",
            "version": "0.1.0",
        }
    
    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.web.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
