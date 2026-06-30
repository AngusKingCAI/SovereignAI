"""CLI interface for HuggingFace database management."""
import json

import click

from sovereignai.databases.huggingface.database import HuggingFaceDatabase
from sovereignai.shared.trace_emitter import TraceEmitter


@click.group()
def huggingface() -> None:
    """HuggingFace database management commands."""
    pass


@huggingface.command()
def status() -> None:
    """Get the current status of the HuggingFace database."""
    trace = TraceEmitter()
    db = HuggingFaceDatabase(trace)
    status = db.status()

    output = {
        "installed": status.installed,
        "size_bytes": status.size_bytes,
        "last_updated": status.last_updated,
        "model_count": status.model_count,
        "error": status.error,
    }
    click.echo(json.dumps(output, indent=2))


@huggingface.command()
def download() -> None:
    """Download and install the HuggingFace database."""
    trace = TraceEmitter()
    db = HuggingFaceDatabase(trace)
    db.download()
    click.echo("HuggingFace database downloaded successfully")


@huggingface.command()
def update() -> None:
    """Update the HuggingFace database to the latest version."""
    trace = TraceEmitter()
    db = HuggingFaceDatabase(trace)
    db.update()
    click.echo("HuggingFace database updated successfully")


@huggingface.command()
def uninstall() -> None:
    """Uninstall the HuggingFace database."""
    trace = TraceEmitter()
    db = HuggingFaceDatabase(trace)
    db.uninstall()
    click.echo("HuggingFace database uninstalled successfully")


if __name__ == "__main__":
    huggingface()
