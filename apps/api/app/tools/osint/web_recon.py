"""Web-based OSINT and subdomain takeover tools."""

import json

from app.tools.base import SecurityTool

OSINT_IMAGE = "nullify-tools-osint:latest"


class AquatoneTool(SecurityTool):
    name = "aquatone_screenshot"
    description = (
        "Web screenshot and visual inspection tool. "
        "Takes screenshots of discovered hosts for visual recon."
    )
    binary = "aquatone"
    docker_image = OSINT_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "urls": {"type": "string", "description": "Newline-separated URLs to screenshot."},
            "ports": {"type": "string", "description": "Ports to check (default: 80,443,8080,8443)."},
        },
        "required": ["urls"],
    }

    def build_command(self, args: dict) -> list[str]:
        urls = args["urls"].replace("'", "'\\''")
        cmd = f"echo '{urls}' | aquatone -out /tmp/aquatone"
        if ports := args.get("ports"):
            cmd += f" -ports {ports}"
        return ["sh", "-c", cmd]

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        for line in raw_output.splitlines():
            if "Saved" in line or "screenshot" in line.lower():
                findings.append({"type": "screenshot_taken", "detail": line.strip()})
            elif "Found" in line:
                findings.append({"type": "aquatone_finding", "detail": line.strip()})
        return findings


class SubjackTool(SecurityTool):
    name = "subjack_scan"
    description = "Subdomain takeover detection tool. Use to check if subdomains are vulnerable to takeover."
    binary = "subjack"
    docker_image = OSINT_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "domains_file": {"type": "string", "description": "File with list of subdomains."},
            "domains": {"type": "string", "description": "Newline-separated list of subdomains."},
        },
        "required": [],
    }

    def build_command(self, args: dict) -> list[str]:
        if domains := args.get("domains"):
            escaped = domains.replace("'", "'\\''")
            return ["sh", "-c",
                    f"echo '{escaped}' > /tmp/subs.txt && "
                    f"subjack -w /tmp/subs.txt -t 100 -timeout 30 -o /dev/stdout -ssl -a"]
        return ["subjack", "-w", args.get("domains_file", "/tmp/subs.txt"),
                "-t", "100", "-timeout", "30", "-o", "/dev/stdout", "-ssl", "-a"]

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        for line in raw_output.splitlines():
            line = line.strip()
            if line and "Vulnerable" in line:
                findings.append({"type": "subdomain_takeover", "detail": line, "severity": "HIGH"})
        return findings
