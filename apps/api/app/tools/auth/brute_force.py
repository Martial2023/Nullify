"""Brute force and credential testing tools."""

from app.tools.base import SecurityTool

AUTH_IMAGE = "nullify-tools-auth:latest"


class HydraTool(SecurityTool):
    name = "hydra_brute"
    description = (
        "Network login brute-forcer supporting 50+ protocols (SSH, FTP, HTTP, SMB, etc). "
        "Use for credential testing against network services."
    )
    binary = "hydra"
    docker_image = AUTH_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "target": {"type": "string", "description": "Target host or IP."},
            "service": {"type": "string", "description": "Service to attack (ssh, ftp, http-post-form, smb, etc)."},
            "username": {"type": "string", "description": "Single username or file path."},
            "password": {"type": "string", "description": "Single password or file path."},
            "username_list": {"type": "string", "description": "Username wordlist path."},
            "password_list": {"type": "string", "description": "Password wordlist path."},
            "port": {"type": "integer", "description": "Target port."},
            "extra": {"type": "string", "description": "Extra arguments (e.g. HTTP form path)."},
        },
        "required": ["target", "service"],
    }

    def build_command(self, args: dict) -> list[str]:
        cmd = ["hydra"]
        if user := args.get("username"):
            cmd.extend(["-l", user])
        elif ulist := args.get("username_list"):
            cmd.extend(["-L", ulist])
        if pwd := args.get("password"):
            cmd.extend(["-p", pwd])
        elif plist := args.get("password_list"):
            cmd.extend(["-P", plist])
        if port := args.get("port"):
            cmd.extend(["-s", str(port)])
        cmd.extend(["-V", "-o", "/dev/stdout", args["target"], args["service"]])
        if extra := args.get("extra"):
            cmd.append(extra)
        return cmd

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        for line in raw_output.splitlines():
            if "host:" in line.lower() and ("login:" in line.lower() or "password:" in line.lower()):
                findings.append({"type": "credential_found", "detail": line.strip(), "severity": "CRITICAL"})
            elif "successfully completed" in line.lower():
                findings.append({"type": "brute_force_complete", "detail": line.strip()})
        return findings


class MedusaTool(SecurityTool):
    name = "medusa_brute"
    description = "Parallel network login brute-forcer. Use as an alternative to Hydra."
    binary = "medusa"
    docker_image = AUTH_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "target": {"type": "string", "description": "Target host."},
            "module": {"type": "string", "description": "Module (ssh, ftp, http, smb, etc)."},
            "username": {"type": "string", "description": "Username."},
            "password_list": {"type": "string", "description": "Password wordlist."},
        },
        "required": ["target", "module"],
    }

    def build_command(self, args: dict) -> list[str]:
        cmd = ["medusa", "-h", args["target"], "-M", args["module"]]
        if user := args.get("username"):
            cmd.extend(["-u", user])
        if plist := args.get("password_list"):
            cmd.extend(["-P", plist])
        cmd.append("-O")
        return cmd

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        for line in raw_output.splitlines():
            if "SUCCESS" in line.upper():
                findings.append({"type": "credential_found", "detail": line.strip(), "severity": "CRITICAL"})
        return findings


class PatatorTool(SecurityTool):
    name = "patator_brute"
    description = "Multi-purpose brute-forcer with flexible module system. Use for complex brute-force scenarios."
    binary = "patator"
    docker_image = AUTH_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "module": {"type": "string", "description": "Module (ssh_login, ftp_login, http_fuzz, etc)."},
            "options": {"type": "string", "description": "Module options string (e.g. 'host=target user=FILE0 password=FILE1 0=/users.txt 1=/pass.txt')."},
        },
        "required": ["module", "options"],
    }

    def build_command(self, args: dict) -> list[str]:
        return ["patator", args["module"]] + args["options"].split()

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        for line in raw_output.splitlines():
            if "0:" in line or "SUCCESS" in line.upper():
                findings.append({"type": "credential_found", "detail": line.strip(), "severity": "CRITICAL"})
        return findings
