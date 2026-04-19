"""Active Directory tools — NetExec, Responder."""

import re

from app.tools.base import SecurityTool

NETWORK_IMAGE = "nullify-tools-network:latest"


class NetExecTool(SecurityTool):
    name = "netexec_scan"
    description = (
        "Multi-protocol network service scanner for Active Directory environments. "
        "Supports SMB, SSH, LDAP, WinRM, and more. Use for credential testing, "
        "service enumeration, and AD reconnaissance."
    )
    binary = "netexec"
    docker_image = NETWORK_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "target": {
                "type": "string",
                "description": "Target IP, hostname, or CIDR range.",
            },
            "protocol": {
                "type": "string",
                "enum": ["smb", "ssh", "ldap", "winrm", "mssql"],
                "description": "Protocol to use (default 'smb').",
            },
            "username": {
                "type": "string",
                "description": "Username for authentication (optional).",
            },
            "password": {
                "type": "string",
                "description": "Password for authentication (optional).",
            },
        },
        "required": ["target"],
    }

    def build_command(self, args: dict) -> list[str]:
        target = args["target"]
        protocol = args.get("protocol", "smb")
        cmd = ["netexec", protocol, target]

        username = args.get("username")
        password = args.get("password")
        if username:
            cmd.extend(["-u", username])
            cmd.extend(["-p", password or ""])

        return cmd

    def parse_output(self, raw_output: str) -> list[dict]:
        findings: list[dict] = []
        for line in raw_output.splitlines():
            line = line.strip()
            if not line:
                continue

            # NetExec output: PROTO  IP:PORT  HOSTNAME  ...  [+] or [-]
            result = {"type": "netexec_result", "raw": line}

            # Detect success/failure markers
            if "[+]" in line:
                result["status"] = "success"
            elif "[-]" in line:
                result["status"] = "failure"
            else:
                result["status"] = "info"

            # Try to extract IP
            ip_match = re.search(r"(\d+\.\d+\.\d+\.\d+)", line)
            if ip_match:
                result["ip"] = ip_match.group(1)

            # Try to extract hostname
            hostname_match = re.search(
                r"\d+\.\d+\.\d+\.\d+\s+(\S+)", line
            )
            if hostname_match:
                result["hostname"] = hostname_match.group(1)

            findings.append(result)

        return findings


class ResponderTool(SecurityTool):
    name = "responder_capture"
    description = (
        "Network protocol analyzer for capturing LLMNR, NBT-NS, and MDNS "
        "requests in analyze mode (passive, no poisoning). Use to discover "
        "what protocols and credentials are broadcast on the network."
    )
    binary = "responder"
    docker_image = NETWORK_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "interface": {
                "type": "string",
                "description": "Network interface to listen on (default 'eth0').",
            },
        },
        "required": [],
    }

    def build_command(self, args: dict) -> list[str]:
        interface = args.get("interface", "eth0")
        # -A = analyze mode (passive, no poisoning)
        return ["responder", "-I", interface, "-A"]

    def parse_output(self, raw_output: str) -> list[dict]:
        findings: list[dict] = []

        # Look for captured hashes/requests
        hash_pattern = re.compile(
            r"\[([\w-]+)\]\s+NTLMv[12]\s+(?:Hash|Client)\s*:\s*(.*)", re.IGNORECASE
        )
        for match in hash_pattern.finditer(raw_output):
            findings.append({
                "type": "captured_hash",
                "protocol": match.group(1),
                "hash": match.group(2).strip(),
            })

        # Look for requests
        request_pattern = re.compile(
            r"\[([\w-]+)\]\s+([\w.]+)\s+from\s+([\d.]+)", re.IGNORECASE
        )
        for match in request_pattern.finditer(raw_output):
            findings.append({
                "type": "captured_request",
                "protocol": match.group(1),
                "requested_name": match.group(2),
                "source_ip": match.group(3),
            })

        if not findings:
            for line in raw_output.splitlines():
                line = line.strip()
                if line and not line.startswith(("[*]", "[!]")):
                    findings.append({"type": "responder_event", "data": line})

        return findings
