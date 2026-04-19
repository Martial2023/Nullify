"""Binary analysis utilities."""

import json

from app.tools.base import SecurityTool

BINARY_IMAGE = "nullify-tools-binary:latest"


class BinwalkTool(SecurityTool):
    name = "binwalk_analyze"
    description = "Firmware and binary analysis — extract embedded files, detect signatures. Use for CTF and IoT."
    binary = "binwalk"
    docker_image = BINARY_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "file_path": {"type": "string", "description": "Path to the binary file."},
            "extract": {"type": "boolean", "description": "Extract embedded files (default: false)."},
        },
        "required": ["file_path"],
    }

    def build_command(self, args: dict) -> list[str]:
        cmd = ["binwalk"]
        if args.get("extract"):
            cmd.append("-e")
        cmd.append(args["file_path"])
        return cmd

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        for line in raw_output.splitlines():
            line = line.strip()
            if line and not line.startswith("DECIMAL") and not line.startswith("-"):
                parts = line.split(None, 2)
                if len(parts) >= 3 and parts[0].isdigit():
                    findings.append({
                        "type": "embedded_signature",
                        "offset_dec": int(parts[0]),
                        "offset_hex": parts[1],
                        "description": parts[2],
                    })
        return findings


class ChecksecTool(SecurityTool):
    name = "checksec_analyze"
    description = "Check binary security protections (RELRO, Stack Canary, NX, PIE, RPATH). Use before exploit dev."
    binary = "checksec"
    docker_image = BINARY_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "file_path": {"type": "string", "description": "Path to the ELF binary."},
        },
        "required": ["file_path"],
    }

    def build_command(self, args: dict) -> list[str]:
        return ["checksec", "--file", args["file_path"], "--output", "json"]

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        try:
            data = json.loads(raw_output)
            for binary_path, info in data.items():
                findings.append({
                    "type": "binary_protections",
                    "binary": binary_path,
                    "relro": info.get("relro", ""),
                    "canary": info.get("canary", ""),
                    "nx": info.get("nx", ""),
                    "pie": info.get("pie", ""),
                    "rpath": info.get("rpath", ""),
                    "fortify": info.get("fortify_source", ""),
                })
        except json.JSONDecodeError:
            findings.append({"type": "binary_protections", "raw": raw_output.strip()})
        return findings


class StringsTool(SecurityTool):
    name = "strings_extract"
    description = "Extract printable strings from binary files. Use for quick analysis and finding hardcoded secrets."
    binary = "strings"
    docker_image = BINARY_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "file_path": {"type": "string", "description": "Path to the file."},
            "min_length": {"type": "integer", "description": "Minimum string length (default: 4)."},
            "encoding": {"type": "string", "description": "Encoding: s=7-bit, S=8-bit, l=little-endian 16-bit."},
        },
        "required": ["file_path"],
    }

    def build_command(self, args: dict) -> list[str]:
        cmd = ["strings", "-n", str(args.get("min_length", 4))]
        if enc := args.get("encoding"):
            cmd.extend(["-e", enc])
        cmd.append(args["file_path"])
        return cmd

    def parse_output(self, raw_output: str) -> list[dict]:
        lines = raw_output.splitlines()
        return [{"type": "extracted_string", "value": line.strip()} for line in lines[:500] if line.strip()]


class ObjdumpTool(SecurityTool):
    name = "objdump_disasm"
    description = "Disassemble binary sections. Use for quick disassembly without a full RE framework."
    binary = "objdump"
    docker_image = BINARY_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "file_path": {"type": "string", "description": "Path to the binary."},
            "options": {"type": "string", "description": "Options: -d (disasm), -x (headers), -s (full contents). Default: -d."},
        },
        "required": ["file_path"],
    }

    def build_command(self, args: dict) -> list[str]:
        return ["objdump", args.get("options", "-d"), args["file_path"]]

    def parse_output(self, raw_output: str) -> list[dict]:
        return [{"type": "disassembly", "data": raw_output.strip()[:10000]}]


class ReadelfTool(SecurityTool):
    name = "readelf_analyze"
    description = "Display ELF binary information (headers, sections, symbols). Use for binary structure analysis."
    binary = "readelf"
    docker_image = BINARY_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "file_path": {"type": "string", "description": "Path to the ELF binary."},
            "options": {"type": "string", "description": "Options: -a (all), -h (header), -S (sections), -s (symbols). Default: -a."},
        },
        "required": ["file_path"],
    }

    def build_command(self, args: dict) -> list[str]:
        return ["readelf", args.get("options", "-a"), args["file_path"]]

    def parse_output(self, raw_output: str) -> list[dict]:
        return [{"type": "elf_info", "data": raw_output.strip()[:10000]}]
