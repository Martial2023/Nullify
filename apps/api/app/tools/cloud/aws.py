"""AWS security tools."""

import json

from app.tools.base import SecurityTool

CLOUD_IMAGE = "nullify-tools-cloud:latest"


class ProwlerTool(SecurityTool):
    name = "prowler_scan"
    description = (
        "AWS security assessment tool — CIS benchmarks, best practices, GDPR, HIPAA compliance. "
        "Use for comprehensive AWS account auditing."
    )
    binary = "prowler"
    docker_image = CLOUD_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "provider": {"type": "string", "description": "Cloud provider: aws, azure, gcp (default: aws)."},
            "checks": {"type": "string", "description": "Specific checks to run (comma-separated)."},
            "severity": {"type": "string", "description": "Minimum severity: informational, low, medium, high, critical."},
        },
        "required": [],
    }

    def build_command(self, args: dict) -> list[str]:
        cmd = ["prowler", args.get("provider", "aws"), "-M", "json", "-o", "/dev/stdout"]
        if checks := args.get("checks"):
            cmd.extend(["-c", checks])
        if severity := args.get("severity"):
            cmd.extend(["--severity", severity])
        return cmd

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        for line in raw_output.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                if data.get("StatusExtended", "").lower() == "fail":
                    findings.append({
                        "type": "cloud_misconfiguration",
                        "check": data.get("CheckTitle", ""),
                        "severity": data.get("Severity", "MEDIUM"),
                        "resource": data.get("ResourceId", ""),
                        "detail": data.get("StatusExtended", ""),
                    })
            except json.JSONDecodeError:
                continue
        return findings


class PacuTool(SecurityTool):
    name = "pacu_exploit"
    description = "AWS exploitation framework. Use for post-compromise AWS enumeration and privilege escalation."
    binary = "pacu"
    docker_image = CLOUD_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "module": {"type": "string", "description": "Pacu module to run (e.g. iam__enum_permissions, ec2__enum)."},
            "args": {"type": "string", "description": "Module arguments."},
        },
        "required": ["module"],
    }

    def build_command(self, args: dict) -> list[str]:
        cmd_str = f"pacu --cli --module {args['module']}"
        if extra := args.get("args"):
            cmd_str += f" --module-args '{extra}'"
        return ["sh", "-c", cmd_str]

    def parse_output(self, raw_output: str) -> list[dict]:
        return [{"type": "aws_exploitation", "data": raw_output.strip()}]


class AwsCliTool(SecurityTool):
    name = "aws_cli"
    description = "AWS CLI for cloud enumeration and interaction. Use for direct AWS API calls."
    binary = "aws"
    docker_image = CLOUD_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "service": {"type": "string", "description": "AWS service (e.g. s3, ec2, iam, lambda)."},
            "command": {"type": "string", "description": "AWS CLI command (e.g. 'ls', 'describe-instances')."},
            "args": {"type": "string", "description": "Additional arguments."},
            "region": {"type": "string", "description": "AWS region."},
        },
        "required": ["service", "command"],
    }

    def build_command(self, args: dict) -> list[str]:
        cmd = ["aws", args["service"], args["command"], "--output", "json"]
        if region := args.get("region"):
            cmd.extend(["--region", region])
        if extra := args.get("args"):
            cmd.extend(extra.split())
        return cmd

    def parse_output(self, raw_output: str) -> list[dict]:
        try:
            data = json.loads(raw_output)
            return [{"type": "aws_result", "data": data}]
        except json.JSONDecodeError:
            return [{"type": "aws_result", "data": raw_output.strip()}]
