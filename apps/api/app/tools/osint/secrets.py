"""Secret and credential discovery tools."""

import json

from app.tools.base import SecurityTool

OSINT_IMAGE = "nullify-tools-osint:latest"


class TrufflehogTool(SecurityTool):
    name = "trufflehog_scan"
    description = (
        "Find leaked credentials and secrets in git repos, filesystems, and S3 buckets. "
        "Use for secret detection and exposure assessment."
    )
    binary = "trufflehog"
    docker_image = OSINT_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "target": {"type": "string", "description": "Git repo URL, filesystem path, or S3 bucket."},
            "source_type": {"type": "string", "description": "Source type: git, filesystem, s3 (default: git)."},
            "only_verified": {"type": "boolean", "description": "Only show verified secrets (default: true)."},
        },
        "required": ["target"],
    }

    def build_command(self, args: dict) -> list[str]:
        source = args.get("source_type", "git")
        cmd = ["trufflehog", source, args["target"], "--json"]
        if args.get("only_verified", True):
            cmd.append("--only-verified")
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
                    "type": "leaked_secret",
                    "detector": data.get("DetectorName", ""),
                    "verified": data.get("Verified", False),
                    "raw": data.get("Raw", "")[:50] + "...",
                    "source": data.get("SourceMetadata", {}),
                    "severity": "CRITICAL" if data.get("Verified") else "HIGH",
                })
            except json.JSONDecodeError:
                continue
        return findings
