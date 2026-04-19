"""API security testing tools."""

import json

from app.tools.base import SecurityTool

WEB_IMAGE = "nullify-tools-web:latest"


class JwtToolTool(SecurityTool):
    name = "jwt_tool_scan"
    description = (
        "JWT (JSON Web Token) security testing. Tests for algorithm confusion, "
        "key brute-force, claim tampering, and known CVEs. Use when JWTs are in scope."
    )
    binary = "jwt_tool"
    docker_image = WEB_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "token": {"type": "string", "description": "JWT token to test."},
            "mode": {"type": "string", "description": "Attack mode: at (all tests), pb (playbook). Default: at."},
            "target_url": {"type": "string", "description": "URL to test the forged tokens against."},
        },
        "required": ["token"],
    }

    def build_command(self, args: dict) -> list[str]:
        cmd = ["python3", "/opt/jwt_tool/jwt_tool.py", args["token"],
               "-M", args.get("mode", "at"), "--bare"]
        if url := args.get("target_url"):
            cmd.extend(["-t", url])
        return cmd

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        for line in raw_output.splitlines():
            line = line.strip()
            if not line:
                continue
            if "VULNERABLE" in line.upper() or "EXPLOIT" in line.upper():
                findings.append({"type": "jwt_vulnerability", "detail": line, "severity": "HIGH"})
            elif "alg" in line.lower() and "none" in line.lower():
                findings.append({"type": "jwt_vulnerability", "detail": "Algorithm None accepted", "severity": "CRITICAL"})
            elif line.startswith("eyJ"):
                findings.append({"type": "jwt_forged_token", "token": line})
        return findings


class GraphqlVoyagerTool(SecurityTool):
    name = "graphql_scan"
    description = (
        "GraphQL endpoint introspection and security testing. "
        "Detects exposed schemas, injection points, and misconfigurations."
    )
    binary = "graphql-cop"
    docker_image = WEB_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "GraphQL endpoint URL."},
        },
        "required": ["url"],
    }

    def build_command(self, args: dict) -> list[str]:
        return ["python3", "-m", "graphql_cop", "-t", args["url"]]

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        for line in raw_output.splitlines():
            line = line.strip()
            if not line:
                continue
            if "FOUND" in line.upper() or "DETECTED" in line.upper():
                severity = "HIGH" if "injection" in line.lower() or "introspection" in line.lower() else "MEDIUM"
                findings.append({"type": "graphql_issue", "detail": line, "severity": severity})
        return findings
