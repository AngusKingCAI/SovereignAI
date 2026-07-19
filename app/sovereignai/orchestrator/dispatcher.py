from __future__ import annotations

import re
import tomllib
from pathlib import Path

from sovereignai.shared.capability_api import CapabilityAPI
from sovereignai.shared.capability_graph import CapabilityGraph
from sovereignai.shared.task_state_machine import ITaskStateQuery, Task
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import (
    CapabilityCategory,
    ComponentId,
    TraceLevel,
)


class MessageDispatcher:

    def __init__(
        self,
        capability_api: CapabilityAPI,
        capability_graph: CapabilityGraph,
        task_state_machine: ITaskStateQuery,
        trace: TraceEmitter,
    ) -> None:
        self._api = capability_api
        self._graph = capability_graph
        self._tasks = task_state_machine
        self._trace = trace

    async def dispatch(self, message: str, token: str) -> Task:
        self._trace.emit(
            component="MessageDispatcher",
            level=TraceLevel.INFO,
            message=f"Received message: {message[:100]}{'...' if len(message) > 100 else ''}",
        )

        # Find matching skill by intent_keywords
        skill_id = self._find_matching_skill(message)

        # If no match, route to Ollama chat skill (catch-all per Finding 13)
        if skill_id is None:
            skill_id = ComponentId("ollama_adapter")
            capability_name = "chat_completion"
            self._trace.emit(
                component="MessageDispatcher",
                level=TraceLevel.DEBUG,
                message="No skill matched, routing to Ollama chat skill",
            )
        else:
            # Extract capability name from the skill's manifest
            capability_name = self._get_capability_name(skill_id)
            self._trace.emit(
                component="MessageDispatcher",
                level=TraceLevel.DEBUG,
                message=f"Matched skill {skill_id} for capability {capability_name}",
            )

        # Submit task via CapabilityAPI
        if skill_id == ComponentId("ollama_adapter"):
            category = CapabilityCategory.MODEL_INFERENCE
        else:
            category = CapabilityCategory.TOOL

        task_id = self._api.submit_task(
            token=token,
            category=category,
            capability_name=capability_name,
            payload=message,
        )

        # Retrieve and return the Task object
        task = self._tasks.list_tasks()[-1]  # Most recent task
        self._trace.emit(
            component="MessageDispatcher",
            level=TraceLevel.INFO,
            message=f"Submitted task {task_id} to {skill_id}",
        )
        return task

    def _find_matching_skill(self, message: str) -> ComponentId | None:
        # Get all registered components
        manifests = self._graph.list_all_components()

        # Filter to skills (TOOL category capabilities)
        skills = [
            manifest for manifest in manifests
            if any(cap.category == CapabilityCategory.TOOL for cap in manifest.provides)
        ]

        # Match using word-boundary regex against intent_keywords
        for skill in sorted(skills, key=lambda m: -max(cap.priority for cap in m.provides)):
            intent_keywords = self._get_intent_keywords(skill.component_id)
            if intent_keywords:
                for keyword in intent_keywords:
                    pattern = rf'\b{re.escape(keyword)}\b'
                    if re.search(pattern, message, re.IGNORECASE):
                        return skill.component_id

        return None

    def _get_intent_keywords(self, component_id: ComponentId) -> list[str]:
        # Try to find the manifest file
        for base_dir in [Path("skills/user"), Path("skills/external"), Path("adapters/external")]:
            manifest_path = base_dir / component_id / "manifest.toml"
            if manifest_path.exists():
                try:
                    with manifest_path.open("rb") as f:
                        data = tomllib.load(f)
                    keywords = data.get("intent_keywords", [])
                    if isinstance(keywords, list):
                        return [str(k) for k in keywords]
                except (tomllib.TOMLDecodeError, OSError) as e:
                    import logging
                    logging.getLogger(__name__).error(
                        f"Failed to read manifest {manifest_path}: {e}"
                    )
        return []

    def _get_capability_name(self, component_id: ComponentId) -> str:
        manifests = self._graph.list_all_components()
        for manifest in manifests:
            if manifest.component_id == component_id and manifest.provides:
                # Return the first capability name (primary capability)
                return str(manifest.provides[0].name)
        # Fallback for Ollama adapter
        if component_id == ComponentId("ollama_adapter"):
            return "chat_completion"
        raise ValueError(f"Component {component_id} not found in capability graph")
