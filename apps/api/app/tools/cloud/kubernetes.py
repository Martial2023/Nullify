"""Kubernetes security tools."""

import json

from app.tools.base import SecurityTool

CLOUD_IMAGE = "nullify-tools-cloud:latest"


class KubeHunterTool(SecurityTool):
    name = "kube_hunter_scan"
    description = "Kubernetes cluster penetration testing. Discovers security weaknesses in K8s clusters."
    binary = "kube-hunter"
    docker_image = CLOUD_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "target": {"type": "string", "description": "Target cluster IP or CIDR."},
            "active": {"type": "boolean", "description": "Enable active hunting (default: false)."},
        },
        "required": [],
    }

    def build_command(self, args: dict) -> list[str]:
        cmd = ["kube-hunter", "--report", "json"]
        if target := args.get("target"):
            cmd.extend(["--remote", target])
        if args.get("active"):
            cmd.append("--active")
        return cmd

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        try:
            data = json.loads(raw_output)
            for vuln in data.get("vulnerabilities", []):
                findings.append({
                    "type": "k8s_vulnerability",
                    "category": vuln.get("category", ""),
                    "vulnerability": vuln.get("vulnerability", ""),
                    "severity": vuln.get("severity", "MEDIUM"),
                    "description": vuln.get("description", ""),
                    "evidence": vuln.get("evidence", ""),
                })
        except json.JSONDecodeError:
            pass
        return findings


class KubeBenchTool(SecurityTool):
    name = "kube_bench_scan"
    description = "CIS Kubernetes Benchmark checks. Use to audit K8s cluster configuration."
    binary = "kube-bench"
    docker_image = CLOUD_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "target": {"type": "string", "description": "Check target: master, node, etcd, policies."},
        },
        "required": [],
    }

    def build_command(self, args: dict) -> list[str]:
        cmd = ["kube-bench", "--json"]
        if target := args.get("target"):
            cmd.extend(["run", "--targets", target])
        return cmd

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        try:
            data = json.loads(raw_output)
            for control in data.get("Controls", []):
                for test in control.get("tests", []):
                    for result in test.get("results", []):
                        if result.get("status") == "FAIL":
                            findings.append({
                                "type": "k8s_benchmark_fail",
                                "test_number": result.get("test_number", ""),
                                "test_desc": result.get("test_desc", ""),
                                "remediation": result.get("remediation", ""),
                            })
        except json.JSONDecodeError:
            pass
        return findings


class KubectlTool(SecurityTool):
    name = "kubectl_exec"
    description = "Kubernetes CLI for cluster interaction. Use for K8s enumeration and resource inspection."
    binary = "kubectl"
    docker_image = CLOUD_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "command": {"type": "string", "description": "kubectl command (e.g. 'get pods', 'describe svc')."},
            "namespace": {"type": "string", "description": "Kubernetes namespace."},
            "output": {"type": "string", "description": "Output format: json, yaml, wide (default: json)."},
        },
        "required": ["command"],
    }

    def build_command(self, args: dict) -> list[str]:
        cmd = ["kubectl"] + args["command"].split()
        if ns := args.get("namespace"):
            cmd.extend(["-n", ns])
        cmd.extend(["-o", args.get("output", "json")])
        return cmd

    def parse_output(self, raw_output: str) -> list[dict]:
        try:
            data = json.loads(raw_output)
            return [{"type": "k8s_resource", "data": data}]
        except json.JSONDecodeError:
            return [{"type": "k8s_output", "data": raw_output.strip()}]


class HelmTool(SecurityTool):
    name = "helm_exec"
    description = "Helm package manager for Kubernetes. Use for listing deployed charts and checking versions."
    binary = "helm"
    docker_image = CLOUD_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "command": {"type": "string", "description": "Helm command (e.g. 'list', 'show values')."},
            "namespace": {"type": "string", "description": "Kubernetes namespace."},
        },
        "required": ["command"],
    }

    def build_command(self, args: dict) -> list[str]:
        cmd = ["helm"] + args["command"].split() + ["-o", "json"]
        if ns := args.get("namespace"):
            cmd.extend(["-n", ns])
        return cmd

    def parse_output(self, raw_output: str) -> list[dict]:
        try:
            data = json.loads(raw_output)
            return [{"type": "helm_result", "data": data}]
        except json.JSONDecodeError:
            return [{"type": "helm_output", "data": raw_output.strip()}]
