"""SSL/TLS testing tools."""

import json

from app.tools.base import SecurityTool

WEB_IMAGE = "nullify-tools-web:latest"


class TestsslTool(SecurityTool):
    name = "testssl_scan"
    description = (
        "Comprehensive SSL/TLS configuration tester. Checks ciphers, protocols, "
        "vulnerabilities (Heartbleed, POODLE, etc). Use for TLS auditing."
    )
    binary = "testssl"
    docker_image = WEB_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "target": {"type": "string", "description": "Target host:port (e.g. example.com:443)."},
            "full": {"type": "boolean", "description": "Run all checks (default: true)."},
        },
        "required": ["target"],
    }

    def build_command(self, args: dict) -> list[str]:
        # testssl.sh checks for TTY — wrap in bash with TERM=dumb to avoid "not a tty"
        flags = "--jsonfile /dev/stdout --quiet --color 0 --sneaky"
        if args.get("full", True):
            flags += " --full"
        target = args["target"]
        return ["bash", "-c", f"export TERM=dumb; testssl {flags} {target}"]

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        try:
            data = json.loads(raw_output)
            for entry in data if isinstance(data, list) else [data]:
                severity = entry.get("severity", "INFO")
                if severity in ("CRITICAL", "HIGH", "MEDIUM", "WARN"):
                    findings.append({
                        "type": "tls_issue",
                        "id": entry.get("id", ""),
                        "finding": entry.get("finding", ""),
                        "severity": severity,
                        "cve": entry.get("cve", ""),
                    })
        except json.JSONDecodeError:
            for line in raw_output.splitlines():
                if "VULNERABLE" in line or "NOT ok" in line:
                    findings.append({"type": "tls_issue", "detail": line.strip()})
        return findings


class SslscanTool(SecurityTool):
    name = "sslscan_scan"
    description = "SSL/TLS scanner — checks supported ciphers and certificate info. Use for quick TLS checks."
    binary = "sslscan"
    docker_image = WEB_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "target": {"type": "string", "description": "Target host:port."},
        },
        "required": ["target"],
    }

    def build_command(self, args: dict) -> list[str]:
        return ["sslscan", "--no-colour", args["target"]]

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        for line in raw_output.splitlines():
            line = line.strip()
            if not line:
                continue
            if "Accepted" in line and ("SSLv" in line or "TLSv1.0" in line or "TLSv1.1" in line):
                findings.append({"type": "weak_protocol", "detail": line})
            elif "Accepted" in line and ("RC4" in line or "DES" in line or "NULL" in line or "EXPORT" in line):
                findings.append({"type": "weak_cipher", "detail": line})
            elif "expired" in line.lower() or "self-signed" in line.lower():
                findings.append({"type": "certificate_issue", "detail": line})
        return findings


class SslyzeTool(SecurityTool):
    name = "sslyze_scan"
    description = "Python-based SSL/TLS scanner with detailed certificate analysis. Use for programmatic TLS auditing."
    binary = "sslyze"
    docker_image = WEB_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "target": {"type": "string", "description": "Target host:port."},
        },
        "required": ["target"],
    }

    def build_command(self, args: dict) -> list[str]:
        return ["sslyze", "--json_out=/dev/stdout", "--quiet", args["target"]]

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        try:
            data = json.loads(raw_output)
            for result in data.get("server_scan_results", []):
                cmds = result.get("scan_commands_results", {})
                if heartbleed := cmds.get("heartbleed"):
                    if heartbleed.get("is_vulnerable_to_heartbleed"):
                        findings.append({"type": "tls_vulnerability", "name": "Heartbleed", "severity": "CRITICAL"})
                if robot := cmds.get("robot"):
                    if "VULNERABLE" in str(robot.get("robot_result", "")):
                        findings.append({"type": "tls_vulnerability", "name": "ROBOT", "severity": "HIGH"})
                if ccs := cmds.get("openssl_ccs_injection"):
                    if ccs.get("is_vulnerable_to_ccs_injection"):
                        findings.append({"type": "tls_vulnerability", "name": "CCS Injection", "severity": "HIGH"})
        except json.JSONDecodeError:
            pass
        return findings
