"""Metadata extraction tools."""

import json

from app.tools.base import SecurityTool

FORENSICS_IMAGE = "nullify-tools-forensics:latest"


class ExiftoolTool(SecurityTool):
    name = "exiftool_extract"
    description = (
        "Extract metadata from files (images, documents, PDFs, videos). "
        "Use for OSINT, finding GPS coordinates, author names, software versions."
    )
    binary = "exiftool"
    docker_image = FORENSICS_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "file_path": {"type": "string", "description": "Path to the file."},
            "tags": {"type": "string", "description": "Specific tags to extract (comma-separated)."},
        },
        "required": ["file_path"],
    }

    def build_command(self, args: dict) -> list[str]:
        cmd = ["exiftool", "-j"]
        if tags := args.get("tags"):
            for tag in tags.split(","):
                cmd.append(f"-{tag.strip()}")
        cmd.append(args["file_path"])
        return cmd

    def parse_output(self, raw_output: str) -> list[dict]:
        try:
            data = json.loads(raw_output)
            return [{"type": "metadata", "data": entry} for entry in data]
        except json.JSONDecodeError:
            return [{"type": "metadata", "raw": raw_output.strip()}]
