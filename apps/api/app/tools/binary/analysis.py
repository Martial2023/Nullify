"""Binary analysis frameworks."""

from app.tools.base import SecurityTool

BINARY_IMAGE = "nullify-tools-binary:latest"


class AngrTool(SecurityTool):
    name = "angr_analyze"
    description = (
        "Symbolic execution engine for binary analysis. "
        "Use for automated vulnerability discovery and CTF solving."
    )
    binary = "python3"
    docker_image = BINARY_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "binary_path": {"type": "string", "description": "Path to the binary."},
            "script": {"type": "string", "description": "Custom angr Python script."},
            "find_addr": {"type": "string", "description": "Address to reach (hex, e.g. 0x401234)."},
            "avoid_addr": {"type": "string", "description": "Address to avoid (hex)."},
        },
        "required": ["binary_path"],
    }

    def build_command(self, args: dict) -> list[str]:
        if script := args.get("script"):
            escaped = script.replace("'", "'\\''")
            return ["sh", "-c", f"echo '{escaped}' | python3"]

        find = args.get("find_addr", "")
        avoid = args.get("avoid_addr", "")
        script_code = (
            f"import angr,sys; "
            f"p=angr.Project('{args['binary_path']}',auto_load_libs=False); "
            f"s=p.factory.entry_state(); "
            f"sm=p.factory.simgr(s); "
        )
        if find:
            script_code += f"sm.explore(find={find}"
            if avoid:
                script_code += f",avoid={avoid}"
            script_code += "); "
            script_code += "print('Found!' if sm.found else 'Not found'); "
            script_code += "[print(f.posix.dumps(0)) for f in sm.found[:3)]"
        else:
            script_code += "print(p.analyses.CFGFast().graph)"
        return ["python3", "-c", script_code]

    def parse_output(self, raw_output: str) -> list[dict]:
        return [{"type": "angr_result", "data": raw_output.strip()}]


class LibcDatabaseTool(SecurityTool):
    name = "libc_database"
    description = "Identify libc version from leaked function addresses. Use for ret2libc exploitation."
    binary = "libc-database"
    docker_image = BINARY_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "function": {"type": "string", "description": "Function name (e.g. puts)."},
            "address": {"type": "string", "description": "Leaked address (last 3 hex nibbles, e.g. 690)."},
        },
        "required": ["function", "address"],
    }

    def build_command(self, args: dict) -> list[str]:
        return ["/opt/libc-database/find", args["function"], args["address"]]

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        for line in raw_output.splitlines():
            line = line.strip()
            if line:
                findings.append({"type": "libc_match", "detail": line})
        return findings
