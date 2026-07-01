from __future__ import annotations

import asyncio
import json
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
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
)
from web.schemas import (
    CapabilityResponseDTO,
    DatabaseResponseDTO,
    ServiceResponseDTO,
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


@app.get("/api/databases", dependencies=[Depends(get_current_user)])
async def get_databases(request: Request) -> list[DatabaseResponseDTO]:
    from sovereignai.shared.database_registry import DatabaseRegistry

    container: Any = request.app.state.container
    db_registry: Any = container.retrieve(DatabaseRegistry)

    database_names = db_registry.list_databases()
    dtos = []
    for db_name in database_names:
        try:
            provider = db_registry.get_database(db_name)
            status = provider.health_check()
            models = provider.list_models()
            dtos.append(
                DatabaseResponseDTO(
                    name=provider.name,
                    status="healthy" if status.available else "unhealthy",
                    models=[f"{m.org}/{m.family}" for m in models],
                )
            )
        except Exception as e:
            dtos.append(
                DatabaseResponseDTO(
                    name=db_name,
                    status=f"error: {str(e)}",
                    models=[],
                )
            )
    return dtos


@app.get("/api/services", dependencies=[Depends(get_current_user)])
async def get_services(request: Request) -> list[ServiceResponseDTO]:
    from sovereignai.shared.service_registry import ServiceRegistry

    container: Any = request.app.state.container
    service_registry: Any = container.retrieve(ServiceRegistry)

    service_names = service_registry.list_services()
    dtos = []
    for svc_name in service_names:
        provider = service_registry.get_service(svc_name)
        status = provider.health_check()
        dtos.append(
            ServiceResponseDTO(
                name=provider.name,
                status="running" if status.running else "stopped",
                pid=status.pid,
                port=status.port,
            )
        )
    return dtos


@app.get("/api/traces/history", dependencies=[Depends(get_current_user)])
async def get_traces_history(request: Request) -> list[TraceEventDTO]:
    container: Any = request.app.state.container
    trace: Any = container.retrieve(TraceEmitter)

    events = trace.recent_events()
    dtos = [
        TraceEventDTO(
            timestamp=event.timestamp.isoformat(),
            level=event.level.value,
            component=event.component,
            correlation_id=str(event.correlation_id),
            message=event.message,
        )
        for event in events
    ]
    return dtos


@app.get("/api/traces/stream")
async def get_traces_stream(request: Request) -> StreamingResponse:
    container: Any = request.app.state.container
    trace: Any = container.retrieve(TraceEmitter)
    auth: Any = container.retrieve(AuthMiddleware)
    token = get_session_token(request)

    try:
        auth.validate(token)
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid session token") from exc

    async def event_generator() -> AsyncGenerator[str, None]:
        import time

        events_queue: asyncio.Queue = asyncio.Queue()
        last_keepalive = time.time()

        def on_trace_event(event: Any) -> None:
            events_queue.put_nowait(event)

        unsubscribe = trace.subscribe_callback(on_trace_event)

        try:
            while True:
                if await request.is_disconnected():
                    break

                try:
                    event = await asyncio.wait_for(events_queue.get(), timeout=1.0)
                    dto = TraceEventDTO(
                        timestamp=event.timestamp.isoformat(),
                        level=event.level.value,
                        component=event.component,
                        correlation_id=str(event.correlation_id),
                        message=event.message,
                    )
                    data = json.dumps(dto.model_dump(mode='json'))
                    yield f"event: trace\ndata: {data}\n\n"
                    last_keepalive = time.time()
                except TimeoutError:
                    current_time = time.time()
                    if current_time - last_keepalive > 15:
                        yield ": keep-alive\n\n"
                        last_keepalive = current_time
        except asyncio.CancelledError:
            pass
        finally:
            unsubscribe()
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
