"""Infrastructure as Code security tools."""

import json

from app.tools.base import SecurityTool

CLOUD_IMAGE = "nullify-tools-cloud:latest"


class CheckovTool(SecurityTool):
    name = "checkov_scan"
    description = (
        "IaC security scanner — Terraform, CloudFormation, Kubernetes, Dockerfile. "
        "Use to find misconfigurations in infrastructure code."
    )
    binary = "checkov"
    docker_image = CLOUD_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "directory": {"type": "string", "description": "Directory to scan."},
            "file": {"type": "string", "description": "Single file to scan."},
            "framework": {"type": "string", "description": "Framework: terraform, cloudformation, kubernetes, dockerfile."},
        },
        "required": [],
    }

    def build_command(self, args: dict) -> list[str]:
        cmd = ["checkov", "-o", "json", "--quiet"]
        if d := args.get("directory"):
            cmd.extend(["-d", d])
        elif f := args.get("file"):
            cmd.extend(["-f", f])
        else:
            cmd.extend(["-d", "."])
        if fw := args.get("framework"):
            cmd.extend(["--framework", fw])
        return cmd

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        try:
            data = json.loads(raw_output)
            results = data if isinstance(data, list) else [data]
            for result in results:
                for check in result.get("results", {}).get("failed_checks", []):
                    findings.append({
                        "type": "iac_misconfiguration",
                        "check_id": check.get("check_id", ""),
                        "check_name": check.get("name", ""),
                        "file": check.get("file_path", ""),
                        "resource": check.get("resource", ""),
                        "severity": check.get("severity", "MEDIUM"),
                    })
        except json.JSONDecodeError:
            pass
        return findings


class TerrascanTool(SecurityTool):
    name = "terrascan_scan"
    description = "IaC security scanner with OPA policy engine. Use for Terraform and K8s manifest scanning."
    binary = "terrascan"
    docker_image = CLOUD_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "directory": {"type": "string", "description": "Directory to scan."},
            "iac_type": {"type": "string", "description": "IaC type: terraform, k8s, docker, cft."},
            "policy_type": {"type": "string", "description": "Policy type: aws, azure, gcp, k8s."},
        },
        "required": [],
    }

    def build_command(self, args: dict) -> list[str]:
        cmd = ["terrascan", "scan", "-o", "json"]
        if d := args.get("directory"):
            cmd.extend(["-d", d])
        if iac := args.get("iac_type"):
            cmd.extend(["-i", iac])
        if policy := args.get("policy_type"):
            cmd.extend(["-t", policy])
        return cmd

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        try:
            data = json.loads(raw_output)
            for violation in data.get("results", {}).get("violations", []):
                findings.append({
                    "type": "iac_violation",
                    "rule_name": violation.get("rule_name", ""),
                    "severity": violation.get("severity", "MEDIUM"),
                    "resource": violation.get("resource_name", ""),
                    "file": violation.get("file", ""),
                    "description": violation.get("description", ""),
                })
        except json.JSONDecodeError:
            pass
        return findings
