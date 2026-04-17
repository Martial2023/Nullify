"""Nmap — Network port scanner and service detection."""

import re

from app.tools.base import SecurityTool


class NmapTool(SecurityTool):
    name = "nmap_scan"
    description = (
        "Scan a target for open ports, running services, and OS detection. "
        "Use this for network reconnaissance and service enumeration."
    )
    binary = "nmap"
    parameters = {
        "type": "object",
        "properties": {
            "target": {
                "type": "string",
                "description": "Target IP, hostname, or CIDR range to scan.",
            },
            "ports": {
                "type": "string",
                "description": "Port specification (e.g. '22,80,443' or '1-1000'). Defaults to top 1000.",
            },
            "scan_type": {
                "type": "string",
                "enum": ["quick", "version", "full"],
                "description": "Quick (top 100), version (-sV), or full (-sV -sC -O).",
            },
        },
        "required": ["target"],
    }

    def build_command(self, args: dict) -> list[str]:
        target = args["target"]
        scan_type = args.get("scan_type", "version")
        ports = args.get("ports")

        cmd = ["nmap"]

        if scan_type == "quick":
            cmd += ["-T4", "--top-ports", "100"]
        elif scan_type == "full":
            cmd += ["-sV", "-sC", "-O", "-T4"]
        else:  # version
            cmd += ["-sV", "-T4"]

        if ports:
            cmd += ["-p", ports]

        cmd.append(target)
        return cmd

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        port_pattern = re.compile(
            r"(\d+)/(tcp|udp)\s+(\w+)\s+(.*)"
        )
        for match in port_pattern.finditer(raw_output):
            port, proto, state, service = match.groups()
            findings.append({
                "type": "open_port",
                "port": int(port),
                "protocol": proto,
                "state": state,
                "service": service.strip(),
            })
        return findings
