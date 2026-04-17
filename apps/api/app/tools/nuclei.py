"""Nuclei — Template-based vulnerability scanner."""

import json

from app.tools.base import SecurityTool


SEVERITY_MAP = {
    "critical": "CRITICAL",
    "high": "HIGH",
    "medium": "MEDIUM",
    "low": "LOW",
    "info": "INFO",
}


class NucleiTool(SecurityTool):
    name = "nuclei_scan"
    description = (
        "Scan a target for known vulnerabilities using Nuclei templates. "
        "Detects CVEs, misconfigurations, exposed panels, default credentials, etc. "
        "This is the primary vulnerability scanning tool."
    )
    binary = "nuclei"
    parameters = {
        "type": "object",
        "properties": {
            "target": {
                "type": "string",
                "description": "Target URL or host to scan.",
            },
            "severity": {
                "type": "string",
                "enum": ["critical", "high", "medium", "low", "info"],
                "description": "Minimum severity to report. Defaults to all.",
            },
            "tags": {
                "type": "string",
                "description": "Comma-separated template tags to filter (e.g. 'cve,xss,sqli').",
            },
        },
        "required": ["target"],
    }

    def build_command(self, args: dict) -> list[str]:
        cmd = [
            "nuclei",
            "-u", args["target"],
            "-jsonl",
            "-silent",
            "-timeout", "10",
            "-duc",
            "-nc",
        ]
        if severity := args.get("severity"):
            cmd += ["-s", severity]
        if tags := args.get("tags"):
            cmd += ["-tags", tags]
        return cmd

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        for line in raw_output.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                info = data.get("info", {})
                findings.append({
                    "type": "vulnerability",
                    "title": info.get("name", data.get("template-id", "Unknown")),
                    "severity": SEVERITY_MAP.get(
                        info.get("severity", "info"), "INFO"
                    ),
                    "description": info.get("description", ""),
                    "target": data.get("matched-at", data.get("host", "")),
                    "evidence": data.get("matcher-name", ""),
                    "template_id": data.get("template-id", ""),
                    "reference": info.get("reference", []),
                })
            except json.JSONDecodeError:
                continue
        return findings
