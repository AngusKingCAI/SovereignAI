# Troubleshooting

Common issues and how to fix them

## Installation Issues

### Install command fails (macOS / Linux / WSL)

If the install script fails to download:

1. Check your internet connection
2. Verify curl is installed: `which curl`
3. Try with verbose output: `curl -fsSL -v https://cli.devin.ai/install.sh | bash`

If you're behind a corporate proxy, you may need to configure proxy settings:
```bash
export https_proxy=http://your-proxy:port
curl -fsSL https://cli.devin.ai/install.sh | bash
```

### Install command fails (Windows)

If the PowerShell install script fails:

1. Check your internet connection
2. Ensure you are running PowerShell as a regular user (not as Administrator unless necessary)
3. If you see an execution policy error, try:
   ```powershell
   Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
   irm https://static.devin.ai/cli/setup.ps1 | iex
   ```
4. If you're behind a corporate proxy, configure proxy settings in PowerShell before running the install command

As an alternative to the PowerShell script, you can download and run the standalone installer directly:
- [x86_64](https://static.devin.ai/cli/devin-updater-x86_64-pc-windows.exe)
- [ARM64](https://static.devin.ai/cli/devin-updater-aarch64-pc-windows.exe)

### Permission denied during install

The installer needs write access to install the binary. If you see permission errors:

1. Check the install location has write permissions
2. Do not run the installer with `sudo` — this can cause ownership issues
3. If installing to a system directory, ensure your user has appropriate permissions

### Binary not found after install

If the install completes but `devin` isn't found:

**macOS / Linux / WSL:**
1. Restart your terminal or run `source ~/.bashrc` (or `~/.zshrc`)
2. Check if the binary location is in your PATH: `echo $PATH`
3. Verify the binary exists: `ls -la ~/.local/bin/devin` (or the install location shown during setup)

**Windows:**
1. Restart your PowerShell session
2. Check if the binary location is in your PATH: `$env:PATH -split ';'`
3. Verify the binary exists in the install location shown during setup

### 'irm' or 'iex' command not found (Windows)

`irm` and `iex` are PowerShell aliases. If you see this error, you're running the install command in Git Bash or CMD instead of PowerShell.

**Fix:** Open **PowerShell** and run the install command there:
```powershell
irm https://static.devin.ai/cli/setup.ps1 | iex
```

Alternatively, from Git Bash or CMD you can invoke PowerShell explicitly:
```bash
powershell -Command "irm https://static.devin.ai/cli/setup.ps1 | iex"
```

After installation, you can use Devin CLI from **PowerShell**, **Windows Terminal**, or **Git Bash**.

## Authentication Issues

### Login fails or times out

If browser-based login doesn't work:

1. Try the manual token flow for remote/SSH sessions:
   ```bash
   devin auth login --force-manual-token-flow
   ```
2. Check that your browser can reach the authentication URL
3. Verify your enterprise account has Devin CLI access enabled

### 'Not authorized' or permission errors

If you see authorization errors after logging in:

1. Verify your account has the correct permission needed to access Devin CLI. You may need to ask your admin.
2. Try logging out and back in: `devin auth logout && devin auth login`
3. Check your authentication status: `devin auth status`

### Token rejected or revoked

Devin CLI API tokens do not expire by default. If a stored token has been revoked or is no longer accepted, remove it before logging in again:
```bash
devin auth logout && devin auth login
```

## Network & Proxy Issues

### Connections fail behind a corporate proxy

The CLI routes its own outbound HTTPS traffic (authentication, updates, model API calls, MCP servers) through a proxy when one is configured. There are two ways to set it:

**Environment variables** — the default `system` proxy mode respects these:
```bash
export HTTPS_PROXY=http://proxy.corp.example.com:8080
export HTTP_PROXY=http://proxy.corp.example.com:8080
export ALL_PROXY=socks5://proxy.corp.example.com:1080   # optional, SOCKS5
export NO_PROXY=localhost,127.0.0.1,.internal.corp      # hosts to bypass
```

**`config.json`** — applies regardless of environment:
```json
{
  "proxy": {
    "mode": "manual",
    "url": "http://proxy.corp.example.com:8080",
    "no_proxy": "localhost,127.0.0.1,.internal.corp"
  }
}
```

If your proxy performs TLS inspection, the CLI uses your operating system's certificate store, so install the proxy's root CA at the OS level (Keychain on macOS, the Windows certificate store, or your distribution's CA bundle on Linux).

### Capture full HTTP request logs for debugging

To get full visibility into the request lifecycle (DNS, connection pooling, TLS handshake, headers, redirects, and retries), raise the log level with `RUST_LOG` and mirror logs to your terminal with `CHISEL_LOG_STDOUT`:

```bash
RUST_LOG="chisel=trace,windsurf_api_client=trace,connect_rpc=trace,reqwest=trace,hyper=trace,hyper_util=trace,rustls=trace" \
  CHISEL_LOG_STDOUT=1 \
  devin auth login
```

What each target adds:
- `chisel`, `windsurf_api_client`, `connect_rpc` — the CLI's own request and authentication logging
- `reqwest=trace` — high-level request/response and redirect handling
- `hyper=trace` / `hyper_util=trace` — connection establishment, pooling, and HTTP/1.1 & HTTP/2 framing
- `rustls=trace` — TLS handshake details (useful for proxy and certificate problems)

Use `CHISEL_LOG_STDERR=1` instead of `CHISEL_LOG_STDOUT=1` if you don't want logs interleaved with command output.

Logs are also always written to a per-run log file under the CLI's data directory, regardless of these env vars:
- **macOS / Linux:** `~/.local/share/devin/cli/logs/devin_<timestamp>_<pid>.log`
- **Windows:** `%APPDATA%\devin\cli\logs\devin_<timestamp>_<pid>.log`

**Warning**: Trace-level logs can include sensitive data such as `Authorization` headers and tokens. Scrub log output before sharing it.

### Inspect full request and response bodies

`RUST_LOG` exposes the request lifecycle but not full payloads. To capture complete request and response bodies, route the CLI through an intercepting proxy such as [mitmproxy](https://mitmproxy.org/):

```bash
# Terminal 1 — start the intercepting proxy:
mitmproxy --listen-port 8080

# Terminal 2 — point the CLI at it:
export HTTPS_PROXY=http://127.0.0.1:8080
devin auth login
```

Because the CLI trusts the OS certificate store, install mitmproxy's CA certificate (`~/.mitmproxy/mitmproxy-ca-cert.pem`) into your system trust store first — otherwise the TLS connection to the proxy will fail.

## Runtime Issues

### Model not available

If you see errors about a model not being available:

1. Check if your enterprise restricts available models in [Team Settings](../07-Enterprise/Team-Settings.md)
2. Verify the model name is correct (try `/model` to see available models)
3. Check your internet connection
4. Try switching to a different model

### Commands hang or timeout

If commands seem to hang:

1. Check if a background shell is still running (look for background shell IDs in output)
2. Try pressing `Ctrl+C` to cancel the current operation
3. Check your internet connection
4. Verify the command isn't waiting for input

### Session won't resume

If you can't resume a previous session:

1. Check that you're in the correct directory
2. Use `/ls` to list available sessions
3. Try starting a new session instead
4. Check that session files haven't been deleted