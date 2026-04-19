"""Disk forensics tools."""

from app.tools.base import SecurityTool

FORENSICS_IMAGE = "nullify-tools-forensics:latest"


class SleuthKitTool(SecurityTool):
    name = "sleuthkit_analyze"
    description = (
        "The Sleuth Kit — filesystem forensic analysis. "
        "Analyze disk images, recover deleted files, examine filesystem metadata."
    )
    binary = "fls"
    docker_image = FORENSICS_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "image_path": {"type": "string", "description": "Path to disk image."},
            "command": {"type": "string", "description": "TSK command: fls (file list), icat (extract file), mmls (partitions). Default: fls."},
            "inode": {"type": "string", "description": "Inode number for icat extraction."},
            "options": {"type": "string", "description": "Additional options (e.g. '-r' for recursive, '-d' for deleted)."},
        },
        "required": ["image_path"],
    }

    def build_command(self, args: dict) -> list[str]:
        tool = args.get("command", "fls")
        cmd = [tool]
        if opts := args.get("options"):
            cmd.extend(opts.split())
        cmd.append(args["image_path"])
        if inode := args.get("inode"):
            cmd.append(inode)
        return cmd

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        for line in raw_output.splitlines():
            line = line.strip()
            if line:
                findings.append({"type": "filesystem_entry", "data": line})
        return findings[:500]
