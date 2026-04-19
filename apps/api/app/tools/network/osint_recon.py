"""OSINT reconnaissance tools — theHarvester."""

import re

from app.tools.base import SecurityTool

NETWORK_IMAGE = "nullify-tools-network:latest"


class TheHarvesterTool(SecurityTool):
    name = "theharvester_scan"
    description = (
        "Gather emails, subdomains, IPs, and URLs from public sources "
        "(search engines, PGP servers, Shodan, etc.). Use for passive "
        "OSINT reconnaissance to map out a target's public footprint."
    )
    binary = "theHarvester"
    docker_image = NETWORK_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "domain": {
                "type": "string",
                "description": "Target domain to search for.",
            },
            "source": {
                "type": "string",
                "description": (
                    "Data source to use (default 'all'). Options: "
                    "all, baidu, bing, certspotter, crtsh, dnsdumpster, "
                    "duckduckgo, google, hackertarget, otx, rapiddns, "
                    "sublist3r, threatcrowd, trello, twitter, urlscan, "
                    "virustotal, yahoo."
                ),
            },
        },
        "required": ["domain"],
    }

    def build_command(self, args: dict) -> list[str]:
        domain = args["domain"]
        source = args.get("source", "all")
        return ["theHarvester", "-d", domain, "-b", source]

    def parse_output(self, raw_output: str) -> list[dict]:
        findings: list[dict] = []

        # Extract emails
        email_pattern = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
        seen_emails: set[str] = set()
        for match in email_pattern.finditer(raw_output):
            email = match.group(0).lower()
            if email not in seen_emails:
                seen_emails.add(email)
                findings.append({"type": "email", "email": email})

        # Extract subdomains (lines that look like hostnames)
        in_hosts_section = False
        for line in raw_output.splitlines():
            line = line.strip()

            if "hosts found" in line.lower() or "[*] hosts" in line.lower():
                in_hosts_section = True
                continue
            if in_hosts_section and line.startswith("[*]"):
                in_hosts_section = False
                continue

            if in_hosts_section and line:
                # Lines like: subdomain.example.com:1.2.3.4
                parts = line.split(":")
                hostname = parts[0].strip()
                ip = parts[1].strip() if len(parts) > 1 else ""
                if "." in hostname and not hostname.startswith("["):
                    findings.append({
                        "type": "discovered_host",
                        "hostname": hostname,
                        "ip": ip,
                    })

        # Extract IPs
        in_ips_section = False
        for line in raw_output.splitlines():
            line = line.strip()
            if "[*] ips" in line.lower():
                in_ips_section = True
                continue
            if in_ips_section and line.startswith("[*]"):
                in_ips_section = False
                continue
            if in_ips_section and re.match(r"^\d+\.\d+\.\d+\.\d+$", line):
                findings.append({"type": "ip_address", "ip": line})

        return findings
