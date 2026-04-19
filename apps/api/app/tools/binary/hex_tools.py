"""Hex dump tools."""

from app.tools.base import SecurityTool

BINARY_IMAGE = "nullify-tools-binary:latest"


class XxdTool(SecurityTool):
    name = "xxd_dump"
    description = "Create hex dump of a file. Use for binary inspection and CTF challenges."
    binary = "xxd"
    docker_image = BINARY_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "file_path": {"type": "string", "description": "Path to the file."},
            "length": {"type": "integer", "description": "Number of bytes to dump (default: 256)."},
            "offset": {"type": "integer", "description": "Start offset in bytes."},
        },
        "required": ["file_path"],
    }

    def build_command(self, args: dict) -> list[str]:
        cmd = ["xxd", "-l", str(args.get("length", 256))]
        if offset := args.get("offset"):
            cmd.extend(["-s", str(offset)])
        cmd.append(args["file_path"])
        return cmd

    def parse_output(self, raw_output: str) -> list[dict]:
        return [{"type": "hex_dump", "data": raw_output.strip()}]


class HexdumpTool(SecurityTool):
    name = "hexdump_dump"
    description = "Canonical hex dump. Use for quick binary file inspection."
    binary = "hexdump"
    docker_image = BINARY_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "file_path": {"type": "string", "description": "Path to the file."},
            "length": {"type": "integer", "description": "Number of bytes (default: 256)."},
        },
        "required": ["file_path"],
    }

    def build_command(self, args: dict) -> list[str]:
        return ["hexdump", "-C", "-n", str(args.get("length", 256)), args["file_path"]]

    def parse_output(self, raw_output: str) -> list[dict]:
        return [{"type": "hex_dump", "data": raw_output.strip()}]
