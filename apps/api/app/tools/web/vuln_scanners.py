"""Web vulnerability scanners."""

import json
import re

from app.tools.base import SecurityTool

WEB_IMAGE = "nullify-tools-web:latest"


class NiktoTool(SecurityTool):
    name = "nikto_scan"
    description = (
        "Web server vulnerability scanner. Detects dangerous files, outdated software, "
        "and server misconfigurations. Use for comprehensive web server auditing."
    )
    binary = "nikto"
    docker_image = WEB_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "target": {"type": "string", "description": "Target URL or host."},
            "tuning": {"type": "string", "description": "Scan tuning (e.g. '123' for interesting files, misconfigs, info disclosure)."},
        },
        "required": ["target"],
    }

    def build_command(self, args: dict) -> list[str]:
        cmd = ["nikto", "-h", args["target"], "-Format", "json", "-output", "/dev/stdout"]
        if tuning := args.get("tuning"):
            cmd.extend(["-Tuning", tuning])
        return cmd

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        try:
            data = json.loads(raw_output)
            for vuln in data.get("vulnerabilities", []):
                findings.append({
                    "type": "vulnerability",
                    "title": vuln.get("msg", ""),
                    "url": vuln.get("url", ""),
                    "method": vuln.get("method", ""),
                    "osvdb_id": vuln.get("OSVDB", ""),
                })
        except json.JSONDecodeError:
            for line in raw_output.splitlines():
                if "+ " in line and "OSVDB" in line:
                    findings.append({"type": "vulnerability", "title": line.strip()})
        return findings


class SqlmapTool(SecurityTool):
    name = "sqlmap_scan"
    description = (
        "Automatic SQL injection detection and exploitation. "
        "Use when you suspect SQL injection in URL parameters or POST data."
    )
    binary = "sqlmap"
    docker_image = WEB_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "Target URL with injectable parameter (e.g. http://target.com/page?id=1)."},
            "data": {"type": "string", "description": "POST data string (e.g. 'user=test&pass=test')."},
            "level": {"type": "integer", "description": "Testing level 1-5 (default: 3)."},
            "risk": {"type": "integer", "description": "Risk level 1-3 (default: 2)."},
        },
        "required": ["url"],
    }

    def build_command(self, args: dict) -> list[str]:
        cmd = ["sqlmap", "-u", args["url"],
               "--level", str(args.get("level", 3)),
               "--risk", str(args.get("risk", 2)),
               "--batch", "-v", "0", "--output-dir=/tmp/sqlmap"]
        if data := args.get("data"):
            cmd.extend(["--data", data])
        return cmd

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        injection_found = False
        for line in raw_output.splitlines():
            if "is vulnerable" in line.lower() or "injectable" in line.lower():
                injection_found = True
                findings.append({"type": "sql_injection", "detail": line.strip(), "severity": "CRITICAL"})
            elif "Type:" in line and injection_found:
                findings.append({"type": "sqli_technique", "detail": line.strip()})
            elif "Payload:" in line:
                findings.append({"type": "sqli_payload", "payload": line.split("Payload:")[-1].strip()})
        return findings


class WpscanTool(SecurityTool):
    name = "wpscan_scan"
    description = (
        "WordPress security scanner. Detects vulnerable plugins, themes, "
        "and WordPress core issues. Use on WordPress sites only."
    )
    binary = "wpscan"
    docker_image = WEB_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "WordPress site URL."},
            "enumerate": {"type": "string", "description": "Enumeration options (default: 'vp,vt,u' for plugins, themes, users)."},
            "api_token": {"type": "string", "description": "WPScan API token for vulnerability data."},
        },
        "required": ["url"],
    }

    def build_command(self, args: dict) -> list[str]:
        cmd = ["wpscan", "--url", args["url"],
               "-e", args.get("enumerate", "vp,vt,u"),
               "-f", "json", "--no-banner"]
        if token := args.get("api_token"):
            cmd.extend(["--api-token", token])
        return cmd

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        try:
            data = json.loads(raw_output)
            for vuln in data.get("plugins", {}).values():
                for v in vuln.get("vulnerabilities", []):
                    findings.append({
                        "type": "wordpress_vuln",
                        "title": v.get("title", ""),
                        "severity": v.get("severity", "MEDIUM"),
                        "references": v.get("references", {}),
                    })
            if version := data.get("version", {}):
                findings.append({"type": "wordpress_version", "version": version.get("number", ""), "status": version.get("status", "")})
        except json.JSONDecodeError:
            pass
        return findings


class JaelesTool(SecurityTool):
    name = "jaeles_scan"
    description = "Advanced vulnerability scanning with custom signatures. Use for targeted vulnerability checks."
    binary = "jaeles"
    docker_image = WEB_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "Target URL."},
            "sign": {"type": "string", "description": "Signature directory or specific signature."},
        },
        "required": ["url"],
    }

    def build_command(self, args: dict) -> list[str]:
        cmd = ["jaeles", "scan", "-u", args["url"]]
        if sign := args.get("sign"):
            cmd.extend(["-s", sign])
        return cmd

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        for line in raw_output.splitlines():
            line = line.strip()
            if line and "[Vulnerable]" in line:
                findings.append({"type": "vulnerability", "detail": line})
        return findings
