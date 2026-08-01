"""Trace and lifecycle routes for Plan 31.

Provides SSE streaming for execution traces and REST endpoints for lifecycle events.
"""

from typing import Any

from fastapi import APIRouter, HTTPException

from app.web.schemas import ExecutionTraceEvent, LifecycleEvent
from app.web.sse_broker import SSEBroker


router = APIRouter(prefix="/api/trace", tags=["trace"])
health_router = APIRouter(prefix="/api", tags=["health"])


# Placeholder for dependencies - will be injected via DI
trace_producer = None
lifecycle_producer = None
sse_broker = None
health_aggregator = None
lifecycle_manager = None


def set_dependencies(trace_producer_dep=None, lifecycle_producer_dep=None, sse_broker_dep=None, health_aggregator_dep=None, lifecycle_manager_dep=None):
    """Set injected dependencies for trace routes."""
    global trace_producer, lifecycle_producer, sse_broker, health_aggregator, lifecycle_manager
    trace_producer = trace_producer_dep
    lifecycle_producer = lifecycle_producer_dep
    sse_broker = sse_broker_dep
    health_aggregator = health_aggregator_dep
    lifecycle_manager = lifecycle_manager_dep


@router.get("/stream")
async def stream_execution_trace():
    """SSE endpoint for execution trace streaming."""
    if sse_broker is None:
        raise HTTPException(status_code=503, detail="SSE broker not available")

    return await sse_broker.create_client("trace")


@router.get("/events")
async def get_trace_events():
    """Get recent trace events via REST."""
    if trace_producer is None:
        raise HTTPException(status_code=503, detail="Trace producer not available")

    try:
        events = await trace_producer.get_recent_events()
        return {"events": events}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/lifecycle/stream")
async def stream_lifecycle_events():
    """SSE endpoint for lifecycle event streaming."""
    if sse_broker is None:
        raise HTTPException(status_code=503, detail="SSE broker not available")

    return await sse_broker.create_client("lifecycle")


@router.get("/lifecycle/events")
async def get_lifecycle_events():
    """Get recent lifecycle events via REST."""
    if lifecycle_producer is None:
        raise HTTPException(status_code=503, detail="Lifecycle producer not available")

    try:
        events = await lifecycle_producer.get_recent_events()
        return {"events": events}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/events")
async def publish_trace_event(event: ExecutionTraceEvent):
    """Publish a trace event (for testing/external sources)."""
    if sse_broker is None:
        raise HTTPException(status_code=503, detail="SSE broker not available")

    try:
        await sse_broker.publish("trace", event.model_dump())
        return {"status": "published"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/lifecycle/events")
async def publish_lifecycle_event(event: LifecycleEvent):
    """Publish a lifecycle event (for testing/external sources)."""
    if sse_broker is None:
        raise HTTPException(status_code=503, detail="SSE broker not available")

    try:
        await sse_broker.publish("lifecycle", event.model_dump())
        return {"status": "published"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@health_router.get("/health")
async def get_health():
    """Get aggregated health status of all components."""
    if health_aggregator is None:
        raise HTTPException(status_code=503, detail="Health aggregator not available")

    try:
        return health_aggregator.get_health_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@health_router.get("/lifecycle/ready")
async def get_lifecycle_ready():
    """Get lifecycle ready status."""
    if lifecycle_manager is None:
        raise HTTPException(status_code=503, detail="Lifecycle manager not available")

    try:
        from sovereignai.lifecycle.types import LifecycleState
        
        state = lifecycle_manager.state
        return {
            "ready": state in (LifecycleState.READY, LifecycleState.DEGRADED),
            "state": state.value,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
