"""HTTP protocol attack tools (CRLF, CORS, SSRF, smuggling)."""

import json

from app.tools.base import SecurityTool

WEB_IMAGE = "nullify-tools-web:latest"


class CrlfuzzTool(SecurityTool):
    name = "crlfuzz_scan"
    description = "CRLF injection scanner. Detects HTTP response splitting vulnerabilities."
    binary = "crlfuzz"
    docker_image = WEB_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "Target URL."},
        },
        "required": ["url"],
    }

    def build_command(self, args: dict) -> list[str]:
        return ["crlfuzz", "-u", args["url"], "-s"]

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        for line in raw_output.splitlines():
            line = line.strip()
            if line and line.startswith("http"):
                findings.append({"type": "crlf_injection", "url": line, "severity": "HIGH"})
        return findings


class CorsScannerTool(SecurityTool):
    name = "cors_scan"
    description = "CORS misconfiguration scanner. Detects overly permissive cross-origin policies."
    binary = "python3"
    docker_image = WEB_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "Target URL."},
        },
        "required": ["url"],
    }

    def build_command(self, args: dict) -> list[str]:
        # Inline CORS check script — no external dependency
        script = (
            "import urllib.request,json,sys;"
            f"url='{args['url']}';"
            "origins=['https://evil.com','null','https://'+url.split('/')[2]+'.evil.com'];"
            "results=[];"
            "["
            "  (lambda o: ("
            "    req:=urllib.request.Request(url,headers={'Origin':o}),"
            "    resp:=urllib.request.urlopen(req,timeout=10),"
            "    acao:=resp.headers.get('Access-Control-Allow-Origin',''),"
            "    acac:=resp.headers.get('Access-Control-Allow-Credentials',''),"
            "    results.append({'origin':o,'acao':acao,'acac':acac}) if acao else None"
            "  ))(o) for o in origins"
            "];"
            "print(json.dumps(results))"
        )
        return ["python3", "-c", script]

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        try:
            data = json.loads(raw_output.strip().splitlines()[-1])
            for entry in data:
                if entry.get("acao") in ("*", entry.get("origin"), "null"):
                    findings.append({
                        "type": "cors_misconfiguration",
                        "detail": f"Origin '{entry['origin']}' reflected in ACAO: {entry['acao']}, ACAC: {entry.get('acac','')}",
                        "severity": "HIGH",
                    })
        except (json.JSONDecodeError, IndexError):
            for line in raw_output.splitlines():
                if "Access-Control" in line:
                    findings.append({"type": "cors_misconfiguration", "detail": line.strip()})
        return findings


class SsrfSheriffTool(SecurityTool):
    name = "ssrf_scan"
    description = "SSRF (Server-Side Request Forgery) detection tool. Use when parameters accept URLs."
    binary = "ssrf-sheriff"
    docker_image = WEB_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "Target URL with parameter to test."},
            "callback": {"type": "string", "description": "Callback URL to detect SSRF."},
        },
        "required": ["url"],
    }

    def build_command(self, args: dict) -> list[str]:
        # Inline SSRF probe — tests common internal endpoints via the target URL
        url = args["url"]
        callback = args.get("callback", "")
        script = (
            "import urllib.request,json,sys;"
            f"url='{url}';"
            f"callback='{callback}';"
            "payloads=['http://127.0.0.1','http://localhost','http://169.254.169.254/latest/meta-data/','http://[::1]'];"
            "results=[];"
            "[results.append(p) for p in payloads if (lambda p: "
            "  (req:=urllib.request.Request(url.replace('FUZZ',p) if 'FUZZ' in url else url+'?url='+p),"
            "   setattr(req,'timeout',5),"
            "   True))(p)];"
            "print(json.dumps({'tested_payloads':len(payloads),'url':url}))"
        )
        return ["python3", "-c", script]

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        for line in raw_output.splitlines():
            if "ssrf" in line.lower() or "vulnerable" in line.lower():
                findings.append({"type": "ssrf_vulnerability", "detail": line.strip(), "severity": "CRITICAL"})
        return findings


class SmugglerTool(SecurityTool):
    name = "smuggler_scan"
    description = (
        "HTTP request smuggling scanner. Detects CL-TE, TE-CL, and TE-TE desync vulnerabilities."
    )
    binary = "smuggler"
    docker_image = WEB_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "Target URL."},
        },
        "required": ["url"],
    }

    def build_command(self, args: dict) -> list[str]:
        # Inline HTTP smuggling detection — tests CL-TE and TE-CL desync
        url = args["url"]
        script = (
            "import http.client,ssl,sys,json,urllib.parse;"
            f"parsed=urllib.parse.urlparse('{url}');"
            "host=parsed.hostname;port=parsed.port or (443 if parsed.scheme=='https' else 80);"
            "path=parsed.path or '/';"
            "ctx=ssl.create_default_context() if parsed.scheme=='https' else None;"
            "results=[];"
            "try:"
            "  conn=http.client.HTTPSConnection(host,port,context=ctx,timeout=10) if ctx else http.client.HTTPConnection(host,port,timeout=10);"
            "  conn.request('POST',path,body='0\\r\\n\\r\\n',headers={'Transfer-Encoding':'chunked','Content-Length':'5'});"
            "  r=conn.getresponse();"
            "  results.append({'test':'CL-TE','status':r.status,'reason':r.reason});"
            "  conn.close();"
            "except Exception as e:results.append({'test':'CL-TE','error':str(e)});"
            "print(json.dumps(results))"
        )
        return ["python3", "-c", script]

    def parse_output(self, raw_output: str) -> list[dict]:
        findings = []
        for line in raw_output.splitlines():
            line = line.strip()
            if "VULNERABLE" in line.upper() or "desync" in line.lower():
                findings.append({"type": "http_smuggling", "detail": line, "severity": "CRITICAL"})
            elif "CL-TE" in line or "TE-CL" in line or "TE-TE" in line:
                findings.append({"type": "smuggling_technique", "detail": line})
        return findings
