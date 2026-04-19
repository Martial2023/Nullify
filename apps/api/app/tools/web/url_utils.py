"""URL manipulation and deduplication utilities."""

from app.tools.base import SimpleTool

WEB_IMAGE = "nullify-tools-web:latest"


class AnewTool(SimpleTool):
    name = "anew_dedup"
    description = "Append lines from stdin to a file, skipping duplicates. Use for URL list deduplication."
    binary = "anew"
    docker_image = WEB_IMAGE
    finding_type = "unique_url"
    parameters = {
        "type": "object",
        "properties": {
            "input_data": {"type": "string", "description": "Newline-separated URLs to deduplicate."},
        },
        "required": ["input_data"],
    }

    def build_command(self, args: dict) -> list[str]:
        data = args["input_data"].replace("'", "'\\''")
        return ["sh", "-c", f"echo '{data}' | anew"]

    def parse_output(self, raw_output: str) -> list[dict]:
        return [
            {"type": "unique_url", "url": line.strip()}
            for line in raw_output.splitlines()
            if line.strip()
        ]


class QsreplaceTool(SimpleTool):
    name = "qsreplace"
    description = "Replace query string parameter values in URLs. Use for preparing fuzzing targets."
    binary = "qsreplace"
    docker_image = WEB_IMAGE
    finding_type = "modified_url"
    parameters = {
        "type": "object",
        "properties": {
            "urls": {"type": "string", "description": "Newline-separated URLs."},
            "value": {"type": "string", "description": "Replacement value for all parameters (default: FUZZ)."},
        },
        "required": ["urls"],
    }

    def build_command(self, args: dict) -> list[str]:
        urls = args["urls"].replace("'", "'\\''")
        value = args.get("value", "FUZZ")
        return ["sh", "-c", f"echo '{urls}' | qsreplace '{value}'"]

    def parse_output(self, raw_output: str) -> list[dict]:
        return [
            {"type": "modified_url", "url": line.strip()}
            for line in raw_output.splitlines()
            if line.strip()
        ]


class UroTool(SimpleTool):
    name = "uro_filter"
    description = "Filter and deduplicate URL lists by removing similar/redundant URLs. Use after crawling."
    binary = "uro"
    docker_image = WEB_IMAGE
    finding_type = "filtered_url"
    parameters = {
        "type": "object",
        "properties": {
            "urls": {"type": "string", "description": "Newline-separated URLs to filter."},
        },
        "required": ["urls"],
    }

    def build_command(self, args: dict) -> list[str]:
        urls = args["urls"].replace("'", "'\\''")
        return ["sh", "-c", f"echo '{urls}' | uro"]

    def parse_output(self, raw_output: str) -> list[dict]:
        return [
            {"type": "filtered_url", "url": line.strip()}
            for line in raw_output.splitlines()
            if line.strip()
        ]
