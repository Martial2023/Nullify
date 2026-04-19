"""File recovery and carving tools."""

from app.tools.base import SecurityTool

FORENSICS_IMAGE = "nullify-tools-forensics:latest"


class ForemostTool(SecurityTool):
    name = "foremost_carve"
    description = "File carving tool — recover files from disk images or raw data. Use for forensic file recovery."
    binary = "foremost"
    docker_image = FORENSICS_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "input_file": {"type": "string", "description": "Path to disk image or raw file."},
            "file_types": {"type": "string", "description": "File types to carve (e.g. 'jpg,png,pdf,doc')."},
        },
        "required": ["input_file"],
    }

    def build_command(self, args: dict) -> list[str]:
        cmd = ["foremost", "-v", "-o", "/tmp/foremost_output", "-i", args["input_file"]]
        if ft := args.get("file_types"):
            cmd.extend(["-t", ft])
        return cmd

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        for line in raw_output.splitlines():
            if "Num:" in line or "Founded" in line.lower() or "files extracted" in line.lower():
                findings.append({"type": "carved_files", "detail": line.strip()})
        return findings


class PhotorecTool(SecurityTool):
    name = "photorec_recover"
    description = "File recovery tool for damaged disks and formatted drives."
    binary = "photorec"
    docker_image = FORENSICS_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "input_file": {"type": "string", "description": "Path to disk image."},
            "file_types": {"type": "string", "description": "File types to recover (e.g. 'jpg,png')."},
        },
        "required": ["input_file"],
    }

    def build_command(self, args: dict) -> list[str]:
        cmd = ["photorec", "/cmd", args["input_file"], "search"]
        return cmd

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        for line in raw_output.splitlines():
            if "file(s) saved" in line.lower() or "recovered" in line.lower():
                findings.append({"type": "recovered_files", "detail": line.strip()})
        return findings


class TestdiskTool(SecurityTool):
    name = "testdisk_analyze"
    description = "Partition recovery and disk analysis. Use for recovering lost partitions."
    binary = "testdisk"
    docker_image = FORENSICS_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "disk_image": {"type": "string", "description": "Path to disk image."},
        },
        "required": ["disk_image"],
    }

    def build_command(self, args: dict) -> list[str]:
        return ["testdisk", "/list", args["disk_image"]]

    def parse_output(self, raw_output: str) -> list[dict]:
        return [{"type": "partition_info", "data": raw_output.strip()}]


class ScalpelTool(SecurityTool):
    name = "scalpel_carve"
    description = "High-performance file carving tool. Use for precise file recovery from disk images."
    binary = "scalpel"
    docker_image = FORENSICS_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "input_file": {"type": "string", "description": "Path to disk image or raw file."},
        },
        "required": ["input_file"],
    }

    def build_command(self, args: dict) -> list[str]:
        return ["scalpel", "-o", "/tmp/scalpel_output", args["input_file"]]

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        for line in raw_output.splitlines():
            if "files carved" in line.lower() or line.strip().endswith("carved"):
                findings.append({"type": "carved_files", "detail": line.strip()})
        return findings


class BulkExtractorTool(SecurityTool):
    name = "bulk_extractor"
    description = (
        "Extract emails, URLs, credit cards, and other artifacts from disk images. "
        "Use for forensic artifact extraction."
    )
    binary = "bulk_extractor"
    docker_image = FORENSICS_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "input_file": {"type": "string", "description": "Path to disk image or file."},
            "scanners": {"type": "string", "description": "Specific scanners to enable (comma-separated)."},
        },
        "required": ["input_file"],
    }

    def build_command(self, args: dict) -> list[str]:
        cmd = ["bulk_extractor", "-o", "/tmp/bulk_output", args["input_file"]]
        if scanners := args.get("scanners"):
            for s in scanners.split(","):
                cmd.extend(["-E", s.strip()])
        return cmd

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        for line in raw_output.splitlines():
            if "Feature" in line or "found" in line.lower():
                findings.append({"type": "extracted_artifact", "detail": line.strip()})
        return findings
