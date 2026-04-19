"""Cryptography analysis tools."""

from app.tools.base import SecurityTool

FORENSICS_IMAGE = "nullify-tools-forensics:latest"


class RsaToolTool(SecurityTool):
    name = "rsatool_analyze"
    description = "RSA key analysis and attacks (Wiener, Fermat, etc). Use for CTF crypto challenges."
    binary = "rsatool"
    docker_image = FORENSICS_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "n": {"type": "string", "description": "RSA modulus N."},
            "e": {"type": "string", "description": "RSA public exponent e."},
            "p": {"type": "string", "description": "Prime factor p (if known)."},
            "q": {"type": "string", "description": "Prime factor q (if known)."},
        },
        "required": ["n", "e"],
    }

    def build_command(self, args: dict) -> list[str]:
        cmd = ["python3", "/opt/rsatool/rsatool.py",
               "-n", args["n"], "-e", args["e"],
               "-o", "/dev/stdout"]
        if p := args.get("p"):
            cmd.extend(["-p", p])
        if q := args.get("q"):
            cmd.extend(["-q", q])
        return cmd

    def parse_output(self, raw_output: str) -> list[dict]:
        return [{"type": "rsa_result", "data": raw_output.strip()}]


class FactorDbTool(SecurityTool):
    name = "factordb_lookup"
    description = "Look up integer factorization in FactorDB. Use for RSA challenges with small/known primes."
    binary = "python3"
    docker_image = FORENSICS_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "number": {"type": "string", "description": "Number to factorize."},
        },
        "required": ["number"],
    }

    def build_command(self, args: dict) -> list[str]:
        script = (
            f"from factordb.factordb import FactorDB; "
            f"f=FactorDB(int('{args['number']}')); f.connect(); "
            f"print('Status:', f.get_status()); "
            f"print('Factors:', f.get_factor_list())"
        )
        return ["python3", "-c", script]

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        for line in raw_output.splitlines():
            if "Status" in line or "Factors" in line:
                findings.append({"type": "factorization", "detail": line.strip()})
        return findings
