"""Central registry for all security tools."""

from __future__ import annotations

import importlib
import pkgutil
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.tools.base import SecurityTool


class ToolRegistry:
    """Manages all available security tools."""

    def __init__(self) -> None:
        self._tools: dict[str, SecurityTool] = {}

    def register(self, tool: SecurityTool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> SecurityTool | None:
        return self._tools.get(name)

    def get_by_names(self, names: list[str]) -> list[SecurityTool]:
        """Return tools matching the given names (skips unknown)."""
        return [self._tools[n] for n in names if n in self._tools]

    def list_available(self) -> list[SecurityTool]:
        return [t for t in self._tools.values() if t.is_available()]

    def list_all(self) -> list[SecurityTool]:
        return list(self._tools.values())

    def to_claude_tools(self, names: list[str] | None = None) -> list[dict]:
        """Tools in Claude tool_use format. Optionally filter by names."""
        tools = self.get_by_names(names) if names else self.list_available()
        return [t.to_claude_tool() for t in tools if t.is_available()]

    # ── auto-discovery ────────────────────────────────────────
    def discover_and_register(self) -> None:
        """Scan all sub-packages of ``app.tools`` and register every
        concrete ``SecurityTool`` subclass found."""
        import app.tools as tools_pkg
        from app.tools.base import SecurityTool as _Base

        for _importer, modname, _ispkg in pkgutil.walk_packages(
            tools_pkg.__path__, prefix="app.tools.",
        ):
            try:
                importlib.import_module(modname)
            except Exception as exc:  # noqa: BLE001
                print(f"[ToolRegistry] Skipping {modname}: {exc}")

        def _all_subclasses(cls: type) -> set[type]:
            subs = set(cls.__subclasses__())
            for sub in list(subs):
                subs |= _all_subclasses(sub)
            return subs

        for cls in _all_subclasses(_Base):
            if getattr(cls, "__abstractmethods__", None):
                continue
            # Must have a name set (not inherited placeholder)
            name = getattr(cls, "name", None)
            if not name or not isinstance(name, str):
                continue
            if name not in self._tools:
                try:
                    self._tools[name] = cls()
                except Exception as exc:  # noqa: BLE001
                    print(f"[ToolRegistry] Cannot instantiate {cls.__name__}: {exc}")


tool_registry = ToolRegistry()
