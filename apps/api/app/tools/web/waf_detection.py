"""WAF detection tools."""

import json

from app.tools.base import SecurityTool

WEB_IMAGE = "nullify-tools-web:latest"


class Wafw00fTool(SecurityTool):
    name = "wafw00f_scan"
    description = (
        "Web Application Firewall (WAF) fingerprinting tool. "
        "Identifies the WAF protecting a target. Use before exploit attempts."
    )
    binary = "wafw00f"
    docker_image = WEB_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "Target URL."},
            "findall": {"type": "boolean", "description": "Find all WAFs (default: false)."},
        },
        "required": ["url"],
    }

    def build_command(self, args: dict) -> list[str]:
        cmd = ["wafw00f", args["url"], "-o", "/dev/stdout", "-f", "json"]
        if args.get("findall"):
            cmd.append("-a")
        return cmd

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        try:
            data = json.loads(raw_output)
            for entry in data if isinstance(data, list) else [data]:
                findings.append({
                    "type": "waf_detected",
                    "firewall": entry.get("firewall", "Unknown"),
                    "manufacturer": entry.get("manufacturer", ""),
                    "url": entry.get("url", ""),
                })
        except json.JSONDecodeError:
            for line in raw_output.splitlines():
                if "is behind" in line or "WAF" in line:
                    findings.append({"type": "waf_detected", "detail": line.strip()})
        return findings
