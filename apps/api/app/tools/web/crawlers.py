"""Web crawlers and URL discovery tools."""

import json

from app.tools.base import SecurityTool

WEB_IMAGE = "nullify-tools-web:latest"


class KatanaTool(SecurityTool):
    name = "katana_crawl"
    description = (
        "Next-generation web crawler with JavaScript rendering support. "
        "Use for deep crawling modern JS-heavy web applications."
    )
    binary = "katana"
    docker_image = WEB_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "Target URL to crawl."},
            "depth": {"type": "integer", "description": "Crawl depth (default: 3)."},
            "js_crawl": {"type": "boolean", "description": "Enable JavaScript crawling (default: true)."},
        },
        "required": ["url"],
    }

    def build_command(self, args: dict) -> list[str]:
        cmd = ["katana", "-u", args["url"], "-d", str(args.get("depth", 3)),
               "-silent", "-nc", "-jsonl"]
        if args.get("js_crawl", True):
            cmd.append("-jc")
        return cmd

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        for line in raw_output.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                findings.append({
                    "type": "discovered_url",
                    "url": data.get("request", {}).get("endpoint", line),
                    "method": data.get("request", {}).get("method", "GET"),
                    "source": data.get("request", {}).get("source", ""),
                })
            except json.JSONDecodeError:
                if line.startswith("http"):
                    findings.append({"type": "discovered_url", "url": line})
        return findings


class HakrawlerTool(SecurityTool):
    name = "hakrawler_crawl"
    description = "Fast web endpoint discovery and crawling. Use for quick URL extraction from a target."
    binary = "hakrawler"
    docker_image = WEB_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "Target URL."},
            "depth": {"type": "integer", "description": "Crawl depth (default: 2)."},
        },
        "required": ["url"],
    }

    def build_command(self, args: dict) -> list[str]:
        url = args["url"]
        depth = args.get("depth", 2)
        return ["sh", "-c", f"echo '{url}' | hakrawler -d {depth} -plain"]

    def parse_output(self, raw_output: str) -> list[dict]:
        return [
            {"type": "discovered_url", "url": line.strip()}
            for line in raw_output.splitlines()
            if line.strip() and line.strip().startswith("http")
        ]


class GauTool(SecurityTool):
    name = "gau_urls"
    description = (
        "Fetch known URLs from Wayback Machine, Common Crawl, and other sources. "
        "Use for passive URL discovery without touching the target."
    )
    binary = "gau"
    docker_image = WEB_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "domain": {"type": "string", "description": "Target domain."},
        },
        "required": ["domain"],
    }

    def build_command(self, args: dict) -> list[str]:
        return ["gau", args["domain"], "--mc", "200,301,302"]

    def parse_output(self, raw_output: str) -> list[dict]:
        return [
            {"type": "archived_url", "url": line.strip()}
            for line in raw_output.splitlines()
            if line.strip()
        ]


class WaybackUrlsTool(SecurityTool):
    name = "waybackurls_fetch"
    description = "Fetch historical URLs from the Wayback Machine. Use for passive recon of past endpoints."
    binary = "waybackurls"
    docker_image = WEB_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "domain": {"type": "string", "description": "Target domain."},
        },
        "required": ["domain"],
    }

    def build_command(self, args: dict) -> list[str]:
        return ["sh", "-c", f"echo '{args['domain']}' | waybackurls"]

    def parse_output(self, raw_output: str) -> list[dict]:
        return [
            {"type": "archived_url", "url": line.strip()}
            for line in raw_output.splitlines()
            if line.strip()
        ]
