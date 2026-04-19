"""XSS detection and exploitation tools."""

import json

from app.tools.base import SecurityTool

WEB_IMAGE = "nullify-tools-web:latest"


class DalfoxTool(SecurityTool):
    name = "dalfox_scan"
    description = (
        "Powerful XSS scanner with DOM analysis and WAF bypass. "
        "Use for detecting reflected, stored, and DOM-based XSS vulnerabilities."
    )
    binary = "dalfox"
    docker_image = WEB_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "Target URL with parameters (e.g. http://target.com/page?q=test)."},
            "blind": {"type": "string", "description": "Blind XSS callback URL."},
            "custom_payload": {"type": "string", "description": "Custom XSS payload file path."},
        },
        "required": ["url"],
    }

    def build_command(self, args: dict) -> list[str]:
        cmd = ["dalfox", "url", args["url"], "--format", "json", "--silence"]
        if blind := args.get("blind"):
            cmd.extend(["--blind", blind])
        if payload := args.get("custom_payload"):
            cmd.extend(["--custom-payload", payload])
        return cmd

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        for line in raw_output.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                findings.append({
                    "type": "xss_vulnerability",
                    "severity": data.get("severity", "HIGH"),
                    "inject_type": data.get("type", ""),
                    "poc": data.get("poc", ""),
                    "param": data.get("param", ""),
                    "payload": data.get("payload", ""),
                })
            except json.JSONDecodeError:
                if "POC" in line or "XSS" in line.upper():
                    findings.append({"type": "xss_vulnerability", "detail": line})
        return findings


class XssTrikeTool(SecurityTool):
    name = "xsstrike_scan"
    description = "Advanced XSS detection with fuzzing and context analysis. Use for thorough XSS testing."
    binary = "xsstrike"
    docker_image = WEB_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "Target URL with parameters."},
            "crawl": {"type": "boolean", "description": "Enable crawling (default: false)."},
        },
        "required": ["url"],
    }

    def build_command(self, args: dict) -> list[str]:
        cmd = ["python3", "/opt/XSStrike/xsstrike.py", "-u", args["url"], "--skip"]
        if args.get("crawl"):
            cmd.append("--crawl")
        return cmd

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        for line in raw_output.splitlines():
            line = line.strip()
            if "Vulnerable" in line or "payload" in line.lower():
                findings.append({"type": "xss_vulnerability", "detail": line})
        return findings
