# E2B JavaScript SDK Sandbox Reference

**Source URL:** https://e2b.dev/docs/sdk-reference/js-sdk/v2.27.0/sandbox

> ## Documentation Index
> Fetch the complete documentation index at: https://e2b.mintlify.site/llms.txt
> Use this file to discover all available pages before exploring further.

# Sandbox

### Sandbox

E2B cloud sandbox is a secure and isolated cloud environment.

The sandbox allows you to:

* Access Linux OS
* Create, list, and delete files and directories
* Run commands
* Run git operations
* Run isolated code
* Access the internet

Check docs here.

Use Sandbox.create to create a new sandbox.

#### Example

```ts
import { Sandbox } from 'e2b'

const sandbox = await Sandbox.create()
```

#### Properties

| Property                                            | Modifier   | Type         | Description                                                                         |
| --------------------------------------------------- | ---------- | ------------ | ----------------------------------------------------------------------------------- |
| `commands`                      | `readonly` | `Commands`   | Module for running commands in the sandbox                                          |
| `files`                            | `readonly` | `Filesystem` | Module for interacting with the sandbox filesystem                                  |
| `git`                                | `readonly` | `Git`        | Module for running git operations in the sandbox                                    |
| `pty`                                | `readonly` | `Pty`        | Module for interacting with the sandbox pseudo-terminals                            |
| `sandboxDomain`            | `readonly` | `string`     | Domain where the sandbox is hosted.                                                 |
| `sandboxId`                    | `readonly` | `string`     | Unique identifier of the sandbox.                                                   |
| `trafficAccessToken?` | `readonly` | `string`     | Traffic access token for accessing sandbox services with restricted public traffic. |

#### Methods

### ~~betaPause()~~

```ts
betaPause(opts?: ConnectionOpts): Promise<boolean>
```

###### Parameters

| Parameter | Type             |
| --------- | ---------------- |
| `opts`?   | `ConnectionOpts` |

###### Returns

`Promise`\<`boolean`>

###### Deprecated

Use Sandbox.pause instead.

### connect()

```ts
connect(opts?: SandboxConnectOpts): Promise<Sandbox>
```

Connect to a sandbox. If the sandbox is paused, it will be automatically resumed.
Sandbox must be either running or be paused.

With sandbox ID you can connect to the same sandbox from different places or environments (serverless functions, etc).

###### Parameters

| Parameter | Type                 | Description         |
| --------- | -------------------- | ------------------- |
| `opts`?   | `SandboxConnectOpts` | connection options. |

###### Returns

`Promise`\<`Sandbox`>

A running sandbox instance

###### Example

```ts
const sandbox = await Sandbox.create()
await sandbox.betaPause()

// Connect to the same sandbox.
const sameSandbox = await sandbox.connect()
```

### createSnapshot()

```ts
createSnapshot(opts?: CreateSnapshotOpts): Promise<SnapshotInfo>
```

Create a snapshot of the sandbox's current state.

The sandbox will be paused while the snapshot is being created.
The snapshot can be used to create new sandboxes with the same filesystem and state.
Snapshots are persistent and survive sandbox deletion.

Use the returned `snapshotId` with `Sandbox.create(snapshotId)` to create a new sandbox from the snapshot.

###### Parameters

| Parameter | Type                 | Description                                                               |
| --------- | -------------------- | ------------------------------------------------------------------------- |
| `opts`?   | `CreateSnapshotOpts` | snapshot creation options including optional name and connection options. |

###### Returns

`Promise`\<`SnapshotInfo`>

snapshot information including the snapshot ID.

###### Example

```ts
const sandbox = await Sandbox.create()
await sandbox.files.write('/app/state.json', '{"step": 1}')

// Create a snapshot
const snapshot = await sandbox.createSnapshot({ name: 'my-snapshot' })

// Create a new sandbox from the snapshot
const newSandbox = await Sandbox.create(snapshot.snapshotId)
```

### downloadUrl()

```ts
downloadUrl(path: string, opts?: SandboxUrlOpts): Promise<string>
```

Get the URL to download a file from the sandbox.

###### Parameters

| Parameter | Type             | Description                      |
| --------- | ---------------- | -------------------------------- |
| `path`    | `string`         | path to the file in the sandbox. |
| `opts`?   | `SandboxUrlOpts` | download url options.            |

###### Returns

`Promise`\<`string`>

URL for downloading file.

### getHost()

```ts
getHost(port: number): string
```

Get the host address for the specified sandbox port.
You can then use this address to connect to the sandbox port from outside the sandbox via HTTP or WebSocket.

###### Parameters

| Parameter | Type     | Description                        |
| --------- | -------- | ---------------------------------- |
| `port`    | `number` | number of the port in the sandbox. |

###### Returns

`string`

host address of the sandbox port.

###### Example

```ts
const sandbox = await Sandbox.create()
// Start an HTTP server
await sandbox.commands.exec('python3 -m http.server 3000')
// Get the hostname of the HTTP server
const serverURL = sandbox.getHost(3000)
```

### getInfo()

```ts
getInfo(opts?: Pick<SandboxOpts, "signal" | "requestTimeoutMs">): Promise<SandboxInfo>
```

Get sandbox information like sandbox ID, template, metadata, started at/end at date.

###### Parameters

| Parameter | Type                                                       | Description         |
| --------- | ---------------------------------------------------------- | ------------------- |
| `opts`?   | `Pick`\<`SandboxOpts`, `"signal"` \| `"requestTimeoutMs"`> | connection options. |

###### Returns

`Promise`\<`SandboxInfo`>

information about the sandbox

### getMcpToken()

```ts
getMcpToken(): Promise<undefined | string>
```

Get the MCP token for the sandbox.

###### Returns

`Promise`\<`undefined` | `string`>

MCP token for the sandbox, or undefined if MCP is not enabled.

### getMcpUrl()

```ts
getMcpUrl(): string
```

Get the MCP URL for the sandbox.

###### Returns

`string`

MCP URL for the sandbox.

### getMetrics()

```ts
getMetrics(opts?: SandboxMetricsOpts): Promise<SandboxMetrics[]>
```

Get the metrics of the sandbox.

###### Parameters

| Parameter | Type                 | Description         |
| --------- | -------------------- | ------------------- |
| `opts`?   | `SandboxMetricsOpts` | connection options. |

###### Returns

`Promise`\<`SandboxMetrics`\[]>

List of sandbox metrics containing CPU, memory and disk usage information.

### isRunning()

```ts
isRunning(opts?: Pick<ConnectionOpts, "signal" | "requestTimeoutMs">): Promise<boolean>
```

Check if the sandbox is running.

###### Parameters

| Parameter | Type                                                          |
| --------- | ------------------------------------------------------------- |
| `opts`?   | `Pick`\<`ConnectionOpts`, `"signal"` \| `"requestTimeoutMs"`> |

###### Returns

`Promise`\<`boolean`>

`true` if the sandbox is running, `false` otherwise.

###### Example

```ts
const sandbox = await Sandbox.create()
await sandbox.isRunning() // Returns true

await sandbox.kill()
await sandbox.isRunning() // Returns false
```

### kill()

```ts
kill(opts?: Pick<SandboxOpts, "signal" | "requestTimeoutMs">): Promise<void>
```

Kill the sandbox.

###### Parameters

| Parameter | Type                                                       | Description         |
| --------- | ---------------------------------------------------------- | ------------------- |
| `opts`?   | `Pick`\<`SandboxOpts`, `"signal"` \| `"requestTimeoutMs"`> | connection options. |

###### Returns

`Promise`\<`void`>

### listSnapshots()

```ts
listSnapshots(opts?: Omit<SnapshotListOpts, "sandboxId">): SnapshotPaginator
```

List all snapshots created from this sandbox.

###### Parameters

| Parameter | Type                                       | Description   |
| --------- | ------------------------------------------ | ------------- |
| `opts`?   | `Omit`\<`SnapshotListOpts`, `"sandboxId"`> | list options. |

###### Returns

`SnapshotPaginator`

paginator for listing snapshots from this sandbox.

### pause()

```ts
pause(opts?: Pick<SandboxOpts, "signal" | "requestTimeoutMs">): Promise<void>
```

Pause the sandbox.

Pause a running sandbox to stop billing and save the state for later resumption.
You can resume a paused sandbox using `Sandbox.connect()`.

###### Parameters

| Parameter | Type                                                       | Description         |
| --------- | ---------------------------------------------------------- | ------------------- |
| `opts`?   | `Pick`\<`SandboxOpts`, `"signal"` \| `"requestTimeoutMs"`> | connection options. |

###### Returns

`Promise`\<`void`>

### reconnect()

```ts
reconnect(opts?: SandboxConnectOpts): Promise<Sandbox>
```

Reconnect to the sandbox.

This method will disconnect and then reconnect to the sandbox.

###### Parameters

| Parameter | Type                 | Description         |
| --------- | -------------------- | ------------------- |
| `opts`?   | `SandboxConnectOpts` | connection options. |

###### Returns

`Promise`\<`Sandbox`>

### resume()

```ts
resume(opts?: Pick<SandboxOpts, "signal" | "requestTimeoutMs">): Promise<void>
```

Resume a paused sandbox.

###### Parameters

| Parameter | Type                                                       | Description         |
| --------- | ---------------------------------------------------------- | ------------------- |
| `opts`?   | `Pick`\<`SandboxOpts`, `"signal"` \| `"requestTimeoutMs"`> | connection options. |

###### Returns

`Promise`\<`void`>

### static create()

```ts
static create(opts?: SandboxOpts): Promise<Sandbox>
```

Create a new sandbox.

###### Parameters

| Parameter | Type           | Description                 |
| --------- | -------------- | --------------------------- |
| `opts`?   | `SandboxOpts`  | sandbox creation options.   |

###### Returns

`Promise`\<`Sandbox`>

A new sandbox instance

###### Example

```ts
const sandbox = await Sandbox.create()
```

### static reconnect()

```ts
static reconnect(sandboxID: string, opts?: SandboxConnectOpts): Promise<Sandbox>
```

Reconnect to a sandbox by ID.

This method will disconnect and then reconnect to the sandbox.

###### Parameters

| Parameter  | Type                 | Description         |
| ---------- | -------------------- | ------------------- |
| `sandboxID`| `string`             | ID of the sandbox.  |
| `opts`?    | `SandboxConnectOpts` | connection options. |

###### Returns

`Promise`\<`Sandbox`>

### uploadUrl()

```ts
uploadUrl(path: string, opts?: SandboxUrlOpts): Promise<string>
```

Get the URL to upload a file to the sandbox.

###### Parameters

| Parameter | Type             | Description                      |
| --------- | ---------------- | -------------------------------- |
| `path`    | `string`         | path to the file in the sandbox. |
| `opts`?   | `SandboxUrlOpts` | upload url options.              |

###### Returns

`Promise`\<`string`>

URL for uploading file.

This reference provides comprehensive API documentation for the E2B JavaScript SDK's Sandbox class, covering all methods and properties for managing secure cloud sandbox environments.
