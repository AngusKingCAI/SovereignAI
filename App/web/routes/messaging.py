"""Messaging API routes for Plan 31.

Provides REST endpoints for cross-department messaging.
"""

from typing import Any

from fastapi import APIRouter, HTTPException, Request

from app.web.schemas import (
    AuditPage,
    CircuitState,
    CircuitStateList,
    CrossDepartmentMessage,
    MessagingAuditEntryDTO,
)


router = APIRouter(prefix="/api/messaging", tags=["messaging"])


# Placeholder for dependencies - will be injected via DI
inter_department_bus = None


def set_dependencies(inter_department_bus_dep=None):
    """Set injected dependencies for messaging routes."""
    global inter_department_bus
    inter_department_bus = inter_department_bus_dep


@router.post("/send")
async def send_message(message: CrossDepartmentMessage) -> dict[str, str]:
    """Send a cross-department message via InterDepartmentBus."""
    if inter_department_bus is None:
        raise HTTPException(status_code=503, detail="Messaging service not available")

    try:
        await inter_department_bus.send(
            source_department=message.source_department,
            target_department=message.target_department,
            content=message.content,
            correlation_id=message.correlation_id,
        )
        return {"status": "sent", "correlation_id": message.correlation_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/audit", response_model=AuditPage[MessagingAuditEntryDTO])
async def get_audit_log(
    offset: int = 0,
    limit: int = 100,
) -> AuditPage[MessagingAuditEntryDTO]:
    """Get paginated audit log for messaging.

    Max page size: 1000.
    """
    if inter_department_bus is None:
        raise HTTPException(status_code=503, detail="Messaging service not available")

    # Validate page size
    limit = max(1, min(limit, 1000))

    try:
        audit_data = await inter_department_bus.get_audit_log(
            offset=offset,
            limit=limit,
        )

        # Convert to DTOs
        entries = [
            MessagingAuditEntryDTO(
                id=entry["id"],
                source_department=entry["source_department"],
                target_department=entry["target_department"],
                content_preview=entry["content_preview"],
                timestamp=entry["timestamp"],
            )
            for entry in audit_data["items"]
        ]

        return AuditPage[MessagingAuditEntryDTO](
            items=entries,
            total_count=audit_data["total_count"],
            offset=offset,
            limit=limit,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/circuits", response_model=CircuitStateList)
async def get_circuit_state() -> CircuitStateList:
    """Get circuit breaker state for all departments."""
    if inter_department_bus is None:
        raise HTTPException(status_code=503, detail="Messaging service not available")

    try:
        circuits_data = await inter_department_bus.get_circuit_state()

        from app.web.schemas import CircuitState
        circuits = [
            CircuitState(
                worker_id=circuit["worker_id"],
                state=circuit["state"],
                error_count=circuit["error_count"],
                last_error=circuit.get("last_error"),
            )
            for circuit in circuits_data["circuits"]
        ]

        return CircuitStateList(circuits=circuits)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
