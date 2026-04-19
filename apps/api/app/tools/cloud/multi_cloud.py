"""Multi-cloud security assessment tools."""

import json

from app.tools.base import SecurityTool

CLOUD_IMAGE = "nullify-tools-cloud:latest"


class ScoutSuiteTool(SecurityTool):
    name = "scoutsuite_scan"
    description = "Multi-cloud security auditing (AWS, Azure, GCP). Use for cloud configuration review."
    binary = "scout"
    docker_image = CLOUD_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "provider": {"type": "string", "description": "Cloud provider: aws, azure, gcp."},
            "services": {"type": "string", "description": "Specific services to audit (comma-separated)."},
        },
        "required": ["provider"],
    }

    def build_command(self, args: dict) -> list[str]:
        cmd = ["scout", args["provider"], "--no-browser", "--report-dir", "/tmp/scoutsuite"]
        if services := args.get("services"):
            cmd.extend(["--services", services])
        return cmd

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        for line in raw_output.splitlines():
            if "danger" in line.lower() or "warning" in line.lower():
                findings.append({"type": "cloud_finding", "detail": line.strip()})
        return findings


class CloudSploitTool(SecurityTool):
    name = "cloudsploit_scan"
    description = "Cloud security posture management scanner. Use for cloud misconfiguration detection."
    binary = "cloudsploit"
    docker_image = CLOUD_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "provider": {"type": "string", "description": "Cloud provider: aws, azure, gcp."},
            "compliance": {"type": "string", "description": "Compliance framework: cis, hipaa, pci."},
        },
        "required": ["provider"],
    }

    def build_command(self, args: dict) -> list[str]:
        cmd = ["cloudsploit", "scan", "--cloud", args["provider"], "--json", "/dev/stdout"]
        if comp := args.get("compliance"):
            cmd.extend(["--compliance", comp])
        return cmd

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        try:
            data = json.loads(raw_output)
            for result in data if isinstance(data, list) else [data]:
                if result.get("status") in ("FAIL", "WARN"):
                    findings.append({
                        "type": "cloud_misconfiguration",
                        "plugin": result.get("plugin", ""),
                        "status": result.get("status", ""),
                        "resource": result.get("resource", ""),
                        "message": result.get("message", ""),
                    })
        except json.JSONDecodeError:
            pass
        return findings
