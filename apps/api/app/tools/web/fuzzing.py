"""Web fuzzing tools."""

import json

from app.tools.base import SecurityTool

WEB_IMAGE = "nullify-tools-web:latest"


class WfuzzTool(SecurityTool):
    name = "wfuzz_scan"
    description = (
        "Versatile web fuzzer for directories, parameters, headers, and more. "
        "Use FUZZ keyword as the injection point. Supports multiple encoders."
    )
    binary = "wfuzz"
    docker_image = WEB_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "Target URL with FUZZ keyword."},
            "wordlist": {"type": "string", "description": "Wordlist path."},
            "hc": {"type": "string", "description": "Hide responses with these status codes (e.g. '404,403')."},
            "hw": {"type": "string", "description": "Hide responses with this word count."},
            "method": {"type": "string", "description": "HTTP method (default: GET)."},
            "header": {"type": "string", "description": "Custom header (e.g. 'Cookie: session=abc')."},
            "data": {"type": "string", "description": "POST data with FUZZ keyword."},
        },
        "required": ["url"],
    }

    def build_command(self, args: dict) -> list[str]:
        cmd = ["wfuzz",
               "-w", args.get("wordlist", "/usr/share/wordlists/dirb/common.txt"),
               "-o", "json", "--no-color"]
        if hc := args.get("hc"):
            cmd.extend(["--hc", hc])
        if hw := args.get("hw"):
            cmd.extend(["--hw", hw])
        if method := args.get("method"):
            cmd.extend(["-X", method])
        if header := args.get("header"):
            cmd.extend(["-H", header])
        if data := args.get("data"):
            cmd.extend(["-d", data])
        cmd.append(args["url"])
        return cmd

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        try:
            data = json.loads(raw_output)
            for result in data if isinstance(data, list) else data.get("results", []):
                findings.append({
                    "type": "fuzz_result",
                    "payload": result.get("payload", ""),
                    "status_code": result.get("code", 0),
                    "words": result.get("words", 0),
                    "lines": result.get("lines", 0),
                    "chars": result.get("chars", 0),
                })
        except json.JSONDecodeError:
            for line in raw_output.splitlines():
                line = line.strip()
                if line and not line.startswith("=") and "Target" not in line:
                    findings.append({"type": "fuzz_result", "detail": line})
        return findings
