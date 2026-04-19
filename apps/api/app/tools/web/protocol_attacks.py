"""HTTP protocol attack tools (CRLF, CORS, SSRF, smuggling)."""

import json

from app.tools.base import SecurityTool

WEB_IMAGE = "nullify-tools-web:latest"


class CrlfuzzTool(SecurityTool):
    name = "crlfuzz_scan"
    description = "CRLF injection scanner. Detects HTTP response splitting vulnerabilities."
    binary = "crlfuzz"
    docker_image = WEB_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "Target URL."},
        },
        "required": ["url"],
    }

    def build_command(self, args: dict) -> list[str]:
        return ["crlfuzz", "-u", args["url"], "-s"]

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        for line in raw_output.splitlines():
            line = line.strip()
            if line and line.startswith("http"):
                findings.append({"type": "crlf_injection", "url": line, "severity": "HIGH"})
        return findings


class CorsScannerTool(SecurityTool):
    name = "cors_scan"
    description = "CORS misconfiguration scanner. Detects overly permissive cross-origin policies."
    binary = "cors-scanner"
    docker_image = WEB_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "Target URL."},
        },
        "required": ["url"],
    }

    def build_command(self, args: dict) -> list[str]:
        return ["python3", "/opt/CORScanner/cors_scan.py", "-u", args["url"]]

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        for line in raw_output.splitlines():
            line = line.strip()
            if "vulnerable" in line.lower() or "misconfigur" in line.lower():
                findings.append({"type": "cors_misconfiguration", "detail": line, "severity": "HIGH"})
        return findings


class SsrfSheriffTool(SecurityTool):
    name = "ssrf_scan"
    description = "SSRF (Server-Side Request Forgery) detection tool. Use when parameters accept URLs."
    binary = "ssrf-sheriff"
    docker_image = WEB_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "Target URL with parameter to test."},
            "callback": {"type": "string", "description": "Callback URL to detect SSRF."},
        },
        "required": ["url"],
    }

    def build_command(self, args: dict) -> list[str]:
        cmd = ["python3", "/opt/ssrf-sheriff/ssrf_sheriff.py", "-u", args["url"]]
        if callback := args.get("callback"):
            cmd.extend(["--callback", callback])
        return cmd

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        for line in raw_output.splitlines():
            if "ssrf" in line.lower() or "vulnerable" in line.lower():
                findings.append({"type": "ssrf_vulnerability", "detail": line.strip(), "severity": "CRITICAL"})
        return findings


class SmugglerTool(SecurityTool):
    name = "smuggler_scan"
    description = (
        "HTTP request smuggling scanner. Detects CL-TE, TE-CL, and TE-TE desync vulnerabilities."
    )
    binary = "smuggler"
    docker_image = WEB_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "Target URL."},
        },
        "required": ["url"],
    }

    def build_command(self, args: dict) -> list[str]:
        return ["python3", "/opt/smuggler/smuggler.py", "-u", args["url"]]

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        for line in raw_output.splitlines():
            line = line.strip()
            if "VULNERABLE" in line.upper() or "desync" in line.lower():
                findings.append({"type": "http_smuggling", "detail": line, "severity": "CRITICAL"})
            elif "CL-TE" in line or "TE-CL" in line or "TE-TE" in line:
                findings.append({"type": "smuggling_technique", "detail": line})
        return findings
