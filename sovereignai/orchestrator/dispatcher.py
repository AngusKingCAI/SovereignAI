"""MessageDispatcher for v1 natural language routing to skills.

Per OR56: This dispatcher queries the CapabilityGraph for registered skills
and routes to the first matching capability by priority order. It does NOT
perform intent parsing, disambiguation, or structured prompt construction —
those are CEO-shaped work deferred to a future plan.

The dispatcher uses simple word-boundary keyword matching against
intent_keywords from each skill's manifest. If no skill matches, it routes
to the Ollama chat skill (the catch-all for general conversation).
"""
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
    """Route natural language messages to skills via keyword matching.

    The dispatcher receives a message from the user, queries the
    CapabilityGraph for skills with matching intent_keywords, and submits
    a task via the CapabilityAPI. It returns immediately after submission
    — the caller polls the TaskStateMachine for completion.

    Per Finding 12 (Rev4): Uses word-boundary regex matching against
    intent_keywords from manifests, not substring or capability name matching.

    Per Finding 13 (Rev4): If no skill matches, routes to the Ollama chat
    skill (registered with intent_keywords for general conversation).
    """

    def __init__(
        self,
        capability_api: CapabilityAPI,
        capability_graph: CapabilityGraph,
        task_state_machine: ITaskStateQuery,
        trace: TraceEmitter,
    ) -> None:
        """Create a message dispatcher wired to the core capability system.

        Args:
            capability_api: Public API for submitting tasks.
            capability_graph: Index of registered components and capabilities.
            task_state_machine: Query interface for task state (used to
                retrieve the submitted Task object).
            trace: Trace emitter for logging routing decisions.
        """
        self._api = capability_api
        self._graph = capability_graph
        self._tasks = task_state_machine
        self._trace = trace

    async def dispatch(self, message: str, token: str) -> Task:
        """Route a natural language message to a matching skill and submit a task.

        The dispatcher queries the CapabilityGraph for skills, matches using
        word-boundary keyword matching against intent_keywords, and submits
        the task via CapabilityAPI.submit_task(). If no skill matches, it
        routes to the Ollama chat skill (the catch-all).

        Args:
            message: Natural language text from the user.
            token: Session token for CapabilityAPI authentication.

        Returns:
            Task object in RECEIVED state (retrieved from TaskStateMachine).

        Raises:
            AuthError: If the token is invalid (from CapabilityAPI).
            NoActiveProviderError: If no provider is registered (from CapabilityAPI).
        """
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
        """Query CapabilityGraph for skills and match using word-boundary keyword matching.

        Args:
            message: Natural language text from the user.

        Returns:
            ComponentId of the highest-priority matching skill, or None if no match.
        """
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
        """Extract intent_keywords from a component's manifest.toml file by reading raw TOML data.

        Since ComponentManifest doesn't store intent_keywords (shared/ is sacred),
        we read the raw TOML file directly. Skills are in skills/user/ or
        skills/external/; adapters are in adapters/external/.

        Args:
            component_id: The component to look up.

        Returns:
            List of intent_keywords, or empty list if not found.
        """
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
                except Exception:
                    # If we can't read the manifest, return empty list
                    pass
        return []

    def _get_capability_name(self, component_id: ComponentId) -> str:
        """Get the primary capability name for a component by querying the capability graph.

        For skills, this is the TOOL capability. For adapters, this is the
        MODEL_INFERENCE capability.

        Args:
            component_id: The component to look up.

        Returns:
            The capability name (e.g. "web_search", "chat_completion").
        """
        manifests = self._graph.list_all_components()
        for manifest in manifests:
            if manifest.component_id == component_id and manifest.provides:
                # Return the first capability name (primary capability)
                return manifest.provides[0].name
        # Fallback for Ollama adapter
        if component_id == ComponentId("ollama_adapter"):
            return "chat_completion"
        raise ValueError(f"Component {component_id} not found in capability graph")
