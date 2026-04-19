"""Container security tools."""

import json

from app.tools.base import SecurityTool

CLOUD_IMAGE = "nullify-tools-cloud:latest"


class TrivyTool(SecurityTool):
    name = "trivy_scan"
    description = (
        "Container and filesystem vulnerability scanner. "
        "Scans Docker images, filesystems, and git repos for CVEs and misconfigs."
    )
    binary = "trivy"
    docker_image = CLOUD_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "target": {"type": "string", "description": "Scan target (image name, path, or repo URL)."},
            "scan_type": {"type": "string", "description": "Scan type: image, fs, repo, config (default: image)."},
            "severity": {"type": "string", "description": "Severity filter: CRITICAL,HIGH,MEDIUM,LOW."},
        },
        "required": ["target"],
    }

    def build_command(self, args: dict) -> list[str]:
        scan = args.get("scan_type", "image")
        cmd = ["trivy", scan, "-f", "json", "-q", args["target"]]
        if sev := args.get("severity"):
            cmd.extend(["--severity", sev])
        return cmd

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        try:
            data = json.loads(raw_output)
            for result in data.get("Results", []):
                for vuln in result.get("Vulnerabilities", []):
                    findings.append({
                        "type": "container_vulnerability",
                        "cve": vuln.get("VulnerabilityID", ""),
                        "package": vuln.get("PkgName", ""),
                        "severity": vuln.get("Severity", ""),
                        "title": vuln.get("Title", ""),
                        "installed": vuln.get("InstalledVersion", ""),
                        "fixed": vuln.get("FixedVersion", ""),
                    })
        except json.JSONDecodeError:
            pass
        return findings


class DockerBenchTool(SecurityTool):
    name = "docker_bench"
    description = "CIS Docker Benchmark security audit. Use to check Docker host and daemon configuration."
    binary = "docker-bench-security"
    docker_image = CLOUD_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "check": {"type": "string", "description": "Specific check number (e.g. '1', '2.1')."},
        },
        "required": [],
    }

    def build_command(self, args: dict) -> list[str]:
        cmd = ["docker-bench-security", "-l", "/dev/stdout"]
        if check := args.get("check"):
            cmd.extend(["-c", check])
        return cmd

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        for line in raw_output.splitlines():
            if "[WARN]" in line:
                findings.append({"type": "docker_misconfiguration", "detail": line.strip(), "severity": "MEDIUM"})
            elif "[FAIL]" in line:
                findings.append({"type": "docker_misconfiguration", "detail": line.strip(), "severity": "HIGH"})
        return findings
