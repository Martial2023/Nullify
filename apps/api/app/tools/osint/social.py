"""Social media OSINT tools."""

import json

from app.tools.base import SecurityTool

OSINT_IMAGE = "nullify-tools-osint:latest"


class SherlockTool(SecurityTool):
    name = "sherlock_search"
    description = (
        "Hunt usernames across 300+ social media sites. "
        "Use for OSINT — finding accounts linked to a target username."
    )
    binary = "sherlock"
    docker_image = OSINT_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "username": {"type": "string", "description": "Username to search."},
            "sites": {"type": "string", "description": "Specific sites to check (comma-separated)."},
        },
        "required": ["username"],
    }

    def build_command(self, args: dict) -> list[str]:
        cmd = ["sherlock", args["username"], "--print-found", "--json", "/dev/stdout"]
        if sites := args.get("sites"):
            for site in sites.split(","):
                cmd.extend(["--site", site.strip()])
        return cmd

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        try:
            data = json.loads(raw_output)
            for site, info in data.items():
                if info.get("status") == "Claimed":
                    findings.append({
                        "type": "social_account",
                        "site": site,
                        "url": info.get("url_user", ""),
                    })
        except json.JSONDecodeError:
            for line in raw_output.splitlines():
                if "[+]" in line:
                    findings.append({"type": "social_account", "detail": line.strip()})
        return findings


class SocialAnalyzerTool(SecurityTool):
    name = "social_analyzer"
    description = "Analyze and find social media profiles. Use for comprehensive social OSINT."
    binary = "social-analyzer"
    docker_image = OSINT_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "username": {"type": "string", "description": "Username to analyze."},
            "mode": {"type": "string", "description": "Mode: fast or slow (default: fast)."},
        },
        "required": ["username"],
    }

    def build_command(self, args: dict) -> list[str]:
        return [
            "social-analyzer",
            "--username", args["username"],
            "--metadata",
            "--mode", args.get("mode", "fast"),
            "--output", "json",
        ]

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        try:
            data = json.loads(raw_output)
            for entry in data if isinstance(data, list) else [data]:
                if entry.get("found"):
                    findings.append({
                        "type": "social_account",
                        "site": entry.get("site", ""),
                        "url": entry.get("link", ""),
                    })
        except json.JSONDecodeError:
            pass
        return findings
