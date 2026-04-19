"""Debugger tools."""

from app.tools.base import SecurityTool

BINARY_IMAGE = "nullify-tools-binary:latest"


class GdbTool(SecurityTool):
    name = "gdb_analyze"
    description = (
        "GNU Debugger — analyze binaries, inspect memory, set breakpoints. "
        "Use for binary analysis and exploit development."
    )
    binary = "gdb"
    docker_image = BINARY_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "binary_path": {"type": "string", "description": "Path to the binary to analyze."},
            "commands": {"type": "string", "description": "GDB commands to execute (semicolon-separated)."},
            "core_file": {"type": "string", "description": "Core dump file path."},
        },
        "required": ["binary_path"],
    }

    def build_command(self, args: dict) -> list[str]:
        cmds = args.get("commands", "info functions;checksec;quit")
        gdb_cmds = " ".join(f'-ex "{c.strip()}"' for c in cmds.split(";"))
        cmd = f"gdb -batch -q {gdb_cmds} {args['binary_path']}"
        if core := args.get("core_file"):
            cmd += f" {core}"
        return ["sh", "-c", cmd]

    def parse_output(self, raw_output: str) -> list[dict]:
        return [{"type": "gdb_output", "data": raw_output.strip()}]
