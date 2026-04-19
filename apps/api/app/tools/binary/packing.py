"""Payload generation and binary manipulation tools."""

from app.tools.base import SecurityTool

BINARY_IMAGE = "nullify-tools-binary:latest"


class MsfvenomTool(SecurityTool):
    name = "msfvenom_generate"
    description = (
        "Metasploit payload generator. Create shellcode, reverse shells, "
        "and encoded payloads. Use for exploit development."
    )
    binary = "msfvenom"
    docker_image = BINARY_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "payload": {"type": "string", "description": "Payload type (e.g. linux/x64/shell_reverse_tcp)."},
            "lhost": {"type": "string", "description": "Listener host."},
            "lport": {"type": "integer", "description": "Listener port."},
            "format": {"type": "string", "description": "Output format (python, c, raw, elf, exe)."},
            "encoder": {"type": "string", "description": "Encoder (e.g. x86/shikata_ga_nai)."},
            "bad_chars": {"type": "string", "description": "Bad characters to avoid (e.g. '\\x00\\x0a')."},
        },
        "required": ["payload"],
    }

    def build_command(self, args: dict) -> list[str]:
        cmd = ["msfvenom", "-p", args["payload"],
               "-f", args.get("format", "python")]
        if lhost := args.get("lhost"):
            cmd.append(f"LHOST={lhost}")
        if lport := args.get("lport"):
            cmd.append(f"LPORT={lport}")
        if encoder := args.get("encoder"):
            cmd.extend(["-e", encoder])
        if bad := args.get("bad_chars"):
            cmd.extend(["-b", bad])
        return cmd

    def parse_output(self, raw_output: str) -> list[dict]:
        return [{"type": "generated_payload", "data": raw_output.strip()}]


class UpxTool(SecurityTool):
    name = "upx_analyze"
    description = "UPX packer/unpacker. Decompress packed binaries for analysis."
    binary = "upx"
    docker_image = BINARY_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "file_path": {"type": "string", "description": "Path to the binary."},
            "decompress": {"type": "boolean", "description": "Decompress the binary (default: true)."},
        },
        "required": ["file_path"],
    }

    def build_command(self, args: dict) -> list[str]:
        if args.get("decompress", True):
            return ["upx", "-d", args["file_path"]]
        return ["upx", "-l", args["file_path"]]

    def parse_output(self, raw_output: str) -> list[dict]:
        return [{"type": "upx_result", "data": raw_output.strip()}]


class LtraceTool(SecurityTool):
    name = "ltrace_analyze"
    description = "Library call tracer. Trace dynamic library calls made by a program."
    binary = "ltrace"
    docker_image = BINARY_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "binary_path": {"type": "string", "description": "Path to the binary."},
            "args": {"type": "string", "description": "Arguments to pass to the binary."},
        },
        "required": ["binary_path"],
    }

    def build_command(self, args: dict) -> list[str]:
        cmd = ["ltrace", "-o", "/dev/stdout", args["binary_path"]]
        if binary_args := args.get("args"):
            cmd.extend(binary_args.split())
        return cmd

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        for line in raw_output.splitlines():
            line = line.strip()
            if line:
                findings.append({"type": "library_call", "call": line})
        return findings[:500]
