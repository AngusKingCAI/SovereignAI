from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from sovereignai.model_registry.adapters import ADAPTER_REGISTRY
from sovereignai.model_registry.database import get_last_successful_sync_at, initialize_database
from sovereignai.model_registry.offline import get_offline_status

router = APIRouter(prefix="/api/models", tags=["models"])


class ProviderResponse(BaseModel):
    """Response model for provider information."""
    id: str
    name: str
    is_enabled: bool
    last_sync_at: str | None = None
    sync_status: str


class ModelResponse(BaseModel):
    """Response model for model information."""
    id: str
    name: str
    family_id: str
    family_name: str
    provider_id: str
    version_string: str
    context_window: int | None = None
    supports_vision: bool = False
    supports_tools: bool = False


class SyncRequest(BaseModel):
    """Request model for triggering sync."""
    provider_id: str


class SyncResponse(BaseModel):
    """Response model for sync operation."""
    status: str
    provider_id: str
    message: str


def get_db_connection():  # type: ignore[no-untyped-def]
    """Get database connection."""
    db_path = Path("model_registry.db")
    return initialize_database(db_path)


@router.get("/providers", response_model=list[ProviderResponse])
def list_providers():  # type: ignore[no-untyped-def]
    """List all providers."""
    conn = get_db_connection()

    cursor = conn.execute("SELECT id, name, is_enabled FROM providers")
    providers = []

    for row in cursor.fetchall():
        provider_id = row["id"]
        last_sync = get_last_successful_sync_at(conn, provider_id)
        offline_status = get_offline_status(conn, provider_id)

        providers.append(
            ProviderResponse(
                id=provider_id,
                name=row["name"],
                is_enabled=bool(row["is_enabled"]),
                last_sync_at=last_sync.isoformat() if last_sync else None,
                sync_status=offline_status["status"],
            )
        )

    conn.close()
    return providers


@router.get("", response_model=list[ModelResponse])
def list_models(
    provider_id: str | None = Query(None),
    family_name: str | None = Query(None),
    supports_vision: bool | None = Query(None),
    supports_tools: bool | None = Query(None),
) -> list[ModelResponse]:
    """List models with optional filters."""
    conn = get_db_connection()

    query = """
        SELECT
            mv.id, mv.version_string, mv.context_window,
            mv.supports_vision, mv.supports_tools,
            m.id as model_id, m.family_id, m.name as model_name,
            f.name as family_name, f.provider_id
        FROM model_versions mv
        JOIN models m ON mv.model_id = m.id
        JOIN families f ON m.family_id = f.id
        WHERE 1=1
    """
    params = []

    if provider_id:
        query += " AND f.provider_id = ?"
        params.append(provider_id)

    if family_name:
        query += " AND LOWER(f.name) LIKE ?"
        params.append(f"%{family_name.lower()}%")

    if supports_vision is not None:
        query += " AND mv.supports_vision = ?"
        params.append(str(1 if supports_vision else 0))

    if supports_tools is not None:
        query += " AND mv.supports_tools = ?"
        params.append(str(1 if supports_tools else 0))

    cursor = conn.execute(query, params)
    models = []

    for row in cursor.fetchall():
        models.append(
            ModelResponse(
                id=row["id"],
                name=row["model_name"],
                family_id=row["family_id"],
                family_name=row["family_name"],
                provider_id=row["provider_id"],
                version_string=row["version_string"],
                context_window=row["context_window"],
                supports_vision=bool(row["supports_vision"]),
                supports_tools=bool(row["supports_tools"]),
            )
        )

    conn.close()
    return models


@router.get("/{model_id}", response_model=ModelResponse)
def get_model(model_id: str):  # type: ignore[no-untyped-def]
    """Get a specific model by ID."""
    conn = get_db_connection()

    query = """
        SELECT
            mv.id, mv.version_string, mv.context_window,
            mv.supports_vision, mv.supports_tools,
            m.id as model_id, m.family_id, m.name as model_name,
            f.name as family_name, f.provider_id
        FROM model_versions mv
        JOIN models m ON mv.model_id = m.id
        JOIN families f ON m.family_id = f.id
        WHERE mv.id = ?
    """

    cursor = conn.execute(query, (model_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Model not found")

    model = ModelResponse(
        id=row["id"],
        name=row["model_name"],
        family_id=row["family_id"],
        family_name=row["family_name"],
        provider_id=row["provider_id"],
        version_string=row["version_string"],
        context_window=row["context_window"],
        supports_vision=bool(row["supports_vision"]),
        supports_tools=bool(row["supports_tools"]),
    )

    conn.close()
    return model


@router.post("/sync", response_model=SyncResponse)
def trigger_sync(request: SyncRequest):  # type: ignore[no-untyped-def]
    """Trigger a sync for a specific provider."""
    provider_id = request.provider_id.lower().replace(" ", "")

    # Check if provider exists in registry
    if provider_id not in ADAPTER_REGISTRY:
        raise HTTPException(status_code=404, detail="Provider not found in registry")

    # In a real implementation, this would trigger an async sync
    # For now, return a success response
    return SyncResponse(
        status="triggered",
        provider_id=provider_id,
        message=f"Sync triggered for provider {provider_id}",
    )
