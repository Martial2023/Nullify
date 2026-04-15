"""Central registry for all security tools."""

from app.tools.base import SecurityTool


class ToolRegistry:
    """Manages all available security tools."""

    def __init__(self) -> None:
        self._tools: dict[str, SecurityTool] = {}

    def register(self, tool: SecurityTool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> SecurityTool | None:
        return self._tools.get(name)

    def list_available(self) -> list[SecurityTool]:
        return [t for t in self._tools.values() if t.is_available()]

    def list_all(self) -> list[SecurityTool]:
        return list(self._tools.values())

    def to_claude_tools(self) -> list[dict]:
        """All available tools in Claude tool_use format."""
        return [t.to_claude_tool() for t in self.list_available()]


tool_registry = ToolRegistry()
