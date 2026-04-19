"""Base class for all AI security agents."""

from __future__ import annotations

from abc import ABC


class SecurityAgent(ABC):
    """Abstract base for every Nullify agent.

    Subclasses must set *name*, *description*, and *system_prompt* as class
    attributes and may override ``get_tools()`` to restrict which tools the
    agent is allowed to call (an empty list means "all available tools").
    """

    name: str
    description: str
    system_prompt: str

    def get_tools(self) -> list[str]:
        """Return the list of tool names this agent can use.

        An empty list means the agent has access to **all** registered tools.
        Subclasses override this to restrict the tool set.
        """
        return []

    def get_system_prompt(self, context: dict | None = None) -> str:
        """Build the final system prompt, optionally enriched with runtime
        context (target info, project scope, previous findings, etc.).
        """
        prompt = self.system_prompt
        if context:
            parts: list[str] = [prompt, "\n\n--- Runtime Context ---"]
            for key, value in context.items():
                parts.append(f"{key}: {value}")
            return "\n".join(parts)
        return prompt

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name!r}>"
