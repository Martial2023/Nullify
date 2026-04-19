"""Parameter discovery tools."""

import json

from app.tools.base import SecurityTool

WEB_IMAGE = "nullify-tools-web:latest"


class ArjunTool(SecurityTool):
    name = "arjun_scan"
    description = (
        "HTTP parameter discovery suite. Finds hidden GET/POST parameters "
        "in web applications. Use when you suspect hidden parameters."
    )
    binary = "arjun"
    docker_image = WEB_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "Target URL."},
            "method": {"type": "string", "description": "HTTP method: GET, POST, JSON (default: GET)."},
            "wordlist": {"type": "string", "description": "Custom wordlist path."},
        },
        "required": ["url"],
    }

    def build_command(self, args: dict) -> list[str]:
        cmd = ["arjun", "-u", args["url"], "-oJ", "/dev/stdout"]
        if method := args.get("method"):
            cmd.extend(["-m", method])
        if wl := args.get("wordlist"):
            cmd.extend(["-w", wl])
        return cmd

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        try:
            data = json.loads(raw_output)
            for url, params in data.items():
                for param in params:
                    findings.append({"type": "hidden_parameter", "url": url, "parameter": param})
        except json.JSONDecodeError:
            for line in raw_output.splitlines():
                line = line.strip()
                if line and not line.startswith("["):
                    findings.append({"type": "hidden_parameter", "parameter": line})
        return findings


class ParamSpiderTool(SecurityTool):
    name = "paramspider_scan"
    description = "Mine parameters from web archives for a domain. Use for passive parameter discovery."
    binary = "paramspider"
    docker_image = WEB_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "domain": {"type": "string", "description": "Target domain."},
        },
        "required": ["domain"],
    }

    def build_command(self, args: dict) -> list[str]:
        return ["paramspider", "-d", args["domain"], "--level", "high", "-o", "/dev/stdout"]

    def parse_output(self, raw_output: str) -> list[dict]:
        return [
            {"type": "parameterized_url", "url": line.strip()}
            for line in raw_output.splitlines()
            if line.strip() and line.strip().startswith("http")
        ]


class X8Tool(SecurityTool):
    name = "x8_scan"
    description = "Hidden parameter discovery with smart detection. Use for finding hidden API parameters."
    binary = "x8"
    docker_image = WEB_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "Target URL."},
            "wordlist": {"type": "string", "description": "Parameter wordlist."},
            "method": {"type": "string", "description": "HTTP method (default: GET)."},
        },
        "required": ["url"],
    }

    def build_command(self, args: dict) -> list[str]:
        cmd = ["x8", "-u", args["url"],
               "-w", args.get("wordlist", "/usr/share/wordlists/params.txt")]
        if method := args.get("method"):
            cmd.extend(["-X", method])
        return cmd

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        for line in raw_output.splitlines():
            line = line.strip()
            if line and "Found" in line:
                findings.append({"type": "hidden_parameter", "detail": line})
        return findings
