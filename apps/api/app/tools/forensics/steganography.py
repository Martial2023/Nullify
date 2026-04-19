"""Steganography tools."""

from app.tools.base import SecurityTool

FORENSICS_IMAGE = "nullify-tools-forensics:latest"


class SteghideTool(SecurityTool):
    name = "steghide_analyze"
    description = "Hide and extract data in images/audio files (JPEG, BMP, WAV, AU). Use for CTF steganography."
    binary = "steghide"
    docker_image = FORENSICS_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "file_path": {"type": "string", "description": "Path to the stego file."},
            "passphrase": {"type": "string", "description": "Passphrase for extraction (empty string for no passphrase)."},
            "action": {"type": "string", "description": "Action: info or extract (default: info)."},
        },
        "required": ["file_path"],
    }

    def build_command(self, args: dict) -> list[str]:
        action = args.get("action", "info")
        if action == "extract":
            cmd = ["steghide", "extract", "-sf", args["file_path"], "-f", "-xf", "/dev/stdout"]
            passphrase = args.get("passphrase", "")
            cmd.extend(["-p", passphrase])
        else:
            cmd = ["steghide", "info", args["file_path"], "-p", args.get("passphrase", "")]
        return cmd

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        for line in raw_output.splitlines():
            line = line.strip()
            if "embedded" in line.lower() or "size:" in line.lower() or "encrypted" in line.lower():
                findings.append({"type": "stego_info", "detail": line})
            elif line and not line.startswith("\""):
                findings.append({"type": "stego_data", "data": line})
        return findings


class ZstegTool(SecurityTool):
    name = "zsteg_analyze"
    description = "PNG/BMP steganography detector — LSB, MSB, bit planes. Use for image steganography CTFs."
    binary = "zsteg"
    docker_image = FORENSICS_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "file_path": {"type": "string", "description": "Path to PNG/BMP file."},
            "all": {"type": "boolean", "description": "Try all known methods (default: true)."},
        },
        "required": ["file_path"],
    }

    def build_command(self, args: dict) -> list[str]:
        cmd = ["zsteg", args["file_path"]]
        if args.get("all", True):
            cmd.append("-a")
        return cmd

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        for line in raw_output.splitlines():
            line = line.strip()
            if line and ":" in line:
                parts = line.split(":", 1)
                findings.append({"type": "stego_finding", "channel": parts[0].strip(), "data": parts[1].strip()})
        return findings


class OutguessTool(SecurityTool):
    name = "outguess_analyze"
    description = "Steganography tool for JPEG files. Use for extracting hidden data from JPEG images."
    binary = "outguess"
    docker_image = FORENSICS_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "file_path": {"type": "string", "description": "Path to JPEG file."},
            "key": {"type": "string", "description": "Extraction key."},
        },
        "required": ["file_path"],
    }

    def build_command(self, args: dict) -> list[str]:
        cmd = ["outguess", "-r"]
        if key := args.get("key"):
            cmd.extend(["-k", key])
        cmd.extend([args["file_path"], "/dev/stdout"])
        return cmd

    def parse_output(self, raw_output: str) -> list[dict]:
        if raw_output.strip():
            return [{"type": "stego_extracted", "data": raw_output.strip()}]
        return []
