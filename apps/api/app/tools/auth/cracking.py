"""Password cracking tools."""

from app.tools.base import SecurityTool

AUTH_IMAGE = "nullify-tools-auth:latest"


class JohnTool(SecurityTool):
    name = "john_crack"
    description = (
        "John the Ripper — password cracker supporting hundreds of hash formats. "
        "Use for cracking password hashes (MD5, SHA, bcrypt, etc)."
    )
    binary = "john"
    docker_image = AUTH_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "hash_file": {"type": "string", "description": "Path to file containing hashes."},
            "hash_value": {"type": "string", "description": "Single hash value to crack."},
            "format": {"type": "string", "description": "Hash format (e.g. raw-md5, bcrypt, sha256crypt)."},
            "wordlist": {"type": "string", "description": "Wordlist path."},
            "rules": {"type": "string", "description": "Mangling rules (e.g. jumbo, best64)."},
        },
        "required": [],
    }

    def build_command(self, args: dict) -> list[str]:
        if hash_val := args.get("hash_value"):
            cmd = ["sh", "-c", f"echo '{hash_val}' > /tmp/hash.txt && john /tmp/hash.txt"]
        else:
            cmd = ["john", args.get("hash_file", "/tmp/hash.txt")]
        if fmt := args.get("format"):
            cmd_str = " ".join(cmd) if cmd[0] == "sh" else None
            if cmd_str:
                cmd = ["sh", "-c", cmd_str.replace("john ", f"john --format={fmt} ", 1)]
            else:
                cmd.extend([f"--format={fmt}"])
        if wl := args.get("wordlist"):
            cmd_str = " ".join(cmd) if cmd[0] == "sh" else None
            if cmd_str:
                cmd = ["sh", "-c", cmd[-1].replace("john ", f"john --wordlist={wl} ", 1)]
            else:
                cmd.extend([f"--wordlist={wl}"])
        if rules := args.get("rules"):
            if cmd[0] != "sh":
                cmd.extend([f"--rules={rules}"])
        cmd_show = cmd + ["--show"] if cmd[0] != "sh" else cmd
        return cmd

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        for line in raw_output.splitlines():
            line = line.strip()
            if ":" in line and not line.startswith("Warning") and not line.startswith("Using"):
                parts = line.split(":")
                if len(parts) >= 2:
                    findings.append({
                        "type": "cracked_password",
                        "hash_or_user": parts[0],
                        "password": parts[1],
                        "severity": "CRITICAL",
                    })
            elif "cracked" in line.lower():
                findings.append({"type": "crack_summary", "detail": line})
        return findings


class HashcatTool(SecurityTool):
    name = "hashcat_crack"
    description = (
        "Advanced password recovery with GPU support (CPU mode in Docker). "
        "Use for fast hash cracking with extensive rule support."
    )
    binary = "hashcat"
    docker_image = AUTH_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "hash_value": {"type": "string", "description": "Hash to crack."},
            "hash_file": {"type": "string", "description": "File containing hashes."},
            "hash_type": {"type": "integer", "description": "Hash type code (e.g. 0=MD5, 1000=NTLM, 1800=SHA-512)."},
            "wordlist": {"type": "string", "description": "Wordlist path."},
            "attack_mode": {"type": "integer", "description": "Attack mode: 0=dictionary, 3=brute-force, 6=hybrid."},
        },
        "required": ["hash_type"],
    }

    def build_command(self, args: dict) -> list[str]:
        if hash_val := args.get("hash_value"):
            hash_src = "/tmp/hash.txt"
            prefix = f"echo '{hash_val}' > {hash_src} && "
        else:
            hash_src = args.get("hash_file", "/tmp/hash.txt")
            prefix = ""

        cmd_parts = [
            f"hashcat -m {args['hash_type']}",
            f"-a {args.get('attack_mode', 0)}",
            "--force",  # CPU mode
            f"{hash_src}",
        ]
        if wl := args.get("wordlist"):
            cmd_parts.append(wl)
        elif args.get("attack_mode", 0) == 0:
            cmd_parts.append("/usr/share/wordlists/rockyou.txt")

        cmd_parts.append("--show")
        return ["sh", "-c", prefix + " ".join(cmd_parts)]

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        for line in raw_output.splitlines():
            line = line.strip()
            if ":" in line and not line.startswith("Session") and not line.startswith("Status"):
                parts = line.rsplit(":", 1)
                if len(parts) == 2:
                    findings.append({
                        "type": "cracked_password",
                        "hash": parts[0],
                        "password": parts[1],
                        "severity": "CRITICAL",
                    })
        return findings
