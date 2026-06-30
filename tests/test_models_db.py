"""Test the models database module for HuggingFace GGUF catalog."""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from sovereignai.shared.models_db import (
    get_families,
    get_model_by_repo_and_quant,
    get_models,
    get_total_count,
    insert_or_update_model,
)


@pytest.fixture
def test_db(tmp_path: Path) -> sqlite3.Connection:
    """Create a test database with sample data."""
    db_path = tmp_path / "test_models.db"
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    conn.execute("""
        CREATE TABLE models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repo_id TEXT NOT NULL,
            model_family TEXT,
            architecture TEXT,
            base_parameter_count INTEGER,
            quantization TEXT,
            filename TEXT NOT NULL,
            file_size_bytes INTEGER NOT NULL,
            file_size_gb REAL NOT NULL,
            context_length INTEGER,
            license TEXT,
            downloads INTEGER,
            likes INTEGER,
            last_modified TEXT,
            tags TEXT,
            vram_required_gb REAL,
            active_bytes_gb REAL,
            sync_timestamp TEXT NOT NULL,
            UNIQUE(repo_id, quantization)
        )
    """)

    conn.execute("""
        CREATE INDEX idx_models_family ON models(model_family)
    """)

    conn.execute("""
        CREATE INDEX idx_models_size ON models(file_size_gb)
    """)

    conn.commit()
    return conn


def test_insert_model(test_db: sqlite3.Connection) -> None:
    """Test inserting a model into the database."""
    insert_or_update_model(
        conn=test_db,
        repo_id="lmstudio-community/gemma-4-E4B-it-GGUF",
        model_family="gemma",
        architecture="dense",
        base_parameter_count=4000000000,
        quantization="Q4_K_M",
        filename="gemma-4-E4B-it-Q4_K_M.gguf",
        file_size_bytes=5335290074,
        context_length=131072,
        license="MIT",
        downloads=1000000,
        likes=50000,
        last_modified="2026-06-30T00:00:00Z",
        tags=["gguf", "gemma"],
    )

    models = get_models(test_db, limit=10)
    assert len(models) == 1
    assert models[0]["repo_id"] == "lmstudio-community/gemma-4-E4B-it-GGUF"
    assert models[0]["quantization"] == "Q4_K_M"
    assert models[0]["vram_required_gb"] > 0
    assert models[0]["active_bytes_gb"] > 0


def test_get_models_with_search(test_db: sqlite3.Connection) -> None:
    """Test searching models by repo_id or quantization."""
    insert_or_update_model(
        conn=test_db,
        repo_id="lmstudio-community/gemma-4-E4B-it-GGUF",
        model_family="gemma",
        architecture="dense",
        base_parameter_count=4000000000,
        quantization="Q4_K_M",
        filename="gemma-4-E4B-it-Q4_K_M.gguf",
        file_size_bytes=5335290074,
        context_length=131072,
        license="MIT",
        downloads=1000000,
        likes=50000,
        last_modified="2026-06-30T00:00:00Z",
        tags=["gguf", "gemma"],
    )

    insert_or_update_model(
        conn=test_db,
        repo_id="lmstudio-community/llama-3-8B-it-GGUF",
        model_family="llama",
        architecture="dense",
        base_parameter_count=8000000000,
        quantization="Q5_K_M",
        filename="llama-3-8B-it-Q5_K_M.gguf",
        file_size_bytes=6000000000,
        context_length=8192,
        license="Apache-2.0",
        downloads=2000000,
        likes=100000,
        last_modified="2026-06-30T00:00:00Z",
        tags=["gguf", "llama"],
    )

    # Search for "gemma"
    gemma_models = get_models(test_db, search="gemma", limit=10)
    assert len(gemma_models) == 1
    assert "gemma" in gemma_models[0]["repo_id"].lower()

    # Search for "Q4"
    q4_models = get_models(test_db, search="Q4", limit=10)
    assert len(q4_models) == 1
    assert q4_models[0]["quantization"] == "Q4_K_M"


def test_get_models_with_family_filter(test_db: sqlite3.Connection) -> None:
    """Test filtering models by family."""
    insert_or_update_model(
        conn=test_db,
        repo_id="lmstudio-community/gemma-4-E4B-it-GGUF",
        model_family="gemma",
        architecture="dense",
        base_parameter_count=4000000000,
        quantization="Q4_K_M",
        filename="gemma-4-E4B-it-Q4_K_M.gguf",
        file_size_bytes=5335290074,
        context_length=131072,
        license="MIT",
        downloads=1000000,
        likes=50000,
        last_modified="2026-06-30T00:00:00Z",
        tags=["gguf", "gemma"],
    )

    insert_or_update_model(
        conn=test_db,
        repo_id="lmstudio-community/llama-3-8B-it-GGUF",
        model_family="llama",
        architecture="dense",
        base_parameter_count=8000000000,
        quantization="Q5_K_M",
        filename="llama-3-8B-it-Q5_K_M.gguf",
        file_size_bytes=6000000000,
        context_length=8192,
        license="Apache-2.0",
        downloads=2000000,
        likes=100000,
        last_modified="2026-06-30T00:00:00Z",
        tags=["gguf", "llama"],
    )

    # Filter by "gemma" family
    gemma_models = get_models(test_db, family="gemma", limit=10)
    assert len(gemma_models) == 1
    assert gemma_models[0]["model_family"] == "gemma"

    # Filter by "llama" family
    llama_models = get_models(test_db, family="llama", limit=10)
    assert len(llama_models) == 1
    assert llama_models[0]["model_family"] == "llama"


def test_get_total_count(test_db: sqlite3.Connection) -> None:
    """Test getting total count of models."""
    insert_or_update_model(
        conn=test_db,
        repo_id="lmstudio-community/gemma-4-E4B-it-GGUF",
        model_family="gemma",
        architecture="dense",
        base_parameter_count=4000000000,
        quantization="Q4_K_M",
        filename="gemma-4-E4B-it-Q4_K_M.gguf",
        file_size_bytes=5335290074,
        context_length=131072,
        license="MIT",
        downloads=1000000,
        likes=50000,
        last_modified="2026-06-30T00:00:00Z",
        tags=["gguf", "gemma"],
    )

    insert_or_update_model(
        conn=test_db,
        repo_id="lmstudio-community/llama-3-8B-it-GGUF",
        model_family="llama",
        architecture="dense",
        base_parameter_count=8000000000,
        quantization="Q5_K_M",
        filename="llama-3-8B-it-Q5_K_M.gguf",
        file_size_bytes=6000000000,
        context_length=8192,
        license="Apache-2.0",
        downloads=2000000,
        likes=100000,
        last_modified="2026-06-30T00:00:00Z",
        tags=["gguf", "llama"],
    )

    assert get_total_count(test_db) == 2
    assert get_total_count(test_db, search="gemma") == 1
    assert get_total_count(test_db, family="llama") == 1


def test_get_model_by_repo_and_quant(test_db: sqlite3.Connection) -> None:
    """Test getting a specific model by repo_id and quantization."""
    insert_or_update_model(
        conn=test_db,
        repo_id="lmstudio-community/gemma-4-E4B-it-GGUF",
        model_family="gemma",
        architecture="dense",
        base_parameter_count=4000000000,
        quantization="Q4_K_M",
        filename="gemma-4-E4B-it-Q4_K_M.gguf",
        file_size_bytes=5335290074,
        context_length=131072,
        license="MIT",
        downloads=1000000,
        likes=50000,
        last_modified="2026-06-30T00:00:00Z",
        tags=["gguf", "gemma"],
    )

    model = get_model_by_repo_and_quant(
        test_db,
        "lmstudio-community/gemma-4-E4B-it-GGUF",
        "Q4_K_M"
    )
    assert model is not None
    assert model["repo_id"] == "lmstudio-community/gemma-4-E4B-it-GGUF"
    assert model["quantization"] == "Q4_K_M"

    # Test non-existent model
    none_model = get_model_by_repo_and_quant(
        test_db,
        "nonexistent/model",
        "Q4_K_M"
    )
    assert none_model is None


def test_get_families(test_db: sqlite3.Connection) -> None:
    """Test getting unique model families."""
    insert_or_update_model(
        conn=test_db,
        repo_id="lmstudio-community/gemma-4-E4B-it-GGUF",
        model_family="gemma",
        architecture="dense",
        base_parameter_count=4000000000,
        quantization="Q4_K_M",
        filename="gemma-4-E4B-it-Q4_K_M.gguf",
        file_size_bytes=5335290074,
        context_length=131072,
        license="MIT",
        downloads=1000000,
        likes=50000,
        last_modified="2026-06-30T00:00:00Z",
        tags=["gguf", "gemma"],
    )

    insert_or_update_model(
        conn=test_db,
        repo_id="lmstudio-community/llama-3-8B-it-GGUF",
        model_family="llama",
        architecture="dense",
        base_parameter_count=8000000000,
        quantization="Q5_K_M",
        filename="llama-3-8B-it-Q5_K_M.gguf",
        file_size_bytes=6000000000,
        context_length=8192,
        license="Apache-2.0",
        downloads=2000000,
        likes=100000,
        last_modified="2026-06-30T00:00:00Z",
        tags=["gguf", "llama"],
    )

    families = get_families(test_db)
    assert len(families) == 2
    assert "gemma" in families
    assert "llama" in families


def test_update_existing_model(test_db: sqlite3.Connection) -> None:
    """Test that inserting a model with same repo_id and quantization updates it."""
    insert_or_update_model(
        conn=test_db,
        repo_id="lmstudio-community/gemma-4-E4B-it-GGUF",
        model_family="gemma",
        architecture="dense",
        base_parameter_count=4000000000,
        quantization="Q4_K_M",
        filename="gemma-4-E4B-it-Q4_K_M.gguf",
        file_size_bytes=5335290074,
        context_length=131072,
        license="MIT",
        downloads=1000000,
        likes=50000,
        last_modified="2026-06-30T00:00:00Z",
        tags=["gguf", "gemma"],
    )

    # Update with new download count
    insert_or_update_model(
        conn=test_db,
        repo_id="lmstudio-community/gemma-4-E4B-it-GGUF",
        model_family="gemma",
        architecture="dense",
        base_parameter_count=4000000000,
        quantization="Q4_K_M",
        filename="gemma-4-E4B-it-Q4_K_M.gguf",
        file_size_bytes=5335290074,
        context_length=131072,
        license="MIT",
        downloads=2000000,  # Updated
        likes=60000,  # Updated
        last_modified="2026-06-30T00:00:00Z",
        tags=["gguf", "gemma"],
    )

    models = get_models(test_db, limit=10)
    assert len(models) == 1
    assert models[0]["downloads"] == 2000000
    assert models[0]["likes"] == 60000


def test_pagination(test_db: sqlite3.Connection) -> None:
    """Test pagination of model results."""
    for i in range(10):
        insert_or_update_model(
            conn=test_db,
            repo_id=f"test/model-{i}",
            model_family="test",
            architecture="dense",
            base_parameter_count=4000000000,
            quantization=f"Q{i}_K_M",
            filename=f"model-{i}.gguf",
            file_size_bytes=1000000000 * (i + 1),
            context_length=8192,
            license="MIT",
            downloads=1000 * (i + 1),
            likes=100 * (i + 1),
            last_modified="2026-06-30T00:00:00Z",
            tags=["gguf"],
        )

    # First page
    page1 = get_models(test_db, limit=5, offset=0)
    assert len(page1) == 5

    # Second page
    page2 = get_models(test_db, limit=5, offset=5)
    assert len(page2) == 5

    # Ensure different results
    page1_ids = {m["repo_id"] for m in page1}
    page2_ids = {m["repo_id"] for m in page2}
    assert page1_ids.isdisjoint(page2_ids)
