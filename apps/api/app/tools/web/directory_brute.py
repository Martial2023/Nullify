"""Directory and file enumeration tools."""

import json
import re

from app.tools.base import SecurityTool

WEB_IMAGE = "nullify-tools-web:latest"


class GobusterTool(SecurityTool):
    name = "gobuster_scan"
    description = (
        "Directory and file enumeration using wordlists. "
        "Use for discovering hidden paths, files, and directories on web servers."
    )
    binary = "gobuster"
    docker_image = WEB_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "Target URL (e.g. http://target.com)."},
            "wordlist": {"type": "string", "description": "Wordlist path (default: /usr/share/wordlists/dirb/common.txt)."},
            "extensions": {"type": "string", "description": "File extensions to search (e.g. 'php,html,txt,js')."},
            "mode": {"type": "string", "enum": ["dir", "dns", "vhost"], "description": "Scan mode (default: dir)."},
        },
        "required": ["url"],
    }

    def build_command(self, args: dict) -> list[str]:
        mode = args.get("mode", "dir")
        cmd = ["gobuster", mode, "-u", args["url"],
               "-w", args.get("wordlist", "/usr/share/wordlists/dirb/common.txt"),
               "-q", "--no-color"]
        if ext := args.get("extensions"):
            cmd.extend(["-x", ext])
        return cmd

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        for line in raw_output.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            match = re.match(r"(/\S+)\s+\(Status:\s*(\d+)\)", line)
            if match:
                findings.append({"type": "discovered_path", "path": match.group(1), "status_code": int(match.group(2))})
            elif line.startswith("/"):
                findings.append({"type": "discovered_path", "path": line.split()[0]})
        return findings


class FeroxbusterTool(SecurityTool):
    name = "feroxbuster_scan"
    description = (
        "Recursive content discovery with intelligent filtering. "
        "Use for thorough directory brute-forcing with auto-recursion."
    )
    binary = "feroxbuster"
    docker_image = WEB_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "Target URL."},
            "wordlist": {"type": "string", "description": "Wordlist path."},
            "depth": {"type": "integer", "description": "Recursion depth (default: 2)."},
            "extensions": {"type": "string", "description": "Extensions to search."},
        },
        "required": ["url"],
    }

    def build_command(self, args: dict) -> list[str]:
        cmd = ["feroxbuster", "-u", args["url"],
               "-w", args.get("wordlist", "/usr/share/wordlists/dirb/common.txt"),
               "-d", str(args.get("depth", 2)), "--silent", "--json"]
        if ext := args.get("extensions"):
            cmd.extend(["-x", ext])
        return cmd

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        for line in raw_output.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                if data.get("type") == "response":
                    findings.append({
                        "type": "discovered_path",
                        "url": data.get("url", ""),
                        "status_code": data.get("status", 0),
                        "content_length": data.get("content_length", 0),
                    })
            except json.JSONDecodeError:
                continue
        return findings


class FfufTool(SecurityTool):
    name = "ffuf_scan"
    description = (
        "Fast web fuzzer for directory discovery, parameter fuzzing, and vhost detection. "
        "Use FUZZ keyword in URL for the injection point."
    )
    binary = "ffuf"
    docker_image = WEB_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "Target URL with FUZZ keyword (e.g. http://target/FUZZ)."},
            "wordlist": {"type": "string", "description": "Wordlist path."},
            "mc": {"type": "string", "description": "Match HTTP status codes (default: '200,301,302,403')."},
            "method": {"type": "string", "description": "HTTP method (default: GET)."},
        },
        "required": ["url"],
    }

    def build_command(self, args: dict) -> list[str]:
        return [
            "ffuf", "-u", args["url"],
            "-w", args.get("wordlist", "/usr/share/wordlists/dirb/common.txt"),
            "-mc", args.get("mc", "200,301,302,403"),
            "-X", args.get("method", "GET"),
            "-o", "/dev/stdout", "-of", "json", "-s",
        ]

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        try:
            data = json.loads(raw_output)
            for result in data.get("results", []):
                findings.append({
                    "type": "discovered_path",
                    "url": result.get("url", ""),
                    "status_code": result.get("status", 0),
                    "content_length": result.get("length", 0),
                    "input": result.get("input", {}).get("FUZZ", ""),
                })
        except json.JSONDecodeError:
            pass
        return findings


class DirsearchTool(SecurityTool):
    name = "dirsearch_scan"
    description = (
        "Advanced directory and file discovery with enhanced logging. "
        "Use for web content enumeration with smart filtering."
    )
    binary = "dirsearch"
    docker_image = WEB_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "Target URL."},
            "extensions": {"type": "string", "description": "Extensions to search (e.g. 'php,html')."},
            "wordlist": {"type": "string", "description": "Custom wordlist path."},
        },
        "required": ["url"],
    }

    def build_command(self, args: dict) -> list[str]:
        cmd = ["dirsearch", "-u", args["url"], "--format=json", "-o", "/dev/stdout", "-q"]
        if ext := args.get("extensions"):
            cmd.extend(["-e", ext])
        if wl := args.get("wordlist"):
            cmd.extend(["--wordlist", wl])
        return cmd

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        try:
            data = json.loads(raw_output)
            for result in data.get("results", []):
                findings.append({
                    "type": "discovered_path",
                    "url": result.get("url", ""),
                    "status_code": result.get("status", 0),
                })
        except json.JSONDecodeError:
            pass
        return findings


class DirbTool(SecurityTool):
    name = "dirb_scan"
    description = "Web content scanner with recursive scanning. Use for basic directory enumeration."
    binary = "dirb"
    docker_image = WEB_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "Target URL."},
            "wordlist": {"type": "string", "description": "Wordlist path."},
        },
        "required": ["url"],
    }

    def build_command(self, args: dict) -> list[str]:
        return ["dirb", args["url"], args.get("wordlist", "/usr/share/wordlists/dirb/common.txt"), "-S"]

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        for line in raw_output.splitlines():
            if line.strip().startswith("+ http"):
                parts = line.strip().split()
                if len(parts) >= 2:
                    findings.append({"type": "discovered_path", "url": parts[1]})
        return findings
