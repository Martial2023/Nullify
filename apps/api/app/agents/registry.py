"""Central registry for all AI security agents."""

from __future__ import annotations

import importlib
import pkgutil
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.agents.base import SecurityAgent


class AgentRegistry:
    """Manages all available security agents."""

    def __init__(self) -> None:
        self._agents: dict[str, SecurityAgent] = {}

    def register(self, agent: SecurityAgent) -> None:
        """Register an agent instance."""
        self._agents[agent.name] = agent

    def get(self, name: str) -> SecurityAgent | None:
        """Return agent by name, or ``None``."""
        return self._agents.get(name)

    def list_all(self) -> list[SecurityAgent]:
        """Return every registered agent."""
        return list(self._agents.values())

    # ── auto-discovery ────────────────────────────────────────
    def discover_and_register(self) -> None:
        """Scan all sub-modules of ``app.agents`` and register every
        concrete ``SecurityAgent`` subclass found."""
        import app.agents as agents_pkg
        from app.agents.base import SecurityAgent as _Base

        for _importer, modname, _ispkg in pkgutil.walk_packages(
            agents_pkg.__path__, prefix="app.agents.",
        ):
            try:
                importlib.import_module(modname)
            except Exception as exc:  # noqa: BLE001
                print(f"[AgentRegistry] Skipping {modname}: {exc}")

        def _all_subclasses(cls: type) -> set[type]:
            subs = set(cls.__subclasses__())
            for sub in list(subs):
                subs |= _all_subclasses(sub)
            return subs

        for cls in _all_subclasses(_Base):
            if getattr(cls, "__abstractmethods__", None):
                continue
            name = getattr(cls, "name", None)
            if not name or not isinstance(name, str):
                continue
            if name not in self._agents:
                try:
                    self._agents[name] = cls()
                except Exception as exc:  # noqa: BLE001
                    print(f"[AgentRegistry] Cannot instantiate {cls.__name__}: {exc}")


agent_registry = AgentRegistry()
