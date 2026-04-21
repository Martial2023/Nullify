"""Injection testing tools (command injection, NoSQL, SSTI)."""

import json

from app.tools.base import SecurityTool

WEB_IMAGE = "nullify-tools-web:latest"


class CommixTool(SecurityTool):
    name = "commix_scan"
    description = (
        "Automated OS command injection detection and exploitation. "
        "Use when you suspect command injection in parameters."
    )
    binary = "commix"
    docker_image = WEB_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "Target URL with injectable parameter."},
            "data": {"type": "string", "description": "POST data (e.g. 'param=value')."},
            "level": {"type": "integer", "description": "Testing level 1-3 (default: 2)."},
        },
        "required": ["url"],
    }

    def build_command(self, args: dict) -> list[str]:
        cmd = ["python3", "/opt/commix/commix.py", "--url", args["url"],
               "--level", str(args.get("level", 2)),
               "--batch"]
        if data := args.get("data"):
            cmd.extend(["--data", data])
        return cmd

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        for line in raw_output.splitlines():
            low = line.lower()
            if "vulnerable" in low or "injectable" in low:
                findings.append({"type": "command_injection", "detail": line.strip(), "severity": "CRITICAL"})
            elif "payload" in low:
                findings.append({"type": "cmdi_payload", "payload": line.strip()})
        return findings


class NosqlmapTool(SecurityTool):
    name = "nosqlmap_scan"
    description = "NoSQL injection detection and exploitation. Use against MongoDB-backed web applications."
    binary = "nosqlmap"
    docker_image = WEB_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "Target URL."},
            "method": {"type": "string", "description": "HTTP method: GET or POST (default: GET)."},
            "post_data": {"type": "string", "description": "POST data string."},
        },
        "required": ["url"],
    }

    def build_command(self, args: dict) -> list[str]:
        cmd = ["python3", "/opt/nosqlmap/nosqlmap.py",
               "--url", args["url"], "--attack", "1"]
        if method := args.get("method"):
            cmd.extend(["--method", method])
        if data := args.get("post_data"):
            cmd.extend(["--data", data])
        return cmd

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        for line in raw_output.splitlines():
            if "inject" in line.lower() or "vulnerable" in line.lower():
                findings.append({"type": "nosql_injection", "detail": line.strip(), "severity": "CRITICAL"})
        return findings


class TplmapTool(SecurityTool):
    name = "tplmap_scan"
    description = (
        "Server-side template injection (SSTI) detection and exploitation. "
        "Use when you suspect template injection in parameters."
    )
    binary = "tplmap"
    docker_image = WEB_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "Target URL with injectable parameter (e.g. http://target.com/page?name=test)."},
            "level": {"type": "integer", "description": "Testing level 1-5 (default: 2)."},
        },
        "required": ["url"],
    }

    def build_command(self, args: dict) -> list[str]:
        return ["python3", "/opt/tplmap/tplmap.py",
                "-u", args["url"],
                "--level", str(args.get("level", 2))]

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        for line in raw_output.splitlines():
            if "confirmed" in line.lower() or "injectable" in line.lower():
                findings.append({"type": "ssti_vulnerability", "detail": line.strip(), "severity": "CRITICAL"})
            elif "engine" in line.lower() and ":" in line:
                findings.append({"type": "template_engine", "detail": line.strip()})
        return findings
