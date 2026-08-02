import json
from typing import Any

from pydantic import BaseModel


class ProviderNode(BaseModel):
    """Provider node in UI tree."""
    id: str
    name: str
    is_enabled: bool
    model_count: int
    last_sync_at: str | None = None
    sync_status: str


class FamilyNode(BaseModel):
    """Model family node in UI tree."""
    id: str
    provider_id: str
    name: str
    description: str
    model_count: int


class ModelNode(BaseModel):
    """Model node in UI tree."""
    id: str
    family_id: str
    name: str
    version_count: int


class VersionNode(BaseModel):
    """Model version node in UI tree."""
    id: str
    model_id: str
    version_string: str
    release_date: str | None = None
    is_latest: bool
    context_window: int | None = None
    supports_vision: bool
    supports_tools: bool


class ModelTreeResponse(BaseModel):
    """Tree-shaped response for UI (Provider → Family → Model → Version)."""
    providers: list[ProviderNode]


class ModelDetailResponse(BaseModel):
    """Detail view JSON for a specific model version."""
    id: str
    model_id: str
    family_id: str
    provider_id: str
    version_string: str
    release_date: str | None = None
    is_latest: bool
    context_window: int | None = None
    supports_vision: bool
    supports_tools: bool
    capabilities: dict[str, Any]
    pricing: dict[str, Any] | None = None


def build_model_tree(conn) -> ModelTreeResponse:  # type: ignore[no-untyped-def]
    """Build tree-shaped response from database."""
    # Get providers with model counts
    cursor = conn.execute(
        """
        SELECT
            p.id, p.name, p.is_enabled,
            COUNT(DISTINCT mv.id) as model_count
        FROM providers p
        LEFT JOIN families f ON p.id = f.provider_id
        LEFT JOIN models m ON f.id = m.family_id
        LEFT JOIN model_versions mv ON m.id = mv.model_id
        GROUP BY p.id
        """
    )

    providers = []
    for row in cursor.fetchall():
        providers.append(
            ProviderNode(
                id=row["id"],
                name=row["name"],
                is_enabled=bool(row["is_enabled"]),
                model_count=row["model_count"] or 0,
                last_sync_at=None,  # Will be filled by caller
                sync_status="unknown",  # Will be filled by caller
            )
        )

    return ModelTreeResponse(providers=providers)


def get_model_detail(conn, version_id: str) -> ModelDetailResponse | None:  # type: ignore[no-untyped-def]
    """Get detailed information for a specific model version."""
    cursor = conn.execute(
        """
        SELECT
            mv.id, mv.version_string, mv.release_date, mv.is_latest,
            mv.context_window, mv.supports_vision, mv.supports_tools,
            mv.capabilities,
            m.id as model_id, m.family_id,
            f.provider_id
        FROM model_versions mv
        JOIN models m ON mv.model_id = m.id
        JOIN families f ON m.family_id = f.id
        WHERE mv.id = ?
        """,
        (version_id,),
    )

    row = cursor.fetchone()
    if not row:
        return None

    return ModelDetailResponse(
        id=row["id"],
        model_id=row["model_id"],
        family_id=row["family_id"],
        provider_id=row["provider_id"],
        version_string=row["version_string"],
        release_date=row["release_date"],
        is_latest=bool(row["is_latest"]),
        context_window=row["context_window"],
        supports_vision=bool(row["supports_vision"]),
        supports_tools=bool(row["supports_tools"]),
        capabilities=json.loads(row["capabilities"]) if row["capabilities"] else {},
        pricing=None,  # Would be populated from provider API if available
    )
