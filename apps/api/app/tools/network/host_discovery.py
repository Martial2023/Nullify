"""Host discovery tools — ArpScan, Traceroute, Ping, Netcat."""

import re

from app.tools.base import SecurityTool

NETWORK_IMAGE = "nullify-tools-network:latest"


class ArpScanTool(SecurityTool):
    name = "arp_scan"
    description = (
        "Discover hosts on a local network segment using ARP requests. "
        "Use to find live hosts on the same subnet (e.g. '192.168.1.0/24')."
    )
    binary = "arp-scan"
    docker_image = NETWORK_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "target": {
                "type": "string",
                "description": "Target subnet in CIDR notation (e.g. '192.168.1.0/24').",
            },
        },
        "required": ["target"],
    }

    def build_command(self, args: dict) -> list[str]:
        return ["arp-scan", args["target"]]

    def parse_output(self, raw_output: str) -> list[dict]:
        findings: list[dict] = []
        # arp-scan outputs: IP\tMAC\tVendor
        arp_pattern = re.compile(
            r"([\d.]+)\s+([\da-fA-F:]{17})\s+(.*)"
        )
        for match in arp_pattern.finditer(raw_output):
            ip, mac, vendor = match.groups()
            findings.append({
                "type": "host_alive",
                "ip": ip,
                "mac": mac,
                "vendor": vendor.strip(),
            })
        return findings


class TracerouteTool(SecurityTool):
    name = "traceroute_scan"
    description = (
        "Trace the network path to a target, showing each hop. "
        "Use to understand network topology and identify firewalls or "
        "filtering devices between you and the target."
    )
    binary = "traceroute"
    docker_image = NETWORK_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "target": {
                "type": "string",
                "description": "Target IP or hostname to trace.",
            },
        },
        "required": ["target"],
    }

    def build_command(self, args: dict) -> list[str]:
        return ["traceroute", args["target"]]

    def parse_output(self, raw_output: str) -> list[dict]:
        findings: list[dict] = []
        # Lines like: " 1  gateway (192.168.1.1)  1.234 ms  ..."
        hop_pattern = re.compile(
            r"^\s*(\d+)\s+(.+?)\s+\(([\d.]+)\)\s+([\d.]+)\s+ms"
        )
        for line in raw_output.splitlines():
            match = hop_pattern.match(line)
            if match:
                hop_num, hostname, ip, latency = match.groups()
                findings.append({
                    "type": "traceroute_hop",
                    "hop": int(hop_num),
                    "hostname": hostname.strip(),
                    "ip": ip,
                    "latency_ms": float(latency),
                })
            elif re.match(r"^\s*\d+\s+\* \* \*", line):
                hop_num = line.strip().split()[0]
                findings.append({
                    "type": "traceroute_hop",
                    "hop": int(hop_num),
                    "hostname": "*",
                    "ip": "*",
                    "latency_ms": None,
                })
        return findings


class PingTool(SecurityTool):
    name = "ping_sweep"
    description = (
        "Send ICMP echo requests to check if a host is alive and measure "
        "round-trip latency. Use for basic host liveness checks."
    )
    binary = "ping"
    docker_image = NETWORK_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "target": {
                "type": "string",
                "description": "Target IP or hostname to ping.",
            },
            "count": {
                "type": "integer",
                "description": "Number of ping packets to send (default 4).",
            },
        },
        "required": ["target"],
    }

    def build_command(self, args: dict) -> list[str]:
        target = args["target"]
        count = str(args.get("count", 4))
        return ["ping", "-c", count, target]

    def parse_output(self, raw_output: str) -> list[dict]:
        alive = "0% packet loss" in raw_output or "0.0% packet loss" in raw_output

        latency = None
        # Extract avg latency from "rtt min/avg/max/mdev = ..."
        rtt_match = re.search(
            r"rtt min/avg/max/mdev = ([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+)",
            raw_output,
        )
        if rtt_match:
            latency = float(rtt_match.group(2))  # avg

        return [{
            "type": "ping_result",
            "target": "",  # filled from args at caller level
            "alive": alive,
            "avg_latency_ms": latency,
            "raw_summary": raw_output.strip().splitlines()[-1] if raw_output.strip() else "",
        }]


class NetcatTool(SecurityTool):
    name = "netcat_connect"
    description = (
        "Test TCP connectivity to a specific host and port. Use for quick "
        "checks whether a specific service port is open or closed."
    )
    binary = "nc"
    docker_image = NETWORK_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "target": {
                "type": "string",
                "description": "Target IP or hostname.",
            },
            "port": {
                "type": "integer",
                "description": "Port number to connect to.",
            },
            "timeout": {
                "type": "integer",
                "description": "Connection timeout in seconds (default 5).",
            },
        },
        "required": ["target", "port"],
    }

    def build_command(self, args: dict) -> list[str]:
        target = args["target"]
        port = str(args["port"])
        timeout = str(args.get("timeout", 5))
        return ["nc", "-zv", "-w", timeout, target, port]

    def parse_output(self, raw_output: str) -> list[dict]:
        # nc outputs to stderr, but we capture both
        combined = raw_output.lower()
        is_open = "succeeded" in combined or "open" in combined

        return [{
            "type": "port_check",
            "state": "open" if is_open else "closed",
            "raw": raw_output.strip(),
        }]
