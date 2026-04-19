"""Disassembly and reverse engineering tools."""

from app.tools.base import SecurityTool

BINARY_IMAGE = "nullify-tools-binary:latest"


class Radare2Tool(SecurityTool):
    name = "radare2_analyze"
    description = (
        "Radare2 reverse engineering framework. Disassemble, analyze control flow, "
        "find strings, and identify functions. Use for binary reverse engineering."
    )
    binary = "r2"
    docker_image = BINARY_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "binary_path": {"type": "string", "description": "Path to the binary."},
            "commands": {"type": "string", "description": "r2 commands (semicolon-separated, e.g. 'aaa;afl;pdf @main')."},
        },
        "required": ["binary_path"],
    }

    def build_command(self, args: dict) -> list[str]:
        cmds = args.get("commands", "aaa;afl;iz")
        return ["r2", "-q", "-c", cmds, args["binary_path"]]

    def parse_output(self, raw_output: str) -> list[dict]:
        return [{"type": "r2_output", "data": raw_output.strip()}]


class GhidraTool(SecurityTool):
    name = "ghidra_analyze"
    description = (
        "Ghidra headless decompiler. Produces pseudo-C from binaries. "
        "Use for advanced decompilation and code analysis."
    )
    binary = "analyzeHeadless"
    docker_image = BINARY_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "binary_path": {"type": "string", "description": "Path to the binary."},
            "script": {"type": "string", "description": "Ghidra script to run (default: decompile all functions)."},
        },
        "required": ["binary_path"],
    }

    def build_command(self, args: dict) -> list[str]:
        script = args.get("script", "DecompileAllFunctions.java")
        return [
            "analyzeHeadless", "/tmp/ghidra_project", "analysis",
            "-import", args["binary_path"],
            "-postScript", script,
            "-deleteProject",
        ]

    def parse_output(self, raw_output: str) -> list[dict]:
        return [{"type": "decompilation", "data": raw_output.strip()}]
