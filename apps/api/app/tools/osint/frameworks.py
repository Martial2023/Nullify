"""OSINT frameworks."""

import json

from app.tools.base import SecurityTool

OSINT_IMAGE = "nullify-tools-osint:latest"


class ReconNgTool(SecurityTool):
    name = "recon_ng_scan"
    description = "Full-featured OSINT reconnaissance framework with modular design. Use for structured OSINT workflows."
    binary = "recon-ng"
    docker_image = OSINT_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "module": {"type": "string", "description": "Module path (e.g. recon/domains-hosts/hackertarget)."},
            "source": {"type": "string", "description": "Source input (domain, email, etc)."},
        },
        "required": ["module", "source"],
    }

    def build_command(self, args: dict) -> list[str]:
        commands = (
            f"workspaces create nullify; "
            f"modules load {args['module']}; "
            f"options set SOURCE {args['source']}; "
            f"run; "
            f"exit"
        )
        return ["sh", "-c", f"echo '{commands}' | recon-ng --no-check"]

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        for line in raw_output.splitlines():
            line = line.strip()
            if line and "[*]" in line and not line.startswith("["):
                findings.append({"type": "osint_finding", "detail": line})
        return findings


class SpiderfootTool(SecurityTool):
    name = "spiderfoot_scan"
    description = (
        "Automated OSINT collection engine — 200+ data sources. "
        "Use for comprehensive target reconnaissance."
    )
    binary = "spiderfoot"
    docker_image = OSINT_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "target": {"type": "string", "description": "Target (domain, IP, email, username)."},
            "modules": {"type": "string", "description": "Specific modules (comma-separated)."},
            "scan_type": {"type": "string", "description": "Scan type: all, passive, investigate, footprint."},
        },
        "required": ["target"],
    }

    def build_command(self, args: dict) -> list[str]:
        cmd = ["spiderfoot", "-s", args["target"], "-q", "-o", "json"]
        if modules := args.get("modules"):
            cmd.extend(["-m", modules])
        if scan_type := args.get("scan_type"):
            cmd.extend(["-t", scan_type])
        return cmd

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        try:
            data = json.loads(raw_output)
            for entry in data if isinstance(data, list) else [data]:
                findings.append({
                    "type": "osint_finding",
                    "module": entry.get("module", ""),
                    "data_type": entry.get("type", ""),
                    "data": entry.get("data", ""),
                })
        except json.JSONDecodeError:
            pass
        return findings
