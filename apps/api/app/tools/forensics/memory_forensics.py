"""Memory forensics tools."""

import json

from app.tools.base import SecurityTool

FORENSICS_IMAGE = "nullify-tools-forensics:latest"


class VolatilityTool(SecurityTool):
    name = "volatility2_analyze"
    description = "Volatility 2 memory forensics framework. Analyze RAM dumps for malware, rootkits, and artifacts."
    binary = "vol.py"
    docker_image = FORENSICS_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "dump_file": {"type": "string", "description": "Path to memory dump file."},
            "profile": {"type": "string", "description": "OS profile (e.g. Win7SP1x64, LinuxUbuntu1604x64)."},
            "plugin": {"type": "string", "description": "Plugin to run (e.g. pslist, netscan, malfind, dlllist)."},
        },
        "required": ["dump_file", "plugin"],
    }

    def build_command(self, args: dict) -> list[str]:
        cmd = ["vol.py", "-f", args["dump_file"]]
        if profile := args.get("profile"):
            cmd.extend(["--profile", profile])
        cmd.append(args["plugin"])
        return cmd

    def parse_output(self, raw_output: str) -> list[dict]:
        return [{"type": "memory_analysis", "plugin": "volatility2", "data": raw_output.strip()[:10000]}]


class Volatility3Tool(SecurityTool):
    name = "volatility3_analyze"
    description = "Volatility 3 — modern memory forensics with auto-detection. Use for RAM dump analysis."
    binary = "vol3"
    docker_image = FORENSICS_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "dump_file": {"type": "string", "description": "Path to memory dump file."},
            "plugin": {"type": "string", "description": "Plugin (e.g. windows.pslist, windows.netscan, linux.pslist)."},
        },
        "required": ["dump_file", "plugin"],
    }

    def build_command(self, args: dict) -> list[str]:
        return ["vol3", "-f", args["dump_file"], "-r", "json", args["plugin"]]

    def parse_output(self, raw_output: str) -> list[dict]:
        try:
            data = json.loads(raw_output)
            return [{"type": "memory_analysis", "plugin": "volatility3", "data": data}]
        except json.JSONDecodeError:
            return [{"type": "memory_analysis", "plugin": "volatility3", "data": raw_output.strip()[:10000]}]
