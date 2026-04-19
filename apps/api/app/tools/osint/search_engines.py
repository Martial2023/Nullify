"""Search engine and data aggregation OSINT tools."""

import json

from app.tools.base import SecurityTool

OSINT_IMAGE = "nullify-tools-osint:latest"


class ShodanTool(SecurityTool):
    name = "shodan_search"
    description = "Search Shodan for internet-connected devices. Use for passive recon of exposed services."
    binary = "shodan"
    docker_image = OSINT_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Shodan search query or IP address."},
            "command": {"type": "string", "description": "Command: search, host, info (default: search)."},
            "api_key": {"type": "string", "description": "Shodan API key."},
        },
        "required": ["query"],
    }

    def build_command(self, args: dict) -> list[str]:
        cmd_type = args.get("command", "search")
        cmd = ["shodan"]
        if api_key := args.get("api_key"):
            cmd = ["sh", "-c", f"shodan init {api_key} && shodan {cmd_type} {args['query']}"]
        else:
            cmd = ["shodan", cmd_type, args["query"]]
        return cmd

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        for line in raw_output.splitlines():
            line = line.strip()
            if line:
                findings.append({"type": "shodan_result", "data": line})
        return findings


class CensysTool(SecurityTool):
    name = "censys_search"
    description = "Search Censys for internet host data. Use for discovering certificates, services, and hosts."
    binary = "censys"
    docker_image = OSINT_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Censys search query."},
            "index": {"type": "string", "description": "Index: hosts, certificates (default: hosts)."},
        },
        "required": ["query"],
    }

    def build_command(self, args: dict) -> list[str]:
        index = args.get("index", "hosts")
        return ["censys", "search", args["query"], "--index-type", index, "-o", "json"]

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        for line in raw_output.splitlines():
            try:
                data = json.loads(line)
                findings.append({"type": "censys_result", "data": data})
            except json.JSONDecodeError:
                if line.strip():
                    findings.append({"type": "censys_result", "data": line.strip()})
        return findings


class HaveIBeenPwnedTool(SecurityTool):
    name = "hibp_check"
    description = "Check if email/domain has been in data breaches. Use for credential exposure assessment."
    binary = "python3"
    docker_image = OSINT_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "email": {"type": "string", "description": "Email address to check."},
            "domain": {"type": "string", "description": "Domain to check for breaches."},
            "api_key": {"type": "string", "description": "HIBP API key."},
        },
        "required": [],
    }

    def build_command(self, args: dict) -> list[str]:
        target = args.get("email") or args.get("domain", "")
        endpoint = "breachedaccount" if args.get("email") else "breaches"
        api_key = args.get("api_key", "")
        script = (
            f"import urllib.request,json; "
            f"req=urllib.request.Request("
            f"'https://haveibeenpwned.com/api/v3/{endpoint}/{target}', "
            f"headers={{'hibp-api-key':'{api_key}','user-agent':'nullify'}}); "
            f"r=urllib.request.urlopen(req); print(r.read().decode())"
        )
        return ["python3", "-c", script]

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        try:
            data = json.loads(raw_output)
            for breach in data if isinstance(data, list) else [data]:
                findings.append({
                    "type": "data_breach",
                    "name": breach.get("Name", ""),
                    "date": breach.get("BreachDate", ""),
                    "count": breach.get("PwnCount", 0),
                    "data_classes": breach.get("DataClasses", []),
                })
        except json.JSONDecodeError:
            pass
        return findings
