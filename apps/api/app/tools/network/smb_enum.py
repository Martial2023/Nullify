"""SMB/NetBIOS enumeration tools — Enum4Linux, Enum4LinuxNg, SmbMap, Nbtscan, RpcClient."""

import json
import re

from app.tools.base import SecurityTool

NETWORK_IMAGE = "nullify-tools-network:latest"


class Enum4LinuxTool(SecurityTool):
    name = "enum4linux_scan"
    description = (
        "Enumerate information from Windows/Samba systems: users, shares, "
        "groups, password policies, and more. Use for SMB reconnaissance "
        "against Windows or Samba targets."
    )
    binary = "enum4linux"
    docker_image = NETWORK_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "target": {
                "type": "string",
                "description": "Target IP or hostname running SMB.",
            },
        },
        "required": ["target"],
    }

    def build_command(self, args: dict) -> list[str]:
        return ["enum4linux", "-a", args["target"]]

    def parse_output(self, raw_output: str) -> list[dict]:
        findings: list[dict] = []

        # Extract users
        user_pattern = re.compile(r"user:\[([^\]]+)\]")
        for match in user_pattern.finditer(raw_output):
            findings.append({"type": "smb_user", "username": match.group(1)})

        # Extract shares
        share_pattern = re.compile(r"\s+([\w$]+)\s+(Disk|IPC|Printer)")
        for match in share_pattern.finditer(raw_output):
            findings.append({
                "type": "smb_share",
                "name": match.group(1),
                "share_type": match.group(2),
            })

        # Extract groups
        group_pattern = re.compile(r"group:\[([^\]]+)\]")
        for match in group_pattern.finditer(raw_output):
            findings.append({"type": "smb_group", "group": match.group(1)})

        if not findings:
            findings.append({"type": "smb_enum_raw", "data": raw_output.strip()})

        return findings


class Enum4LinuxNgTool(SecurityTool):
    name = "enum4linux_ng_scan"
    description = (
        "Next-generation SMB enumeration with JSON output. Improved version "
        "of enum4linux with better parsing and reliability. Use for structured "
        "SMB enumeration results."
    )
    binary = "enum4linux-ng"
    docker_image = NETWORK_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "target": {
                "type": "string",
                "description": "Target IP or hostname running SMB.",
            },
        },
        "required": ["target"],
    }

    def build_command(self, args: dict) -> list[str]:
        return ["enum4linux-ng", "-A", args["target"], "-oJ", "-"]

    def parse_output(self, raw_output: str) -> list[dict]:
        try:
            data = json.loads(raw_output)
            findings: list[dict] = []

            # Users
            for user in data.get("users", {}).values():
                findings.append({"type": "smb_user", **user})

            # Shares
            for name, info in data.get("shares", {}).items():
                findings.append({"type": "smb_share", "name": name, **info})

            # Groups
            for group in data.get("groups", {}).values():
                findings.append({"type": "smb_group", **group})

            if not findings:
                findings.append({"type": "smb_enum_data", "data": data})

            return findings
        except json.JSONDecodeError:
            return [{"type": "smb_enum_raw", "data": raw_output.strip()}]


class SmbMapTool(SecurityTool):
    name = "smbmap_scan"
    description = (
        "Enumerate SMB share permissions and access levels. Use to identify "
        "readable/writable shares on a target, optionally with credentials."
    )
    binary = "smbmap"
    docker_image = NETWORK_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "target": {
                "type": "string",
                "description": "Target IP or hostname running SMB.",
            },
            "username": {
                "type": "string",
                "description": "Username for authentication (optional, null session if omitted).",
            },
            "password": {
                "type": "string",
                "description": "Password for authentication (optional).",
            },
        },
        "required": ["target"],
    }

    def build_command(self, args: dict) -> list[str]:
        cmd = ["smbmap", "-H", args["target"]]
        username = args.get("username")
        password = args.get("password")
        if username:
            cmd.extend(["-u", username])
            if password:
                cmd.extend(["-p", password])
        return cmd

    def parse_output(self, raw_output: str) -> list[dict]:
        findings: list[dict] = []
        # smbmap output: Disk  ShareName  Permissions  Comment
        share_pattern = re.compile(
            r"\s+([\w$]+)\s+(READ ONLY|READ, WRITE|NO ACCESS|READ/WRITE)\s*(.*)"
        )
        for match in share_pattern.finditer(raw_output):
            name, permissions, comment = match.groups()
            findings.append({
                "type": "smb_share_access",
                "name": name,
                "permissions": permissions.strip(),
                "comment": comment.strip(),
            })
        if not findings:
            findings.append({"type": "smbmap_raw", "data": raw_output.strip()})
        return findings


class NbtscanTool(SecurityTool):
    name = "nbtscan_scan"
    description = (
        "Scan a network for NetBIOS name information. Use to discover "
        "Windows hosts, their NetBIOS names, and logged-in users on a "
        "local network segment."
    )
    binary = "nbtscan"
    docker_image = NETWORK_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "target": {
                "type": "string",
                "description": "Target IP or CIDR range (e.g. '192.168.1.0/24').",
            },
        },
        "required": ["target"],
    }

    def build_command(self, args: dict) -> list[str]:
        return ["nbtscan", args["target"]]

    def parse_output(self, raw_output: str) -> list[dict]:
        findings: list[dict] = []
        # nbtscan: IP  NetBIOS_Name  Server  User  MAC
        line_pattern = re.compile(
            r"([\d.]+)\s+(\S+)\s+(<server>|Sendto)?\s*(\S*)\s*([\da-fA-F:-]*)"
        )
        for line in raw_output.splitlines():
            line = line.strip()
            if not line or line.startswith(("Doing", "IP", "---")):
                continue
            parts = line.split()
            if len(parts) >= 2 and re.match(r"^\d+\.\d+\.\d+\.\d+$", parts[0]):
                findings.append({
                    "type": "netbios_host",
                    "ip": parts[0],
                    "netbios_name": parts[1] if len(parts) > 1 else "",
                    "user": parts[2] if len(parts) > 2 else "",
                    "mac": parts[-1] if len(parts) > 3 else "",
                })
        return findings


class RpcClientTool(SecurityTool):
    name = "rpcclient_enum"
    description = (
        "Enumerate information from Windows hosts via MS-RPC. "
        "Use for user enumeration, group enumeration, and SID lookups "
        "via null or authenticated sessions."
    )
    binary = "rpcclient"
    docker_image = NETWORK_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "target": {
                "type": "string",
                "description": "Target IP or hostname.",
            },
            "command": {
                "type": "string",
                "description": "RPC command to run (default 'enumdomusers'). "
                "Examples: enumdomusers, enumdomgroups, querydispinfo.",
            },
        },
        "required": ["target"],
    }

    def build_command(self, args: dict) -> list[str]:
        target = args["target"]
        rpc_command = args.get("command", "enumdomusers")
        return ["rpcclient", "-U", "", "-N", target, "-c", rpc_command]

    def parse_output(self, raw_output: str) -> list[dict]:
        findings: list[dict] = []
        # enumdomusers: user:[username] rid:[0xrid]
        user_pattern = re.compile(r"user:\[([^\]]+)\]\s+rid:\[([^\]]+)\]")
        for match in user_pattern.finditer(raw_output):
            findings.append({
                "type": "rpc_user",
                "username": match.group(1),
                "rid": match.group(2),
            })

        # enumdomgroups: group:[name] rid:[0xrid]
        group_pattern = re.compile(r"group:\[([^\]]+)\]\s+rid:\[([^\]]+)\]")
        for match in group_pattern.finditer(raw_output):
            findings.append({
                "type": "rpc_group",
                "group": match.group(1),
                "rid": match.group(2),
            })

        if not findings:
            for line in raw_output.splitlines():
                if line.strip():
                    findings.append({"type": "rpc_result", "data": line.strip()})

        return findings
