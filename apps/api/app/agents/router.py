"""Intelligent Decision Engine — routes user intent to the correct agent."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import httpx

from app.config import settings

if TYPE_CHECKING:
    from app.agents.base import SecurityAgent
    from app.models import HistoryMessage

CLASSIFICATION_PROMPT = """\
You are an intent classifier for a security testing platform called Nullify.
Your job is to analyze the user's message and determine which specialized \
security agent should handle the request.

Available agents:
{agents_block}

Rules:
- Return ONLY a JSON object: {{"agent": "<agent_name>"}}
- Pick the single best agent based on the user's intent.
- If the user asks for recon, subdomain enumeration, or attack surface mapping, \
pick "recon".
- If the user asks about vulnerabilities in a web app, SQL injection, XSS, \
directory bruteforce, or API security testing, pick "web_testing".
- If the user asks to verify, prioritize, or deduplicate findings, pick "triage".
- If the user asks about threat modeling, STRIDE, risk assessment, or trust \
boundaries, pick "threat_modeling".
- If the user asks for code review, static analysis, or secret detection, \
pick "code_review".
- If the user asks about compliance, SOC2, ISO 27001, PCI DSS, cloud security \
posture, pick "compliance".
- If the user asks for a full bug bounty workflow, pick "bug_bounty".
- If the user asks about CTF challenges, pick "ctf".
- If the user asks about CVEs or vulnerability intelligence, pick "cve_intel".
- If the user asks about exploit generation or PoC creation, pick "exploit_gen".
- If the user asks about attack chains or correlating vulnerabilities, \
pick "vuln_correlator".
- If the user asks about technology detection or fingerprinting, \
pick "tech_detector".
- If the message is ambiguous or general, pick "general".
- Do NOT explain your reasoning. Return ONLY the JSON object.
"""


class IntelligentDecisionEngine:
    """Routes user intent to the best matching agent using a lightweight
    LLM classification call."""

    async def classify_intent(
        self,
        message: str,
        history: list[HistoryMessage] | None = None,
        available_agents: list[SecurityAgent] | None = None,
    ) -> str:
        """Return the *name* of the agent best suited for the user's request.

        Falls back to ``"general"`` when classification fails or the model
        returns an unknown agent name.
        """
        if not available_agents:
            return "general"

        agents_block = "\n".join(
            f"- {a.name}: {a.description}" for a in available_agents
        )
        system = CLASSIFICATION_PROMPT.format(agents_block=agents_block)

        # Build a minimal conversation for classification
        messages: list[dict] = [{"role": "system", "content": system}]
        if history:
            for h in history[-4:]:  # last 4 messages for context
                messages.append({"role": h.role.lower(), "content": h.content})
        messages.append({"role": "user", "content": message})

        valid_names = {a.name for a in available_agents}

        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(30, connect=10)) as client:
                resp = await client.post(
                    f"{settings.openrouter_base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.openrouter_api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "http://localhost:3000",
                        "X-Title": "Nullify",
                    },
                    json={
                        "model": "anthropic/claude-haiku-4-5",
                        "messages": messages,
                        "max_tokens": 64,
                        "temperature": 0,
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                raw = data["choices"][0]["message"]["content"].strip()

                # Parse agent name from JSON response
                parsed = json.loads(raw)
                agent_name = parsed.get("agent", "general")
                if agent_name in valid_names:
                    return agent_name
                return "general"

        except Exception:
            return "general"


decision_engine = IntelligentDecisionEngine()
