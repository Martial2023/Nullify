# Nullify — AI Security Engineer Platform

## Projet
Nullify est une plateforme web d'ingénierie de sécurité par IA. L'utilisateur décrit en langage naturel ce qu'il veut tester, l'IA orchestre les outils de sécurité, analyse les résultats, et produit un rapport.
Inspiré de ProjectDiscovery Neo (https://neo.projectdiscovery.io/).

## Architecture
- **Monorepo Turborepo** : `apps/web` (Next.js) + `apps/api` (FastAPI)
- **Frontend** : Next.js 16 App Router, shadcn/ui, Tailwind, Prisma, NextAuth
- **Backend IA** : FastAPI, Claude API (tool_use), Celery + Redis
- **BDD** : PostgreSQL + pgvector
- **Sandbox** : Docker (chaque outil de sécurité dans un conteneur isolé)

## Conventions
- Communiquer en **français** avec le développeur
- Le frontend (Next.js) gère : auth, CRUD, UI chat 3 panneaux
- Le backend (FastAPI) gère : IA, agents, exécution outils, WebSocket streaming
- Prisma est utilisé côté Next.js uniquement
- Les outils de sécurité sont wrappés en Python (subprocess) dans `apps/api/tools/`
- Les agents IA sont dans `apps/api/agents/`

## Stack validée
| Couche | Techno |
|--------|--------|
| Frontend | Next.js 16 + shadcn/ui + Tailwind |
| Backend | FastAPI (Python) |
| ORM | Prisma (Next.js) |
| BDD | PostgreSQL + pgvector |
| LLM | Claude API (tool_use) |
| Queue | Redis + Celery |
| Sandbox | Docker |
| Auth | NextAuth.js |

## Modèle de données
User → Project → ChatSession → Message
Project → Scan → Finding (severity: critical/high/medium/low/info)

## Références
- Specs complètes : `../ai-nullify/nullify-full-specification.md`
- Plan de build : `../ai-nullify/nullify-build-plan.md`
- Résumé et outils : `nullify-resume-et-outils.md`
