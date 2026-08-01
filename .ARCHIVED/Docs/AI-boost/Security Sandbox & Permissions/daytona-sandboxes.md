# Daytona Sandboxes

**Source:** https://www.daytona.io/docs/en/sandboxes/

## Overview
Daytona provides full composable computers — sandboxes — for AI agents. Sandboxes are isolated runtime environments you can manage programmatically to run code. Each sandbox runs in isolation, giving it a dedicated kernel, filesystem, network stack, and allocated vCPU, RAM, and disk.

## Sandbox Types

### Container (Default)
Linux container runtime for running processes and executing code with dynamic builds and Docker images.

### Linux VM
Linux OS runtime in a virtual machine for running Linux-specific tools and workflows. Supports fork, pause/resume, and memory snapshots.

### Windows
Windows OS runtime in a virtual machine for running Windows applications and tooling. Supports fork, pause/resume, and memory snapshots.

### GPU
NVIDIA GPU runtime for model inference, fine-tuning, and CUDA-accelerated compute. Supports H100/H200 RTX with ephemeral capability.

## Available Snapshots

### Container Snapshots
- `daytona-small`: 1 vCPU, 1GiB memory, 3GiB storage
- `daytona-medium`: 2 vCPU, 4GiB memory, 8GiB storage
- `daytona-large`: 4 vCPU, 8GiB memory, 10GiB storage
- `daytona-gpu`: 1 vCPU, 1GiB memory, 1GiB storage, 1 GPU

### Linux VM Snapshots
- `daytona-vm-small`: 1 vCPU, 1GiB memory, 3GiB storage
- `daytona-vm-medium`: 2 vCPU, 4GiB memory, 8GiB storage
- `daytona-vm-large`: 4 vCPU, 8GiB memory, 10GiB storage

### Windows Snapshots
- `windows-small`: 1 vCPU, 4GiB memory, 30GiB storage
- `windows-medium`: 2 vCPU, 8GiB memory, 50GiB storage
- `windows-large`: 4 vCPU, 16GiB memory, 50GiB storage

## Key Features

### Agent Tools
- File System operations
- Git Operations
- Language Server Protocol
- Process & Code Execution
- Pseudo Terminal (PTY)
- Log Streaming
- MCP Server
- Computer Use
- Agent Skills

### Human Tools
- Web Terminal
- SSH Access
- VNC Access
- VPN Connections
- Preview
- Custom Preview Proxy
- Playground

### System Tools
- Webhooks
- Network Limits

### Security
- Secrets management
- Audit Logs

### Lifecycle Management
- Auto-stop interval
- Auto-pause interval
- Auto-archive interval
- Auto-delete interval
- Wall-clock TTL
- Update sandbox last activity
- Running indefinitely

## SDK Support
Daytona provides SDKs for multiple languages:
- Python
- TypeScript
- Ruby
- Go
- Java
- CLI
- REST API

## Use Cases
- AI agent execution environments
- Development environments
- Testing and validation
- GPU-accelerated compute
- Windows-specific workflows
- Model inference and fine-tuning
