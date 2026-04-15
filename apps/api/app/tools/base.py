"""Base class for all security tools."""

import asyncio
import re
import shutil
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class ToolResult:
    """Result of a security tool execution."""

    success: bool
    output: str
    error: str | None = None
    findings: list[dict] = field(default_factory=list)


def _docker_available() -> bool:
    """Check if Docker daemon is running."""
    return shutil.which("docker") is not None


class SecurityTool(ABC):
    """Base class for security tool wrappers."""

    name: str
    description: str
    binary: str  # nom de l'exécutable (ex: "nmap")
    docker_image: str  # image Docker (ex: "projectdiscovery/httpx:latest")
    parameters: dict  # JSON Schema pour Claude tool_use

    def is_available(self) -> bool:
        """Tool is available if Docker is running or the binary is installed locally."""
        if _docker_available():
            return True
        return shutil.which(self.binary) is not None

    @abstractmethod
    def build_command(self, args: dict) -> list[str]:
        """Build the CLI command from arguments (without the binary name prefix)."""
        ...

    @abstractmethod
    def parse_output(self, raw_output: str) -> list[dict]:
        """Parse raw CLI output into structured findings."""
        ...

    # Extra CLI flags appended when running inside Docker
    # (e.g. ["-duc", "-nc"] for ProjectDiscovery tools).
    docker_extra_args: list[str] = []

    def _build_docker_command(self, tool_args: list[str]) -> list[str]:
        """Wrap tool arguments inside `docker run`.

        Docker images from ProjectDiscovery / instrumentisto have the tool
        binary as ENTRYPOINT, so we only pass the arguments.
        On Windows Docker Desktop, --network host doesn't work the same way,
        so we also add host.docker.internal mapping.
        """
        return [
            "docker", "run", "--rm",
            "--network", "host",
            "--add-host=host.docker.internal:host-gateway",
            self.docker_image,
            *tool_args,
            *self.docker_extra_args,
        ]

    @staticmethod
    def _rewrite_localhost_for_docker(args: dict) -> dict:
        """Replace localhost/127.0.0.1 references with host.docker.internal.

        On Windows/macOS Docker Desktop, containers can't reach the host's
        localhost directly — they must use host.docker.internal instead.
        """
        if sys.platform != "linux":
            patched = {}
            for k, v in args.items():
                if isinstance(v, str):
                    v = re.sub(
                        r"(https?://)?(localhost|127\.0\.0\.1)",
                        lambda m: (m.group(1) or "") + "host.docker.internal",
                        v,
                    )
                patched[k] = v
            return patched
        return args

    async def execute(self, args: dict, timeout: int = 120) -> ToolResult:
        """Execute the tool via Docker (preferred) or local binary."""
        use_docker = _docker_available()

        # Rewrite localhost targets when running inside Docker on Windows/macOS
        effective_args = self._rewrite_localhost_for_docker(args) if use_docker else args
        cmd = self.build_command(effective_args)

        if use_docker:
            # build_command returns [binary, ...args] — strip the binary
            # because Docker ENTRYPOINT already provides it.
            tool_args = cmd[1:] if cmd and cmd[0] == self.binary else cmd
            exec_cmd = self._build_docker_command(tool_args)
        elif shutil.which(self.binary):
            exec_cmd = cmd
        else:
            return ToolResult(
                success=False,
                output="",
                error=f"Tool '{self.binary}' is not available: Docker is not running and binary is not in PATH.",
            )

        try:
            proc = await asyncio.create_subprocess_exec(
                *exec_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            # Collect stdout lines as they arrive so we keep partial output
            # even if the process hangs (common with ProjectDiscovery tools).
            stdout_lines: list[str] = []
            stderr_lines: list[str] = []
            timed_out = False

            async def _read_stream(
                stream: asyncio.StreamReader | None, dest: list[str]
            ) -> None:
                if stream is None:
                    return
                while True:
                    line = await stream.readline()
                    if not line:
                        break
                    dest.append(line.decode(errors="replace"))

            try:
                await asyncio.wait_for(
                    asyncio.gather(
                        _read_stream(proc.stdout, stdout_lines),
                        _read_stream(proc.stderr, stderr_lines),
                    ),
                    timeout=timeout,
                )
                await proc.wait()
            except asyncio.TimeoutError:
                timed_out = True
                try:
                    proc.kill()
                    await proc.wait()
                except Exception:
                    pass

            raw = "".join(stdout_lines)
            err = "".join(stderr_lines)

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
            return ToolResult(success=False, output="", error=str(e))

    def to_claude_tool(self) -> dict:
        """Convert to Anthropic tool_use format."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.parameters,
        }
