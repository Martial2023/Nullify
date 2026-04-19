"""Hash identification tools."""

from app.tools.base import SecurityTool

AUTH_IMAGE = "nullify-tools-auth:latest"


class HashIdentifierTool(SecurityTool):
    name = "hash_identifier"
    description = "Identify hash types from hash values. Use before attempting to crack an unknown hash."
    binary = "hash-identifier"
    docker_image = AUTH_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "hash_value": {"type": "string", "description": "Hash value to identify."},
        },
        "required": ["hash_value"],
    }

    def build_command(self, args: dict) -> list[str]:
        h = args["hash_value"].replace("'", "'\\''")
        return ["sh", "-c", f"echo '{h}' | hash-identifier"]

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        capture = False
        for line in raw_output.splitlines():
            line = line.strip()
            if "Possible Hashs" in line:
                capture = True
                continue
            if "Least Possible" in line:
                capture = False
                continue
            if capture and line.startswith("[+]"):
                findings.append({"type": "hash_type", "algorithm": line.replace("[+]", "").strip(), "confidence": "high"})
        return findings


class HashIdTool(SecurityTool):
    name = "hashid_identify"
    description = "Modern hash type identifier with hashcat/john mode references. Use to identify hashes."
    binary = "hashid"
    docker_image = AUTH_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "hash_value": {"type": "string", "description": "Hash value to identify."},
        },
        "required": ["hash_value"],
    }

    def build_command(self, args: dict) -> list[str]:
        return ["hashid", "-m", "-j", args["hash_value"]]

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        for line in raw_output.splitlines():
            line = line.strip()
            if line.startswith("[+]"):
                findings.append({"type": "hash_type", "detail": line.replace("[+]", "").strip()})
        return findings
