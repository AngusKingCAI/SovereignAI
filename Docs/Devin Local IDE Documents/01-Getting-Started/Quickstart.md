# Quickstart

Get up and running in 2 minutes with Devin CLI, a local command-line coding agent with deep Devin Cloud integration.

## Install Devin CLI

### macOS / Linux / WSL
```bash
curl -fsSL https://cli.devin.ai/install.sh | bash
```

### Homebrew
On macOS, install Devin CLI with Homebrew:

```bash
brew install --cask devin-cli
```

To upgrade to the latest version later:

```bash
brew upgrade --cask devin-cli
```

### Windows
Download and run the installer:

- [x86_64 (most Windows PCs)](https://static.devin.ai/cli/devin-updater-x86_64-pc-windows.exe)
- [ARM64 (Windows on ARM)](https://static.devin.ai/cli/devin-updater-aarch64-pc-windows.exe)

Alternatively, open **PowerShell** and run:

```powershell
irm https://static.devin.ai/cli/setup.ps1 | iex
```

**Note**: `irm` and `iex` are PowerShell commands. Do not run this in Git Bash or CMD — it will fail with "command not found". Use PowerShell for installation only.

After installing, you can use Devin CLI from **PowerShell**, **Windows Terminal**, or **Git Bash**.

### Devin Desktop
Devin CLI is bundled with **Devin Desktop**. This installation method is available for **Legacy Windsurf Enterprise** and **Devin Enterprise** plans.

**Admin setup:** For the Devin Desktop-bundled install, an admin must first enable the install option in Devin CLI team settings by toggling on **Show "Install Devin CLI" in the Devin Desktop Command Palette**.

**User installation:**

1. Open Devin Desktop
2. Open the Command Palette with `Cmd+Shift+P` (macOS) or `Ctrl+Shift+P` (Windows/Linux)
3. Search for and run **Install Devin CLI**

This adds the `devin` binary to your PATH so you can use it from any terminal.

## Start coding

That's it! After you restart your terminal, enter a project directory and type `devin` to activate Devin CLI. Also try preloading the session with a prompt for automation:

```bash
devin -- check out this code and suggest a feasible, helpful feature
```

You're ready to go. For must-know tips, see [Essential Commands](../02-Essential-Commands/).

## What's next?

Devin CLI can implement new features, fix bugs, review code, answer questions, automate tasks, and more.

- [Essential Commands](../02-Essential-Commands/) - Must-know commands and slash commands
- [Models](../03-Models/) - Choose the right model for your task
- [Extensibility](../04-Extensibility/) - Connect MCP servers and skills
- [Command Reference](../05-Reference/Commands.md) - Explore all commands and flags

## Devin CLI vs. Devin

Devin CLI and [Devin](https://app.devin.ai) are separate tools designed for different workflows.

**Devin CLI** is a local coding agent that runs directly in your terminal. It works with your local files and environment, giving you fast, interactive assistance right where you code.

**Devin** is our cloud-based AI software engineer that runs in a virtual machine. It includes features like Playbooks, Secrets, Knowledge, and other capabilities that are not available in Devin CLI.

**Note**: Devin CLI does not yet support Knowledge, Playbooks, or Secrets from your Devin account. We're actively working on adding support for each of these and plan to roll them out soon.