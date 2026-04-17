"""httpx (ProjectDiscovery) — HTTP probe for live hosts."""

import json

from app.tools.base import SecurityTool


class HttpxTool(SecurityTool):
    name = "httpx_probe"
    description = (
        "Probe a list of hosts/URLs to check which ones are alive and "
        "collect HTTP response info (status, title, tech). "
        "Use after subdomain discovery to find live web servers."
    )
    binary = "httpx"
    parameters = {
        "type": "object",
        "properties": {
            "targets": {
                "type": "string",
                "description": "Comma-separated list of hosts or URLs to probe.",
            },
        },
        "required": ["targets"],
    }

    def build_command(self, args: dict) -> list[str]:
        targets = args["targets"]
        return [
            "httpx",
            "-u", targets,
            "-silent",
            "-status-code",
            "-title",
            "-tech-detect",
            "-json",
            "-timeout", "10",
            "-duc",
            "-nc",
        ]

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        for line in raw_output.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                findings.append({
                    "type": "live_host",
                    "url": data.get("url", ""),
                    "status_code": data.get("status_code"),
                    "title": data.get("title", ""),
                    "technologies": data.get("tech", []),
                })
            except json.JSONDecodeError:
                continue
        return findings
