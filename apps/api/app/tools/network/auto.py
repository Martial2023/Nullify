"""Automated reconnaissance — AutoRecon."""

import re

from app.tools.base import SecurityTool

NETWORK_IMAGE = "nullify-tools-network:latest"


class AutoReconTool(SecurityTool):
    name = "autorecon_scan"
    description = (
        "Multi-threaded automated network reconnaissance tool. Runs port "
        "scans, service enumeration, and service-specific scans automatically. "
        "Use for comprehensive, hands-off reconnaissance of a single target."
    )
    binary = "autorecon"
    docker_image = NETWORK_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "target": {
                "type": "string",
                "description": "Target IP or hostname to scan.",
            },
        },
        "required": ["target"],
    }

    def build_command(self, args: dict) -> list[str]:
        target = args["target"]
        return [
            "autorecon", target,
            "--single-target",
            "-o", "/tmp/autorecon",
        ]

    def parse_output(self, raw_output: str) -> list[dict]:
        findings: list[dict] = []

        # Extract discovered services from autorecon summary output
        service_pattern = re.compile(
            r"\[(\d+)/(tcp|udp)\]\s+(\S+)"
        )
        for match in service_pattern.finditer(raw_output):
            port, proto, service = match.groups()
            findings.append({
                "type": "discovered_service",
                "port": int(port),
                "protocol": proto,
                "service": service,
            })

        # Extract open port mentions
        port_pattern = re.compile(r"(\d+)/(tcp|udp)\s+open\s+(\S+)")
        for match in port_pattern.finditer(raw_output):
            port, proto, service = match.groups()
            # Avoid duplicates
            existing = {(f["port"], f["protocol"]) for f in findings if "port" in f}
            if (int(port), proto) not in existing:
                findings.append({
                    "type": "discovered_service",
                    "port": int(port),
                    "protocol": proto,
                    "service": service,
                })

        # If nothing was parsed, return raw summary lines
        if not findings:
            for line in raw_output.splitlines():
                line = line.strip()
                if line and not line.startswith(("[*]", "[!]", "---")):
                    findings.append({"type": "autorecon_output", "data": line})

        return findings
