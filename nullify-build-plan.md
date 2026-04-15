# Nullify - Development Build Plan

## AI Security Engineer Platform

**Version:** 1.0  
**Platform:** Nullify  
**Tagline:** "Nullify threats before they become breaches"

---

## Reference Sources

| Source | URL | Purpose |
|--------|-----|---------|
| **HexStrike AI MCP** | https://github.com/0x4m4/hexstrike-ai | 150+ security tools, 12+ AI agents, MCP server architecture |
| **ProjectDiscovery Neo** | https://neo.projectdiscovery.io/ | UI/UX reference, workflow patterns, Neo primitives |
| **Neo Documentation** | https://docs.neo.projectdiscovery.io/ | Agents, Tools, Memory, Files, Sandboxes specs |
| **InstaVM Security Skills** | https://github.com/instavm/security-skills | Security skills methodology |
| **InstaVM Blog** | https://instavm.io/blog/analysed-4000-to-create-security-agent-cli | 4000+ report analysis approach |
| **HackerOne Dataset** | https://huggingface.co/datasets/Hacker0x01/hackerone_disclosed_reports | Training data for vulnerability patterns |

---

## Executive Summary

Nullify is an AI-powered security engineer platform that automates complex security workflows. Built on:
- **HexStrike AI MCP** architecture (150+ tools, 12+ agents)
- **ProjectDiscovery Neo** UI/UX and workflow patterns
- **4000+ HackerOne bounty reports** for real-world vulnerability patterns

### Core Value Proposition
- **Zero False Positives**: AI-validated findings only
- **Full Automation**: From discovery to remediation
- **Neo-Identical**: Same capabilities as ProjectDiscovery Neo
- **Enhanced**: 150+ tools vs Neo's 40+

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            NULLIFY PLATFORM                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                         USER INTERFACES                               │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │   │
│  │  │   Web UI    │  │   CLI/MCP   │  │   Slack     │  │   GitHub    │  │   │
│  │  │  (Neo-like) │  │   Server    │  │   Bot       │  │   App       │  │   │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  │   │
│  └─────────┴────────────────┴────────────────┴────────────────┴─────────┘   │
│                                    │                                         │
│  ┌─────────────────────────────────▼─────────────────────────────────────┐  │
│  │                     API GATEWAY (FastAPI)                              │  │
│  │              WebSocket + REST API + GraphQL                            │  │
│  └─────────────────────────────────┬─────────────────────────────────────┘  │
│                                    │                                         │
│  ┌─────────────────────────────────▼─────────────────────────────────────┐  │
│  │                    NEO PRIMITIVES (5 Core Concepts)                    │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │  │
│  │  │  AGENTS  │  │  TOOLS   │  │  MEMORY  │  │  FILES   │  │ SANDBOXES│ │  │
│  │  │  12+     │  │  150+    │  │  Vector  │  │  S3      │  │  Docker  │ │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                    INTEGRATIONS                                        │  │
│  │  GitHub │ GitLab │ Slack │ Linear │ Jira │ ServiceNow │ Tenable │ ... │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                    DATA LAYER                                          │  │
│  │  PostgreSQL │ Redis │ Qdrant (Vectors) │ S3 │ Elasticsearch            │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Build Phases

### Phase 1: Foundation (Weeks 1-2)
**Goal:** Set up infrastructure and development environment

#### Tasks
- [ ] Initialize monorepo (Turborepo/Nx)
- [ ] Set up Docker development environment
- [ ] Configure CI/CD (GitHub Actions)
- [ ] Set up databases (PostgreSQL, Redis, Qdrant)
- [ ] Deploy to staging (Kubernetes)

#### Directory Structure
```
nullify/
├── apps/
│   ├── web/                 # Next.js frontend (Neo-like UI)
│   ├── api/                 # FastAPI backend
│   ├── worker/              # Celery task workers
│   ├── mcp-server/          # MCP server (from HexStrike)
│   └── cli/                 # CLI tool
├── packages/
│   ├── ui/                  # Shared UI components
│   ├── core/                # Core business logic
│   ├── tools/               # 150+ security tools
│   ├── agents/              # 12+ AI agents
│   └── skills/              # Security skills library
├── infra/
│   ├── docker/
│   ├── kubernetes/
│   └── terraform/
└── docs/
```

#### Deliverables
- [ ] Running dev environment
- [ ] CI/CD pipeline
- [ ] Database schemas
- [ ] API scaffolding

---

### Phase 2: Core AI Engine (Weeks 3-5)
**Goal:** Implement LLM integration and reasoning engine

#### Tasks
- [ ] LLM provider integration (Claude, GPT-4, local models)
- [ ] Prompt engineering system
- [ ] Streaming response handling
- [ ] Context management
- [ ] Agent Router (combined planner + orchestrator)

#### Key Components
```python
# core/llm/engine.py
class LLMEngine:
    providers = ["anthropic", "openai", "ollama"]
    
    async def reason(self, prompt: str, context: Dict) -> str:
        """Execute reasoning with context"""
        pass
    
    async def plan(self, objective: str) -> List[Task]:
        """Create multi-step execution plan"""
        pass

# core/agents/router.py
class AgentRouter:
    """Single LLM call for planning + tool selection"""
    
    async def route(self, objective: str, context: Dict) -> ExecutionPlan:
        # Analyze objective
        # Select appropriate agent
        # Generate tool sequence
        # Return executable plan
        pass
```

#### Deliverables
- [ ] Working LLM integration
- [ ] Prompt templates
- [ ] Agent Router
- [ ] Streaming chat

---

### Phase 3: Security Tools (Weeks 6-9)
**Goal:** Port HexStrike AI MCP tools to Nullify

**Reference:** https://github.com/0x4m4/hexstrike-ai

#### Tool Categories (150+ Tools)

| Category | Count | Key Tools |
|----------|-------|-----------|
| Network Recon | 25+ | nmap, rustscan, masscan, amass, subfinder |
| Web Security | 40+ | nuclei, sqlmap, gobuster, ffuf, nikto, burp |
| Browser Agent | 10+ | selenium, puppeteer, DOM analysis |
| Auth/Password | 12+ | hydra, john, hashcat, medusa |
| Binary/RE | 25+ | ghidra, radare2, gdb, binwalk, pwntools |
| Cloud Security | 20+ | prowler, trivy, kube-hunter, scout-suite |
| CTF/Forensics | 20+ | volatility, steghide, foremost, exiftool |
| OSINT | 20+ | sherlock, shodan, theharvester, recon-ng |

#### Tasks
- [ ] Port HexStrike MCP tools to TypeScript/Python
- [ ] Create tool registry with caching
- [ ] Implement tool execution sandbox
- [ ] Add progress streaming
- [ ] Create tool documentation

#### Tool Interface
```python
# tools/base.py
class SecurityTool:
    name: str
    description: str
    parameters: Dict
    
    async def execute(self, params: Dict) -> ToolResult:
        """Execute tool in sandbox"""
        pass

# tools/network/nmap.py
class NmapTool(SecurityTool):
    name = "nmap"
    
    async def execute(self, params: Dict) -> ToolResult:
        target = params["target"]
        cmd = f"nmap -sV -sC -O {target}"
        return await self.sandbox.execute(cmd)
```

#### Deliverables
- [ ] 150+ working tools
- [ ] Tool registry API
- [ ] Sandbox execution
- [ ] Real-time output streaming

---

### Phase 4: AI Agents (Weeks 10-12)
**Goal:** Implement 12+ specialized security agents

**Reference:** https://github.com/0x4m4/hexstrike-ai (agent architecture)

#### Agent List

| Agent | Purpose | Tools Used |
|-------|---------|------------|
| IntelligentDecisionEngine | Tool selection, parameter optimization | All |
| BugBountyWorkflowManager | Bug bounty hunting automation | Recon, Web, OSINT |
| CTFWorkflowManager | CTF challenge solving | Binary, Crypto, Forensics |
| CVEIntelligenceManager | Vulnerability intelligence | NVD API, Nuclei |
| AIExploitGenerator | Exploit development assistance | Binary, Pwntools |
| VulnerabilityCorrelator | Attack chain discovery | All |
| ReconAgent | Full-scope reconnaissance | Network, OSINT |
| WebTestingAgent | Application security testing | Web, Browser |
| ThreatModelingAgent | Architecture security review | Analysis |
| CodeReviewAgent | Static code analysis | Semgrep, CodeQL |
| TriageAgent | Finding validation and prioritization | All |
| ComplianceAgent | Compliance and benchmarking | Cloud, Config |

#### Tasks
- [ ] Implement base agent class
- [ ] Create specialized agents
- [ ] Agent memory system
- [ ] Inter-agent communication
- [ ] Agent execution orchestration

#### Agent Architecture
```python
# agents/base.py
class SecurityAgent:
    name: str
    skills: List[str]
    tools: List[str]
    memory: AgentMemory
    
    async def plan(self, objective: str) -> List[Task]:
        """Create execution plan"""
        pass
    
    async def execute(self, task: Task) -> TaskResult:
        """Execute task using tools"""
        pass
    
    async def run(self, objective: str) -> AgentResult:
        """Full agent execution loop with replanning"""
        pass
```

#### Deliverables
- [ ] 12+ working agents
- [ ] Agent orchestration system
- [ ] Agent-specific memory
- [ ] Workflow automation

---

### Phase 5: Memory & Learning (Weeks 13-14)
**Goal:** Implement persistent memory system (Neo-identical)

**Reference:** https://docs.neo.projectdiscovery.io/concepts/memory

#### Memory System
```python
# core/memory/system.py
class MemorySystem:
    """
    Neo-identical memory implementation.
    Learns environment, services, naming conventions, business context.
    """
    
    def __init__(self):
        self.vector_db = QdrantClient()
        self.embedding_model = "text-embedding-3-small"
    
    async def store(self, content: str, metadata: Dict):
        """Store memory with embeddings"""
        embedding = await self.embed(content)
        await self.vector_db.upsert(embedding, metadata)
    
    async def recall(self, query: str, limit: int = 10) -> List[Memory]:
        """Semantic search for relevant memories"""
        embedding = await self.embed(query)
        return await self.vector_db.search(embedding, limit)
    
    async def learn_from_workflow(self, workflow_result: WorkflowResult):
        """Learn from completed workflow"""
        # Extract learnings
        # Store patterns
        # Update context
        pass
```

#### Tasks
- [ ] Set up Qdrant vector database
- [ ] Implement embedding generation
- [ ] Create memory storage/retrieval
- [ ] Build learning pipeline from workflows
- [ ] Implement context injection

#### Deliverables
- [ ] Working vector search
- [ ] Automatic learning from workflows
- [ ] Context persistence across sessions

---

### Phase 6: Sandbox Environment (Weeks 15-16)
**Goal:** Isolated execution environment for tools

**Reference:** https://docs.neo.projectdiscovery.io/concepts/sandboxes

#### Sandbox Architecture
```python
# core/sandbox/manager.py
class SandboxManager:
    """
    Manage isolated execution environments.
    Each task runs in its own container with controlled access.
    """
    
    async def create_sandbox(self, config: SandboxConfig) -> Sandbox:
        """Create isolated Docker/Firecracker sandbox"""
        container = await self.docker.create(
            image="nullify/sandbox:latest",
            network_mode=config.network_mode,
            mem_limit=config.memory_limit,
            cpu_quota=config.cpu_quota
        )
        return Sandbox(container)
    
    async def execute(self, sandbox: Sandbox, command: str) -> ExecutionResult:
        """Execute command in sandbox with streaming output"""
        pass
```

#### Tasks
- [ ] Docker sandbox implementation
- [ ] Network isolation controls
- [ ] Resource limits
- [ ] Real-time output streaming
- [ ] Automatic cleanup

#### Deliverables
- [ ] Working sandbox execution
- [ ] Resource controls
- [ ] Log streaming

---

### Phase 7: Web UI (Weeks 17-21)
**Goal:** Neo-identical 3-panel chat interface

**Reference:** https://neo.projectdiscovery.io/ (UI/UX)

#### UI Layout
```
┌─────────────────┬─────────────────────────┬──────────────────┐
│   LEFT PANEL    │      CENTER PANEL       │   RIGHT PANEL    │
│   (320px)       │      (flex-1)           │   (384px)        │
├─────────────────┼─────────────────────────┼──────────────────┤
│ PROJECT         │ [User Message]          │ ACTIVE TOOLS     │
│ ─────────       │ "Run recon on target"   │ ─────────────    │
│ Acme Corp       │                         │ ┌────────────┐   │
│                 │ [AI Response]           │ │ subfinder  │   │
│ TARGETS         │ "Starting recon..."     │ │ ████████░░ │   │
│ ─────────       │                         │ └────────────┘   │
│ example.com     │ [Tool Execution]        │                  │
│                 │ ┌─────────────────────┐ │ FINDINGS         │
│ MEMORY          │ │ $ subfinder -d ...  │ │ ─────────        │
│ ─────────       │ │ > found 47 subs     │ │ Critical: 2      │
│ Context...      │ └─────────────────────┘ │ High: 5          │
│                 │                         │                  │
│ FILES           │ [Finding Card]          │ LOGS             │
│ ─────────       │ ┌─────────────────────┐ │ ─────────        │
│ report.pdf      │ │ 🔴 SQL Injection    │ │ [streaming...]   │
│                 │ └─────────────────────┘ │                  │
└─────────────────┴─────────────────────────┴──────────────────┘
```

#### Tasks
- [ ] Next.js 14 App Router setup
- [ ] 3-panel layout component
- [ ] Chat message components
- [ ] Tool execution blocks (collapsible)
- [ ] Finding cards (severity-colored)
- [ ] Real-time WebSocket updates
- [ ] Dashboard with charts
- [ ] Findings list with filters
- [ ] Finding detail view

#### Tech Stack
- Next.js 14 (App Router)
- Tailwind CSS
- shadcn/ui components
- Recharts for visualizations
- WebSocket for real-time

#### Deliverables
- [ ] Working chat interface
- [ ] Dashboard
- [ ] Findings management
- [ ] Real-time updates

---

### Phase 8: Integrations (Weeks 22-24)
**Goal:** Connect to external platforms

#### Required Integrations

| Integration | Purpose | Priority |
|-------------|---------|----------|
| GitHub | PR reviews, code scanning, webhooks | P0 |
| GitLab | MR reviews, pipeline integration | P0 |
| Slack | Notifications, chat commands | P0 |
| Linear | Issue tracking, ticket creation | P1 |
| Jira | Issue tracking, ticket creation | P1 |
| Tenable | Import vulnerabilities | P1 |
| DefectDojo | Vulnerability management | P2 |
| ServiceNow | Enterprise ticketing | P2 |

#### Tasks
- [ ] OAuth integration framework
- [ ] Webhook handlers
- [ ] Bidirectional sync
- [ ] Credential management

#### Deliverables
- [ ] Working integrations
- [ ] Webhook support
- [ ] Credential vault

---

### Phase 9: Security Skills Library (Weeks 25-26)
**Goal:** Build skills from 4000+ HackerOne reports

**Reference:** 
- https://github.com/instavm/security-skills
- https://instavm.io/blog/analysed-4000-to-create-security-agent-cli
- https://huggingface.co/datasets/Hacker0x01/hackerone_disclosed_reports

#### Skills Architecture
```python
# skills/processor.py
from datasets import load_dataset

def process_hackerone_reports():
    """Extract patterns from 4000+ HackerOne reports"""
    
    # Load dataset
    dataset = load_dataset("Hacker0x01/hackerone_disclosed_reports")
    df = pd.DataFrame(dataset['train'])
    
    # Filter for bounty-paid reports (higher quality)
    df_bounty = df[df['has_bounty?'] == True]
    
    # Group by vulnerability type
    vuln_groups = df_bounty.groupby('weakness')
    
    skills = {}
    for vuln_type, group in vuln_groups:
        if len(group) >= 10:  # Minimum reports for pattern extraction
            skills[vuln_type] = {
                'reports': group.to_dict('records'),
                'count': len(group),
                'patterns': extract_patterns(group),
                'methodology': extract_methodology(group),
                'severity_distribution': group['severity'].value_counts().to_dict()
            }
    
    return skills
```

#### Example Skill: IDOR Detection
```yaml
# skills/find-idor.yaml
name: find-idor
description: Find IDOR vulnerabilities
triggers: ["idor", "authorization", "access control"]
severity: high
bounty_reports_count: 132

patterns:
  - user_id, userId, user-id, uid, account_id
  - order_id, orderId, booking_id, transaction_id
  - document_id, doc_id, file_id, attachment_id

methodology:
  1. Identify candidate parameters in traffic
  2. Check for sequential/predictable IDs
  3. Test horizontal privilege escalation
  4. Test vertical privilege escalation
  5. Document with evidence

real_examples:
  - url: "https://target.com/api/users/{user_id}"
    bounty: $5000
```

#### Tasks
- [ ] Process HackerOne dataset
- [ ] Extract vulnerability patterns
- [ ] Create skill files for each vuln type
- [ ] Build skill matching engine
- [ ] Integrate with agents

#### Deliverables
- [ ] 50+ security skills
- [ ] Pattern database
- [ ] Skill-to-agent mapping

---

### Phase 10: Testing & Deployment (Weeks 27-28)
**Goal:** Production-ready deployment

#### Testing
- [ ] Unit tests (80% coverage)
- [ ] Integration tests
- [ ] End-to-end tests
- [ ] Security testing (own platform)
- [ ] Performance testing

#### Deployment
- [ ] Kubernetes manifests
- [ ] Helm charts
- [ ] CI/CD pipeline
- [ ] Monitoring (Prometheus, Grafana)
- [ ] Logging (ELK stack)

#### Deliverables
- [ ] Deployed to production
- [ ] Monitoring dashboards
- [ ] Documentation

---

## Technology Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | Next.js 14, Tailwind CSS, shadcn/ui, Recharts |
| **Backend** | FastAPI (Python), TypeScript |
| **Database** | PostgreSQL, Redis, Qdrant |
| **Queue** | Celery, Redis |
| **Sandbox** | Docker, Firecracker |
| **LLM** | Claude API, OpenAI API, Ollama |
| **Infra** | Kubernetes, Terraform, GitHub Actions |

---

## Timeline Summary

| Phase | Duration | Weeks | Deliverable |
|-------|----------|-------|-------------|
| 1. Foundation | 2 weeks | 1-2 | Dev environment, CI/CD |
| 2. Core AI | 3 weeks | 3-5 | LLM integration, Agent Router |
| 3. Security Tools | 4 weeks | 6-9 | 150+ tools ported |
| 4. AI Agents | 3 weeks | 10-12 | 12+ agents |
| 5. Memory | 2 weeks | 13-14 | Vector DB, learning |
| 6. Sandbox | 2 weeks | 15-16 | Isolated execution |
| 7. Web UI | 5 weeks | 17-21 | Neo-identical UI |
| 8. Integrations | 3 weeks | 22-24 | GitHub, Slack, Jira |
| 9. Skills | 2 weeks | 25-26 | 50+ security skills |
| 10. Deployment | 2 weeks | 27-28 | Production ready |

**Total: 28 weeks (7 months)**

---

## Success Metrics

| Metric | Target |
|--------|--------|
| **Tool Count** | 150+ (matching HexStrike) |
| **Agent Count** | 12+ |
| **Neo Feature Parity** | 100% |
| **False Positive Rate** | < 5% |
| **Vulnerability Detection Rate** | > 95% |
| **Response Time** | < 2s for simple queries |
| **Uptime** | 99.9% |

---

## Team Requirements

| Role | Count | Responsibilities |
|------|-------|------------------|
| **Tech Lead** | 1 | Architecture, code review |
| **Backend Engineers** | 2 | API, agents, tools |
| **Frontend Engineer** | 1 | Web UI |
| **ML/AI Engineer** | 1 | LLM integration, memory |
| **DevOps Engineer** | 1 | Infrastructure, CI/CD |
| **Security Engineer** | 1 | Tool integration, testing |

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| LLM API costs | Implement caching, use local models for development |
| Tool compatibility | Start with most critical tools, add incrementally |
| Performance | Async execution, connection pooling, caching |
| Security | Sandbox isolation, network controls, audit logging |

---

## Quick Start Commands

```bash
# Clone repository
git clone https://github.com/your-org/nullify.git
cd nullify

# Start development environment
docker-compose up -d

# Install dependencies
pnpm install

# Run development servers
pnpm dev

# Run tests
pnpm test

# Deploy to staging
kubectl apply -f infra/kubernetes/staging/
```

---

## References

1. **HexStrike AI MCP** - https://github.com/0x4m4/hexstrike-ai
   - 150+ security tools
   - 12+ AI agents
   - MCP server architecture
   - Python implementation

2. **ProjectDiscovery Neo** - https://neo.projectdiscovery.io/
   - UI/UX reference
   - Workflow patterns
   - Enterprise features

3. **Neo Documentation** - https://docs.neo.projectdiscovery.io/
   - Agents, Tools, Memory, Files, Sandboxes
   - Integration patterns

4. **InstaVM Security Skills** - https://github.com/instavm/security-skills
   - Security skills methodology
   - Pattern extraction

5. **InstaVM Blog** - https://instavm.io/blog/analysed-4000-to-create-security-agent-cli
   - 4000+ report analysis
   - Skill creation approach

6. **HackerOne Dataset** - https://huggingface.co/datasets/Hacker0x01/hackerone_disclosed_reports
   - Training data
   - Real vulnerability patterns

---

## Next Steps

1. **Week 1**: Set up repository and development environment
2. **Week 2**: Database schemas and API scaffolding
3. **Week 3**: Begin LLM integration
4. **Week 4**: Start porting HexStrike tools

---

**Document Version:** 1.0  
**Last Updated:** January 2026  
**Author:** Nullify Team
