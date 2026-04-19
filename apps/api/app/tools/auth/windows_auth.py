"""Windows authentication tools."""

from app.tools.base import SecurityTool

AUTH_IMAGE = "nullify-tools-auth:latest"


class EvilWinrmTool(SecurityTool):
    name = "evil_winrm"
    description = (
        "Windows Remote Management (WinRM) shell. "
        "Use for authenticated access to Windows hosts via WinRM."
    )
    binary = "evil-winrm"
    docker_image = AUTH_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "target": {"type": "string", "description": "Target Windows host."},
            "username": {"type": "string", "description": "Username."},
            "password": {"type": "string", "description": "Password."},
            "hash": {"type": "string", "description": "NTLM hash for pass-the-hash."},
            "command": {"type": "string", "description": "Command to execute remotely."},
        },
        "required": ["target", "username"],
    }

    def build_command(self, args: dict) -> list[str]:
        cmd = ["evil-winrm", "-i", args["target"], "-u", args["username"]]
        if pwd := args.get("password"):
            cmd.extend(["-p", pwd])
        elif h := args.get("hash"):
            cmd.extend(["-H", h])
        if command := args.get("command"):
            cmd.extend(["-c", command])
        return cmd

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        for line in raw_output.splitlines():
            line = line.strip()
            if not line or line.startswith("Info:") or line.startswith("Warning:"):
                continue
            if "Evil-WinRM" in line and "PS" in line:
                findings.append({"type": "winrm_session", "detail": "Shell established", "severity": "CRITICAL"})
            elif line:
                findings.append({"type": "command_output", "data": line})
        return findings
