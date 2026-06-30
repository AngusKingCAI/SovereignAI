"""CLI interface for Ollama service management."""
import json

import click

from sovereignai.services.ollama.service import OllamaService
from sovereignai.shared.trace_emitter import TraceEmitter


@click.group()
def ollama() -> None:
    """Ollama service management commands."""
    pass


@ollama.command()
def status() -> None:
    """Get the current status of Ollama."""
    trace = TraceEmitter()
    service = OllamaService(trace)
    status = service.status()

    output = {
        "installed": status.installed,
        "running": status.running,
        "version": status.version,
        "pid": status.pid,
        "error": status.error,
    }
    click.echo(json.dumps(output, indent=2))


@ollama.command()
def download() -> None:
    """Download and install Ollama."""
    trace = TraceEmitter()
    service = OllamaService(trace)
    service.download()
    click.echo("Ollama downloaded successfully")


@ollama.command()
def update() -> None:
    """Update Ollama to the latest version."""
    trace = TraceEmitter()
    service = OllamaService(trace)
    service.update()
    click.echo("Ollama updated successfully")


@ollama.command()
def uninstall() -> None:
    """Uninstall Ollama."""
    trace = TraceEmitter()
    service = OllamaService(trace)
    service.uninstall()
    click.echo("Ollama uninstalled successfully")


@ollama.command()
def start() -> None:
    """Start the Ollama service."""
    trace = TraceEmitter()
    service = OllamaService(trace)
    service.start()
    click.echo("Ollama started successfully")


@ollama.command()
def stop() -> None:
    """Stop the Ollama service."""
    trace = TraceEmitter()
    service = OllamaService(trace)
    service.stop()
    click.echo("Ollama stopped successfully")


@ollama.command()
def restart() -> None:
    """Restart the Ollama service."""
    trace = TraceEmitter()
    service = OllamaService(trace)
    service.restart()
    click.echo("Ollama restarted successfully")


if __name__ == "__main__":
    ollama()
