"""Web technology fingerprinting tools."""

import json

from app.tools.base import SecurityTool

WEB_IMAGE = "nullify-tools-web:latest"


class WhatwebTool(SecurityTool):
    name = "whatweb_detect"
    description = (
        "Web technology fingerprinting — identifies CMS, frameworks, "
        "server software, and other technologies. Use for tech stack identification."
    )
    binary = "whatweb"
    docker_image = WEB_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "Target URL."},
            "aggression": {"type": "integer", "description": "Aggression level 1-4 (default: 1)."},
        },
        "required": ["url"],
    }

    def build_command(self, args: dict) -> list[str]:
        return [
            "whatweb", args["url"],
            "--log-json=/dev/stdout",
            f"--aggression={args.get('aggression', 1)}",
            "--no-errors",
        ]

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        for line in raw_output.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                plugins = data.get("plugins", {})
                for name, info in plugins.items():
                    version = info.get("version", [None])[0] if info.get("version") else None
                    findings.append({
                        "type": "technology",
                        "name": name,
                        "version": version,
                        "url": data.get("target", ""),
                    })
            except json.JSONDecodeError:
                continue
        return findings
