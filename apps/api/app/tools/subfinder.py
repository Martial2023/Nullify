"""Subfinder — Subdomain discovery tool."""

from app.tools.base import SecurityTool


class SubfinderTool(SecurityTool):
    name = "subfinder"
    description = (
        "Discover subdomains of a target domain using passive sources. "
        "Use this for reconnaissance to map the attack surface."
    )
    binary = "subfinder"
    docker_image = "projectdiscovery/subfinder:latest"
    docker_extra_args = ["-duc", "-nc"]
    parameters = {
        "type": "object",
        "properties": {
            "domain": {
                "type": "string",
                "description": "Target domain to enumerate subdomains for.",
            },
        },
        "required": ["domain"],
    }

    def build_command(self, args: dict) -> list[str]:
        return ["subfinder", "-d", args["domain"], "-silent"]

    def parse_output(self, raw_output: str) -> list[dict]:
        subdomains = [
            line.strip()
            for line in raw_output.splitlines()
            if line.strip()
        ]
        return [
            {"type": "subdomain", "subdomain": s}
            for s in subdomains
        ]
