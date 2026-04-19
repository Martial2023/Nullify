"""Port scanners — Rustscan & Masscan wrappers."""

import json
import re

from app.tools.base import SecurityTool

NETWORK_IMAGE = "nullify-tools-network:latest"


class RustscanTool(SecurityTool):
    name = "rustscan"
    description = (
        "Ultra-fast port scanner. Use for quick initial port discovery "
        "before detailed nmap scans. Scans all 65535 ports in seconds."
    )
    binary = "rustscan"
    docker_image = NETWORK_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "target": {
                "type": "string",
                "description": "Target IP or hostname to scan.",
            },
            "batch_size": {
                "type": "integer",
                "description": "Number of ports scanned concurrently (default 4500).",
            },
            "ports": {
                "type": "string",
                "description": "Port range to scan (e.g. '1-1000'). Defaults to all ports.",
            },
        },
        "required": ["target"],
    }

    def build_command(self, args: dict) -> list[str]:
        target = args["target"]
        batch_size = str(args.get("batch_size", 4500))

        cmd = ["rustscan", "-a", target, "-b", batch_size]

        ports = args.get("ports")
        if ports:
            cmd.extend(["-p", ports])

        # Pass remaining flags to nmap for service detection
        cmd.extend(["--", "-sV"])
        return cmd

    def parse_output(self, raw_output: str) -> list[dict]:
        findings: list[dict] = []
        port_pattern = re.compile(r"(\d+)/(tcp|udp)\s+(\w+)\s+(.*)")
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


class MasscanTool(SecurityTool):
    name = "masscan_scan"
    description = (
        "High-speed Internet-scale port scanner. Use for scanning large "
        "IP ranges quickly. Can scan the entire Internet in under 6 minutes."
    )
    binary = "masscan"
    docker_image = NETWORK_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "target": {
                "type": "string",
                "description": "Target IP, CIDR range, or range (e.g. '10.0.0.0/8').",
            },
            "ports": {
                "type": "string",
                "description": "Port specification (default '1-65535').",
            },
            "rate": {
                "type": "integer",
                "description": "Packets per second (default 10000).",
            },
        },
        "required": ["target"],
    }

    def build_command(self, args: dict) -> list[str]:
        target = args["target"]
        ports = args.get("ports", "1-65535")
        rate = str(args.get("rate", 10000))

        return [
            "masscan", target,
            f"-p{ports}",
            f"--rate={rate}",
            "--banners",
            "-oJ", "-",
        ]

    def parse_output(self, raw_output: str) -> list[dict]:
        findings: list[dict] = []
        try:
            # masscan JSON output may have trailing commas; strip them
            cleaned = raw_output.strip().rstrip(",")
            if not cleaned.startswith("["):
                cleaned = f"[{cleaned}]"
            data = json.loads(cleaned)
            for entry in data:
                ip = entry.get("ip", "")
                for port_info in entry.get("ports", []):
                    findings.append({
                        "type": "open_port",
                        "ip": ip,
                        "port": port_info.get("port"),
                        "protocol": port_info.get("proto", "tcp"),
                        "state": port_info.get("status", "open"),
                        "service": port_info.get("service", {}).get("name", ""),
                        "banner": port_info.get("service", {}).get("banner", ""),
                    })
        except json.JSONDecodeError:
            # Fallback: try to extract IPs and ports from raw text
            for line in raw_output.splitlines():
                line = line.strip()
                if line and not line.startswith(("#", "{")):
                    findings.append({"type": "raw_result", "data": line})
        return findings
