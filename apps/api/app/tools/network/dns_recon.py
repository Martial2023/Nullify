"""DNS reconnaissance tools — Amass, Fierce, DnsEnum, DnsRecon, Whois."""

import json
import re

from app.tools.base import SecurityTool

NETWORK_IMAGE = "nullify-tools-network:latest"


class AmassTool(SecurityTool):
    name = "amass_recon"
    description = (
        "Advanced subdomain enumeration using passive and active techniques "
        "with OSINT sources. Use when you need thorough subdomain discovery "
        "beyond what subfinder provides."
    )
    binary = "amass"
    docker_image = NETWORK_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "domain": {
                "type": "string",
                "description": "Target domain to enumerate subdomains for.",
            },
            "passive": {
                "type": "boolean",
                "description": "Use passive-only mode (no DNS resolution). Default true.",
            },
        },
        "required": ["domain"],
    }

    def build_command(self, args: dict) -> list[str]:
        domain = args["domain"]
        passive = args.get("passive", True)

        cmd = ["amass", "enum", "-d", domain]
        if passive:
            cmd.append("-passive")
        return cmd

    def parse_output(self, raw_output: str) -> list[dict]:
        return [
            {"type": "subdomain", "subdomain": line.strip()}
            for line in raw_output.splitlines()
            if line.strip() and not line.startswith(("OWASP", "The", "http", "----"))
        ]


class FierceTool(SecurityTool):
    name = "fierce_scan"
    description = (
        "DNS reconnaissance tool for zone transfer testing and subdomain "
        "discovery via brute-force. Use to find non-contiguous IP space "
        "and hostnames against specified domains."
    )
    binary = "fierce"
    docker_image = NETWORK_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "domain": {
                "type": "string",
                "description": "Target domain to scan.",
            },
        },
        "required": ["domain"],
    }

    def build_command(self, args: dict) -> list[str]:
        return ["fierce", "--domain", args["domain"]]

    def parse_output(self, raw_output: str) -> list[dict]:
        findings: list[dict] = []
        # Fierce outputs lines like: "Found: hostname.example.com (1.2.3.4)"
        host_pattern = re.compile(r"(\S+\.[\w.-]+)\s*\(?([\d.]+)\)?")
        for line in raw_output.splitlines():
            line = line.strip()
            if not line or line.startswith(("#", "!", "---")):
                continue
            match = host_pattern.search(line)
            if match:
                hostname, ip = match.groups()
                findings.append({
                    "type": "discovered_host",
                    "hostname": hostname,
                    "ip": ip,
                })
        return findings


class DnsEnumTool(SecurityTool):
    name = "dns_enum"
    description = (
        "DNS information gathering including zone transfers, brute forcing, "
        "and reverse lookups. Use for comprehensive DNS enumeration of a domain."
    )
    binary = "dnsenum"
    docker_image = NETWORK_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "domain": {
                "type": "string",
                "description": "Target domain to enumerate.",
            },
        },
        "required": ["domain"],
    }

    def build_command(self, args: dict) -> list[str]:
        return ["dnsenum", args["domain"]]

    def parse_output(self, raw_output: str) -> list[dict]:
        findings: list[dict] = []
        # Extract DNS records (A, NS, MX, etc.)
        record_pattern = re.compile(
            r"(\S+)\s+\d+\s+IN\s+(A|AAAA|NS|MX|CNAME|TXT|SOA)\s+(.*)"
        )
        for match in record_pattern.finditer(raw_output):
            name, rtype, value = match.groups()
            findings.append({
                "type": "dns_record",
                "name": name,
                "record_type": rtype,
                "value": value.strip(),
            })
        return findings


class DnsReconTool(SecurityTool):
    name = "dnsrecon_scan"
    description = (
        "DNS reconnaissance with zone transfer, cache snooping, and "
        "record enumeration. Outputs structured JSON for easy processing. "
        "Use for detailed DNS analysis."
    )
    binary = "dnsrecon"
    docker_image = NETWORK_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "domain": {
                "type": "string",
                "description": "Target domain to scan.",
            },
            "type": {
                "type": "string",
                "enum": ["std", "brt", "axfr"],
                "description": "Scan type: std (standard), brt (brute-force), axfr (zone transfer).",
            },
        },
        "required": ["domain"],
    }

    def build_command(self, args: dict) -> list[str]:
        domain = args["domain"]
        scan_type = args.get("type", "std")
        return ["dnsrecon", "-d", domain, "-t", scan_type, "-j", "/dev/stdout"]

    def parse_output(self, raw_output: str) -> list[dict]:
        try:
            data = json.loads(raw_output)
            if isinstance(data, list):
                return [
                    {"type": "dns_record", **entry}
                    for entry in data
                ]
            return [{"type": "dns_record", **data}]
        except json.JSONDecodeError:
            # Fallback to line-based parsing
            return [
                {"type": "dns_result", "data": line.strip()}
                for line in raw_output.splitlines()
                if line.strip()
            ]


class WhoisTool(SecurityTool):
    name = "whois_lookup"
    description = (
        "WHOIS lookups for domain registration info, registrar, nameservers, "
        "and expiry dates. Use to gather registration and ownership details "
        "about a target domain or IP."
    )
    binary = "whois"
    docker_image = NETWORK_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "target": {
                "type": "string",
                "description": "Domain name or IP address to look up.",
            },
        },
        "required": ["target"],
    }

    def build_command(self, args: dict) -> list[str]:
        return ["whois", args["target"]]

    def parse_output(self, raw_output: str) -> list[dict]:
        return [{"type": "whois_info", "data": raw_output.strip()}]
