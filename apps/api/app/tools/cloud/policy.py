"""Policy-as-code tools."""

from app.tools.base import SecurityTool

CLOUD_IMAGE = "nullify-tools-cloud:latest"


class OpaTool(SecurityTool):
    name = "opa_eval"
    description = (
        "Open Policy Agent — evaluate Rego policies against data. "
        "Use for custom policy enforcement and compliance checking."
    )
    binary = "opa"
    docker_image = CLOUD_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "policy_file": {"type": "string", "description": "Path to Rego policy file."},
            "data_file": {"type": "string", "description": "Path to JSON data file to evaluate."},
            "query": {"type": "string", "description": "Rego query (e.g. 'data.main.deny')."},
            "input_file": {"type": "string", "description": "Input JSON file."},
        },
        "required": ["query"],
    }

    def build_command(self, args: dict) -> list[str]:
        cmd = ["opa", "eval", "-f", "pretty"]
        if policy := args.get("policy_file"):
            cmd.extend(["-d", policy])
        if data := args.get("data_file"):
            cmd.extend(["-d", data])
        if inp := args.get("input_file"):
            cmd.extend(["-i", inp])
        cmd.append(args["query"])
        return cmd

    def parse_output(self, raw_output: str) -> list[dict]:
        return [{"type": "policy_result", "data": raw_output.strip()}]
