"""Base class for all security tools — Docker-only execution."""

import asyncio
import shutil
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

TOOLS_IMAGE = "nullify-tools:latest"


@dataclass
class ToolResult:
    """Result of a security tool execution."""

    success: bool
    output: str
    error: str | None = None
    findings: list[dict] = field(default_factory=list)


def _docker_available() -> bool:
    """Check if the Docker CLI is reachable."""
    return shutil.which("docker") is not None


class SecurityTool(ABC):
    """Base class for security tool wrappers."""

    name: str
    description: str
    binary: str
    docker_image: str = TOOLS_IMAGE
    parameters: dict

    def is_available(self) -> bool:
        return _docker_available()

    @abstractmethod
    def build_command(self, args: dict) -> list[str]:
        """Build the full CLI command (binary included)."""
        ...

    @abstractmethod
    def parse_output(self, raw_output: str) -> list[dict]:
        """Parse raw CLI output into structured findings."""
        ...

    def _build_docker_command(self, cmd: list[str], container_name: str) -> list[str]:
        """Wrap a full command inside `docker run`."""
        return [
            "docker", "run", "--rm",
            "--network", "host",
            "--name", container_name,
            self.docker_image,
            *cmd,
        ]

    async def _kill_container(self, name: str) -> None:
        try:
            p = await asyncio.create_subprocess_exec(
                "docker", "kill", name,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            await asyncio.wait_for(p.wait(), timeout=10)
        except Exception:
            pass

    async def execute(self, args: dict, timeout: int = 120) -> ToolResult:
        """Execute the tool inside Docker."""
        if not _docker_available():
            return ToolResult(
                success=False, output="",
                error="Docker is not available on this system.",
            )

        cmd = self.build_command(args)
        container_name = f"nullify-{self.name}-{uuid.uuid4().hex[:8]}"
        exec_cmd = self._build_docker_command(cmd, container_name)

        print(f"[{self.name}] EXEC: {' '.join(exec_cmd)}")

        try:
            proc = await asyncio.create_subprocess_exec(
                *exec_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            timed_out = False
            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(), timeout=timeout
                )
            except asyncio.TimeoutError:
                timed_out = True
                await self._kill_container(container_name)
                try:
                    proc.kill()
                except Exception:
                    pass
                try:
                    stdout, stderr = await asyncio.wait_for(
                        proc.communicate(), timeout=5
                    )
                except Exception:
                    stdout, stderr = b"", b""

            raw = stdout.decode(errors="replace")
            err = stderr.decode(errors="replace")

            print(f"[{self.name}] DONE — timed_out={timed_out} returncode={proc.returncode} stdout={len(raw)}ch")
            if err.strip():
                print(f"[{self.name}] STDERR: {err[:200]}")

            if timed_out and not raw.strip():
                return ToolResult(
                    success=False, output="",
                    error=f"Tool execution timed out ({timeout}s).",
                )

            if proc.returncode != 0 and not raw.strip() and not timed_out:
                return ToolResult(success=False, output=raw, error=err)

            findings = self.parse_output(raw)
            return ToolResult(success=True, output=raw, findings=findings)

        except Exception as e:
            print(f"[{self.name}] EXCEPTION: {type(e).__name__}: {e}")
            await self._kill_container(container_name)
            return ToolResult(success=False, output="", error=str(e))

    def to_claude_tool(self) -> dict:
        """Convert to Anthropic tool_use format."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.parameters,
        }
