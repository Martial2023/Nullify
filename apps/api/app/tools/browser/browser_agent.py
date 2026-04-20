"""Browser automation tool using Playwright."""

import json

from app.tools.base import SecurityTool

BROWSER_IMAGE = "nullify-tools-browser:latest"


class BrowserTool(SecurityTool):
    name = "browser_action"
    description = (
        "Browser automation with Playwright — navigate, click, fill forms, "
        "take screenshots, extract content. Use for testing authenticated flows, "
        "complex web interactions, and visual inspection."
    )
    binary = "python3"
    docker_image = BROWSER_IMAGE
    parameters = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["navigate", "screenshot", "click", "fill", "evaluate", "content", "cookies"],
                "description": "Action to perform.",
            },
            "url": {"type": "string", "description": "URL to navigate to."},
            "selector": {"type": "string", "description": "CSS selector for click/fill actions."},
            "value": {"type": "string", "description": "Value for fill action or JS for evaluate."},
            "wait_for": {"type": "string", "description": "Selector to wait for after action."},
        },
        "required": ["action", "url"],
    }

    def build_command(self, args: dict) -> list[str]:
        action = args["action"]
        url = args.get("url", "")
        if not url:
            # Return a script that just reports the error
            return ["python3", "-c", "import json;print(json.dumps({'error':'URL is required for browser actions'}))"]
        selector = args.get("selector", "")
        value = args.get("value", "")
        wait_for = args.get("wait_for", "")

        script = """
import asyncio, json
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        result = {}
"""
        if action == "navigate":
            script += f"""
        resp = await page.goto("{url}", wait_until="networkidle")
        result = {{"url": page.url, "status": resp.status, "title": await page.title()}}
"""
        elif action == "screenshot":
            script += f"""
        await page.goto("{url}", wait_until="networkidle")
        await page.screenshot(path="/tmp/screenshot.png", full_page=True)
        result = {{"screenshot": "/tmp/screenshot.png", "title": await page.title()}}
"""
        elif action == "click":
            script += f"""
        if "{url}": await page.goto("{url}", wait_until="networkidle")
        await page.click("{selector}")
        if "{wait_for}": await page.wait_for_selector("{wait_for}")
        result = {{"clicked": "{selector}", "url": page.url}}
"""
        elif action == "fill":
            script += f"""
        if "{url}": await page.goto("{url}", wait_until="networkidle")
        await page.fill("{selector}", "{value}")
        result = {{"filled": "{selector}", "value": "{value}"}}
"""
        elif action == "evaluate":
            script += f"""
        if "{url}": await page.goto("{url}", wait_until="networkidle")
        js_result = await page.evaluate("{value}")
        result = {{"js_result": str(js_result)}}
"""
        elif action == "content":
            script += f"""
        await page.goto("{url}", wait_until="networkidle")
        content = await page.content()
        result = {{"html_length": len(content), "title": await page.title(), "content": content[:5000]}}
"""
        elif action == "cookies":
            script += f"""
        await page.goto("{url}", wait_until="networkidle")
        cookies = await page.context.cookies()
        result = {{"cookies": cookies}}
"""
        script += """
        print(json.dumps(result))
        await browser.close()

asyncio.run(main())
"""
        escaped = script.replace("'", "'\\''")
        return ["sh", "-c", f"echo '{escaped}' | python3"]

    def parse_output(self, raw_output: str) -> list[dict]:
        for line in reversed(raw_output.splitlines()):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                return [{"type": "browser_result", "data": data}]
            except json.JSONDecodeError:
                continue
        return [{"type": "browser_result", "data": raw_output.strip()}]
