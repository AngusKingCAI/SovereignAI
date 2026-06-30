from __future__ import annotations

import asyncio
import json
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import JSONResponse, RedirectResponse, StreamingResponse

from sovereignai.main import build_container
from sovereignai.shared.auth import AuthMiddleware
from sovereignai.shared.capability_api import CapabilityAPI
from sovereignai.shared.capability_graph import ICapabilityIndex
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import (
    CapabilityCategory,
    TaskState,
    TaskStateChanged,
)
from web.schemas import (
    CapabilityResponseDTO,
    TaskResponseDTO,
    TaskSubmitDTO,
    TraceEventDTO,
)

# Per Finding 11 (Rev4): Multi-worker is NOT supported (in-memory auth + TraceEmitter state)
if os.environ.get("UVICORN_WORKERS", "1") != "1":
    raise RuntimeError("SovereignAI requires --workers 1 (in-memory state)")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup
    container = build_container()
    app.state.container = container
    yield
    # Shutdown (no-op for now)


app = FastAPI(lifespan=lifespan)

# Static files and templates
app.mount("/static", StaticFiles(directory="web/static"), name="static")
templates = Jinja2Templates(directory="web/templates")


@app.middleware("http")
async def first_run_redirect(request: Request, call_next: Any) -> Response:
    path = request.url.path
    if (
        path.startswith("/static/")
        or path in ("/login", "/register")
        or path.startswith("/api/auth/")
    ):
        return await call_next(request)  # type: ignore[no-any-return]

    container: Any = request.app.state.container
    auth: Any = container.retrieve(AuthMiddleware)
    if len(auth._password_hashes) == 0:
        if path.startswith("/api/"):
            # Return JSONResponse directly — raising HTTPException inside BaseHTTPMiddleware
            # gets swallowed by Starlette and turned into a 500. The frontend's auth check
            # (app.js) expects a clean 401 JSON response.
            return JSONResponse(
                status_code=401,
                content={"detail": "No user registered — complete first-run setup"},
            )
        return RedirectResponse(url="/register")  # type: ignore[no-any-return]

    return await call_next(request)  # type: ignore[no-any-return]


def get_session_token(request: Request) -> str:
    token = request.cookies.get("session_id")
    if not token:
        raise HTTPException(status_code=401, detail="No session cookie")
    return token


async def get_current_user(request: Request) -> Any:
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    container: Any = request.app.state.container
    auth: Any = container.retrieve(AuthMiddleware)
    try:
        user = auth.validate(session_id)
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired session") from exc
    return user


@app.get("/")
async def get_index(request: Request) -> Response:
    return templates.TemplateResponse(request, "index.html")


@app.post("/api/auth/login")
async def login(request: Request, response: Response) -> dict:
    data = await request.json()
    container: Any = request.app.state.container
    auth: Any = container.retrieve(AuthMiddleware)
    try:
        session = auth.login(data["username"], data["password"])
        response.set_cookie(
            key="session_id",
            value=session.token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=86400,
        )
        return {"status": "authenticated"}
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid credentials") from exc


@app.post("/api/auth/logout")
async def logout(response: Response) -> dict:
    response.delete_cookie(key="session_id")
    return {"status": "logged_out"}


@app.post("/api/auth/register")
async def register(request: Request) -> dict:
    data = await request.json()
    container: Any = request.app.state.container
    auth: Any = container.retrieve(AuthMiddleware)
    if len(auth._password_hashes) > 0:
        raise HTTPException(status_code=403, detail="Registration closed — user already exists")
    try:
        auth.register_user(data["username"], data["password"])
    except ValueError as exc:
        raise HTTPException(
            status_code=403, detail="Registration closed — user already exists"
        ) from exc
    return {"status": "created"}


@app.get("/login")
async def login_page(request: Request) -> Response:
    return templates.TemplateResponse(request, "login.html")


@app.get("/register")
async def register_page(request: Request) -> Response:
    container: Any = request.app.state.container
    auth: Any = container.retrieve(AuthMiddleware)
    if len(auth._password_hashes) > 0:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(request, "register.html")


@app.get("/api/auth/status")
async def auth_status(request: Request) -> dict:
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    container: Any = request.app.state.container
    auth: Any = container.retrieve(AuthMiddleware)
    try:
        user = auth.validate(session_id)
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired session") from exc
    return {"username": user.username}


@app.get("/api/capabilities", dependencies=[Depends(get_current_user)])
async def get_capabilities(request: Request) -> list[CapabilityResponseDTO]:
    container: Any = request.app.state.container
    capability_index: Any = container.retrieve(ICapabilityIndex)  # type: ignore[type-abstract]
    manifests = capability_index.list_all_components()

    dtos = []
    for manifest in manifests:
        for cap in manifest.provides:
            dtos.append(
                CapabilityResponseDTO(
                    id=manifest.component_id,
                    name=cap.name,
                    category=cap.category.value,
                    description=f"{manifest.component_id} v{manifest.version}",
                    priority=cap.priority,
                    input_schema=None,
                    output_schema=None,
                )
            )
    return dtos


@app.get("/api/workers", dependencies=[Depends(get_current_user)])
async def get_workers(request: Request) -> list[dict]:
    container: Any = request.app.state.container
    capability_index: Any = container.retrieve(ICapabilityIndex)  # type: ignore[type-abstract]
    components = capability_index.list_all_components()

    return [
        {
            "id": str(c.component_id),
            "name": c.version,
            "category": c.provides[0].category.value if c.provides else "unknown",
        }
        for c in components
    ]


@app.get("/api/tasks", dependencies=[Depends(get_current_user)])
async def get_tasks(request: Request) -> list[TaskResponseDTO]:
    from sovereignai.shared.task_state_machine import ITaskStateQuery

    container: Any = request.app.state.container
    task_state_query: Any = container.retrieve(ITaskStateQuery)  # type: ignore[type-abstract]
    tasks = task_state_query.list_tasks()

    dtos: list[TaskResponseDTO] = []
    for t in tasks:
        state = task_state_query.get_state(t.task_id)
        state_str = state.value if state is not None else "unknown"
        dtos.append(
            TaskResponseDTO(
                task_id=str(t.task_id),
                state=state_str,
                result=None,   # v1: no result storage yet
                error=None,    # v1: no error storage yet
            )
        )
    return dtos


@app.post("/api/tasks", dependencies=[Depends(get_current_user)])
async def post_task(
    request: Request,
    task_dto: TaskSubmitDTO,
) -> TaskResponseDTO:
    container: Any = request.app.state.container
    api: Any = container.retrieve(CapabilityAPI)
    token = get_session_token(request)

    try:
        category = CapabilityCategory(task_dto.category)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category: {task_dto.category}"
        ) from exc

    try:
        task_id = api.submit_task(
            token=token,
            category=category,
            capability_name=task_dto.capability_name,
            payload=task_dto.payload,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return TaskResponseDTO(
        task_id=str(task_id),
        state=TaskState.RECEIVED.value,
        result=None,
        error=None,
    )


@app.get("/api/tasks/{task_id}", dependencies=[Depends(get_current_user)])
async def get_task(request: Request, task_id: str) -> TaskResponseDTO:
    container: Any = request.app.state.container
    api: Any = container.retrieve(CapabilityAPI)
    token = get_session_token(request)

    from uuid import UUID

    try:
        task_uuid = UUID(task_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid task ID format") from exc

    state = api.get_task_state(token, task_uuid)
    if state is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return TaskResponseDTO(
        task_id=task_id,
        state=state.value,
        result=None,
        error=None,
    )


@app.post("/api/dispatch", dependencies=[Depends(get_current_user)])
async def dispatch(request: Request) -> TaskResponseDTO:
    from sovereignai.shared.capability_api import CapabilityAPI
    from sovereignai.shared.task_state_machine import ITaskStateQuery

    container: Any = request.app.state.container
    capability_api: Any = container.retrieve(CapabilityAPI)
    task_state_query: Any = container.retrieve(ITaskStateQuery)  # type: ignore[type-abstract]
    token = get_session_token(request)

    data = await request.json()
    message = data.get("message", "")

    try:
        task_id = capability_api.submit_task(
            token=token,
            category=CapabilityCategory.TOOL,
            capability_name="web_search",
            payload=message,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    # Retrieve the task state from the state machine
    state = task_state_query.get_state(task_id)
    if state is None:
        state = TaskState.RECEIVED

    return TaskResponseDTO(
        task_id=str(task_id),
        state=state.value,
        result=None,
        error=None,
    )


@app.get("/api/hardware", dependencies=[Depends(get_current_user)])
async def get_hardware(request: Request) -> dict:
    from web.hardware_probe import HardwareProbe

    probe = HardwareProbe()
    info = await probe.probe_async()

    return {
        "cpu_count": info.cpu_count,
        "cpu_freq_mhz": info.cpu_freq_mhz,
        "ram_total_mb": info.ram_total_mb,
        "ram_available_mb": info.ram_available_mb,
        "gpu_name": info.gpu_name,
        "gpu_vram_mb": info.gpu_vram_mb,
    }


@app.get("/api/traces/stream")
async def get_traces_stream(request: Request) -> StreamingResponse:
    container: Any = request.app.state.container
    trace: Any = container.retrieve(TraceEmitter)
    auth: Any = container.retrieve(AuthMiddleware)
    token = get_session_token(request)

    # Validate token
    try:
        auth.validate(token)
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid session token") from exc

    async def event_generator() -> AsyncGenerator[str, None]:
        from datetime import UTC
        last_timestamp = datetime.min.replace(tzinfo=UTC)
        sequence = 0
        queue_max = 1000
        queue: list[str] = []
        last_queue_check = datetime.now()

        # Subscribe to task state changes
        task_state_queue: asyncio.Queue[TaskStateChanged] = asyncio.Queue()

        def on_task_state(event: TaskStateChanged) -> None:
            task_state_queue.put_nowait(event)

        # Subscribe to the event bus (simplified - in a real implementation,
        # we'd need to properly manage the subscription lifecycle)
        # For now, we'll poll the trace emitter only

        try:
            while True:
                # Poll for trace events every 100ms
                await asyncio.sleep(0.1)

                # Check queue timeout (60 seconds)
                if (datetime.now() - last_queue_check).total_seconds() > 60:
                    if queue:
                        # Client not consuming - close connection
                        break
                    last_queue_check = datetime.now()

                # Get new trace events
                events = trace.get_events()
                new_events = [e for e in events if e.timestamp > last_timestamp]

                if new_events:
                    last_timestamp = max(e.timestamp for e in new_events)

                    for event in new_events:
                        # Check backpressure
                        if len(queue) >= queue_max:
                            # Send gap marker
                            gap_data = json.dumps({"dropped": len(queue)})
                            yield f"event: gap\ndata: {gap_data}\n\n"
                            queue.clear()

                        dto = TraceEventDTO(
                            sequence=sequence,
                            timestamp=event.timestamp.isoformat(),
                            level=event.level.value,
                            component=event.component,
                            message=event.message,
                            trace_id=str(event.correlation_id),
                            task_id=None,
                        )
                        data = json.dumps(dto.model_dump())
                        yield f"id: {sequence}\nevent: message\ndata: {data}\n\n"
                        sequence += 1
                        queue.append(data)
                        last_queue_check = datetime.now()

                # Check for task state changes
                try:
                    while True:
                        task_event = task_state_queue.get_nowait()
                        task_data = json.dumps(
                            {
                                "task_id": str(task_event.task_id),
                                "old_state": task_event.old_state.value,
                                "new_state": task_event.new_state.value,
                            }
                        )
                        yield f"id: {sequence}\nevent: task_state\ndata: {task_data}\n\n"
                        sequence += 1
                        queue.append(task_data)
                        last_queue_check = datetime.now()
                except asyncio.QueueEmpty:
                    pass

                # Yield keepalive if no new events
                if not new_events and task_state_queue.empty():
                    yield ": keepalive\n\n"

        except asyncio.CancelledError:
            # Client disconnected
            pass

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
