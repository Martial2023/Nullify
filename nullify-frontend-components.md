# Nullify — Architecture Frontend (Composants & Communication)

**Objectif :** Liste exhaustive des composants React/Next.js à développer pour reproduire l'interface de `nullify-live-preview.html`, avec communication temps réel vers FastAPI.

**Stack frontend :** Next.js 16 (App Router) + TypeScript + Tailwind + shadcn/ui + Zustand + TanStack Query + Socket.IO (ou WebSocket natif).

---

## 1. Vue d'ensemble de l'architecture frontend

```
apps/web/
├── app/                              # Routes Next.js (App Router)
│   ├── (auth)/
│   │   ├── login/page.tsx
│   │   └── register/page.tsx
│   ├── (app)/                        # Routes authentifiées
│   │   ├── layout.tsx                # Layout principal avec Sidebar
│   │   ├── dashboard/page.tsx
│   │   ├── chat/page.tsx             # Redirection vers dernière session
│   │   ├── chat/[projectId]/page.tsx # Interface chat 3 panneaux
│   │   ├── tasks/page.tsx
│   │   ├── findings/page.tsx
│   │   ├── findings/[id]/page.tsx
│   │   ├── assets/page.tsx
│   │   └── reports/page.tsx
│   └── api/                          # API Routes Next.js (CRUD via Prisma)
│
├── components/
│   ├── layout/                       # Structure globale
│   ├── chat/                         # Interface chat
│   ├── findings/                     # Gestion findings
│   ├── dashboard/                    # Widgets dashboard
│   ├── shared/                       # Composants réutilisables
│   └── ui/                           # shadcn/ui (Button, Input, etc.)
│
├── hooks/                            # Hooks custom
├── lib/                              # Clients API, WebSocket, utilitaires
├── stores/                           # Stores Zustand (état global)
└── types/                            # Types TypeScript
```

---

## 2. Composants de layout (structure globale)

### 2.1 `AppShell.tsx`
**Rôle :** Conteneur racine — englobe Sidebar + MainContent.
**Pourquoi :** Toutes les pages authentifiées partagent la même structure (sidebar gauche + zone principale).
**Communication :** Aucune (pur layout).

### 2.2 `Sidebar.tsx`
**Rôle :** Navigation verticale gauche avec logo, bouton "New Chat", menu Main, liste des projets, profil utilisateur.
**Enfants :** `SidebarNav`, `SidebarProjects`, `UserProfile`.
**Communication :** 
- **REST** `GET /api/projects` (via Next.js API Route + Prisma) pour lister les projets.
- **REST** `POST /api/chat-sessions` pour créer une nouvelle session au clic sur "New Chat".

### 2.3 `SidebarNav.tsx`
**Rôle :** Liens de navigation (Dashboard, Chat, Tasks, Findings, Assets, Reports) avec badges de compteur.
**Pourquoi séparé :** Les badges (Tasks 3, Findings 47) doivent se mettre à jour en temps réel.
**Communication :** 
- **REST** `GET /api/stats/counts` (findings ouvertes, tâches actives).
- **WebSocket** `counts.updated` pour rafraîchir les badges quand un scan termine.

### 2.4 `SidebarProjects.tsx`
**Rôle :** Liste cliquable des projets de l'utilisateur.
**Communication :** **REST** `GET /api/projects`.

### 2.5 `UserProfile.tsx`
**Rôle :** Carte profil en bas de la sidebar (avatar, nom, plan).
**Communication :** Données déjà en session (NextAuth).

### 2.6 `TopBar.tsx` *(optionnel selon design final)*
**Rôle :** Barre supérieure avec breadcrumb, recherche globale, notifications.

---

## 3. Composants Dashboard

### 3.1 `DashboardPage.tsx`
**Rôle :** Page complète — orchestre stats, charts, et table récente.
**Communication :** 
- **REST** `GET /api/dashboard/overview?range=30d` — renvoie stats agrégées.
- **WebSocket** `finding.created`, `scan.completed` pour rafraîchir en temps réel.

### 3.2 `StatsGrid.tsx`
**Rôle :** Grille de 4 cartes stats (Active Tasks, Open Findings, Assets Monitored, Compliance Score).
**Enfants :** `StatCard`.

### 3.3 `StatCard.tsx`
**Rôle :** Carte individuelle avec icône, valeur, delta (+3, -8), label.
**Props :** `icon`, `value`, `delta`, `label`, `color`.
**Pourquoi réutilisable :** 4 instances identiques avec couleurs différentes.

### 3.4 `SeverityChart.tsx`
**Rôle :** Barres horizontales par sévérité (Critical/High/Medium/Low/Info).
**Pourquoi :** Visualisation immédiate de la distribution des findings.
**Communication :** Données via `DashboardPage` props.

### 3.5 `TrendChart.tsx`
**Rôle :** Histogramme hebdomadaire (W1-W4) des findings.
**Librairie suggérée :** Recharts ou Tremor (simples, compatibles Next.js).

### 3.6 `RecentFindingsTable.tsx`
**Rôle :** Table des 5 derniers findings avec lien vers vue détaillée.
**Réutilise :** `SeverityBadge`, `StatusBadge`.

### 3.7 `DateRangeSelector.tsx`
**Rôle :** Select "Last 7/30/90 days" — filtre les données du dashboard.
**Communication :** Déclenche re-fetch de `GET /api/dashboard/overview`.

---

## 4. Composants Chat (le cœur de l'application)

### 4.1 `ChatLayout.tsx`
**Rôle :** Conteneur 3 colonnes — ContextPanel (320px) | ChatArea (flex) | ToolsPanel (384px).
**Pourquoi :** Layout spécifique à la vue chat, différent des autres pages.

### 4.2 `ContextPanel.tsx` (panneau gauche)
**Rôle :** Affiche le contexte de la session courante (Project, Targets, Memory, Files).
**Enfants :** `ProjectCard`, `TargetsList`, `MemoryList`, `FilesList`.
**Communication :** 
- **REST** `GET /api/projects/:id` — projet courant avec targets.
- **REST** `GET /api/projects/:id/memory` — entrées mémoire (via FastAPI qui lit pgvector).

### 4.3 `TargetsList.tsx`
**Rôle :** Liste éditable des cibles (api.example.com, app.example.com).
**Communication :** **REST** `POST/DELETE /api/projects/:id/targets`.

### 4.4 `MemoryList.tsx`
**Rôle :** Affiche les faits mémorisés par l'IA (framework, auth, DB).
**Pourquoi séparé :** La mémoire vient de pgvector côté FastAPI, pas de Prisma direct.
**Communication :** **REST** `GET /api/memory/:projectId` (proxy vers FastAPI).

### 4.5 `FilesList.tsx`
**Rôle :** Fichiers uploadés au projet (scope.txt, api-docs.pdf).
**Communication :** 
- **REST** `GET /api/projects/:id/files`.
- **REST** `POST /api/files/upload` (multipart) vers FastAPI pour stockage S3.

---

### 4.6 `ChatArea.tsx` (panneau central)
**Rôle :** Container principal — messages + input.
**Enfants :** `MessageList`, `ChatInput`, `QuickActions`.
**Communication WebSocket principale :** 
- **WS ↔ FastAPI** `ws://api/chat/:sessionId` — flux bidirectionnel pour messages et tool events.

### 4.7 `MessageList.tsx`
**Rôle :** Liste scrollable des messages avec auto-scroll vers le bas.
**Enfants :** `UserMessage`, `AssistantMessage`.
**Pourquoi :** Doit gérer le streaming (messages qui s'affichent caractère par caractère).

### 4.8 `UserMessage.tsx`
**Rôle :** Bulle utilisateur (fond indigo, aligné à droite) avec timestamp.
**Props :** `content`, `timestamp`.

### 4.9 `AssistantMessage.tsx`
**Rôle :** Bulle assistant (avec mascotte à gauche) + contenu texte + blocs d'outils + boutons d'action.
**Enfants :** `MascotAvatar`, `MarkdownRenderer`, `ToolExecutionBlock`, `FindingPreview`.
**Pourquoi complexe :** Un message peut contenir du texte + plusieurs blocs d'outils + récapitulatif.

### 4.10 `MarkdownRenderer.tsx`
**Rôle :** Rendu markdown + syntax highlighting pour code.
**Librairie :** `react-markdown` + `rehype-highlight`.
**Pourquoi :** L'IA répond en markdown (listes, code blocks, tableaux).

### 4.11 `ToolExecutionBlock.tsx` ⭐ (composant clé)
**Rôle :** Carte montrant un outil en cours d'exécution — header avec nom, progress bar, icône de statut + terminal de sortie en live.
**Enfants :** `ToolHeader`, `TerminalOutput`, `ProgressBar`.
**États :** `pending | running | completed | failed`.
**Communication WebSocket :** 
- Écoute `tool.started` → crée le bloc.
- Écoute `tool.output` → append à `TerminalOutput`.
- Écoute `tool.progress` → update `ProgressBar`.
- Écoute `tool.completed` / `tool.failed` → change icône et finalise.

### 4.12 `TerminalOutput.tsx`
**Rôle :** Affichage façon terminal (monospace, fond sombre) avec coloration par niveau (INF bleu, ERR rouge, OK vert).
**Pourquoi :** Reproduit fidèlement la sortie console des outils (nmap, nuclei...).
**Optimisation :** Virtualisation si > 500 lignes (react-window).

### 4.13 `ProgressBar.tsx`
**Rôle :** Barre de progression animée avec pourcentage.
**Props :** `progress` (0-100), `status`.

### 4.14 `FindingPreview.tsx`
**Rôle :** Carte inline dans le chat quand l'IA annonce un finding (severity, titre, endpoint).
**Action :** Clic → ouvre `FindingDetailDrawer` ou navigue vers `/findings/:id`.

### 4.15 `ChatInput.tsx`
**Rôle :** Zone de saisie (textarea auto-resize) + bouton envoi + upload fichier.
**Fonctionnalités :**
- Ctrl+Enter pour envoyer.
- Auto-resize à 5 lignes max.
- Indicateur "AI is typing...".
**Communication :** 
- Envoie message via **WebSocket** `chat.message`.
- Upload fichier via **REST** `POST /api/files/upload`.

### 4.16 `QuickActions.tsx`
**Rôle :** Boutons d'actions rapides ("Run nuclei scan", "Check compliance", "Generate report").
**Pourquoi :** Préremplit le message ou déclenche directement une commande.

### 4.17 `MascotAvatar.tsx`
**Rôle :** Avatar animé de Nullify à gauche des messages assistant.
**Animations :** idle (flottement) + wave (réponse reçue).
**Pourquoi séparé :** Animations complexes, toggle on/off, réutilisé en mode fixed bottom-right.

---

### 4.18 `ToolsPanel.tsx` (panneau droit)
**Rôle :** Container — résumé live des outils actifs, findings détectés, logs.
**Enfants :** `ActiveToolsList`, `FindingsPreviewList`, `LogsStream`.

### 4.19 `ActiveToolsList.tsx`
**Rôle :** Liste des outils en cours ou récemment terminés avec statut (✓ Complete, ⟳ Running).
**Communication WS :** Synchronisé avec `tool.*` events.

### 4.20 `FindingsPreviewList.tsx`
**Rôle :** Liste condensée des findings de la session courante (clic → detail).
**Communication WS :** Écoute `finding.created`.

### 4.21 `LogsStream.tsx`
**Rôle :** Flux textuel temps réel horodaté `[2:34:01] Chat started`.
**Communication WS :** Écoute `log.entry`.

---

## 5. Composants Findings

### 5.1 `FindingsPage.tsx`
**Rôle :** Page complète — header + filtres + table + pagination.
**Communication :** **REST** `GET /api/findings?severity=&status=&asset=&page=`.

### 5.2 `SeverityBadges.tsx`
**Rôle :** Rangée de badges résumé (8 Critical, 15 High, 12 Medium...).
**Pourquoi :** Cliquable pour filtrer rapidement.

### 5.3 `FindingsFilters.tsx`
**Rôle :** Barre de filtres (recherche texte, severity select, status select, asset select).
**Communication :** Met à jour les query params → re-fetch table.

### 5.4 `FindingsTable.tsx`
**Rôle :** Table paginée avec checkbox sélection, severity, title, asset, status, age.
**Fonctionnalités :** Tri par colonne, sélection multiple, actions groupées.

### 5.5 `FindingsTableRow.tsx`
**Rôle :** Ligne individuelle — clic navigue vers `/findings/:id`.

### 5.6 `Pagination.tsx`
**Rôle :** Pagination avec numéros de pages et flèches.
**Réutilisable :** Aussi dans d'autres tables (scans, assets, reports).

---

## 6. Composants Finding Detail

### 6.1 `FindingDetailPage.tsx`
**Rôle :** Page détaillée d'un finding (2 colonnes : contenu principal + sidebar).
**Communication :** **REST** `GET /api/findings/:id`.

### 6.2 `FindingHeader.tsx`
**Rôle :** Header avec badge sévérité, titre, métadonnées (CVE, CWE, CVSS), actions (Assign, Export, Mark as Fixed).
**Actions communication :** **REST** `PATCH /api/findings/:id`.

### 6.3 `FindingDescription.tsx`
**Rôle :** Description + reproduction steps + evidence (code block).

### 6.4 `FindingRemediation.tsx`
**Rôle :** Étapes de remédiation + suggestion de code fix (diff avant/après).

### 6.5 `FindingDetailsSidebar.tsx`
**Rôle :** Panneau droit avec Details, References, Activity.

### 6.6 `FindingActivity.tsx`
**Rôle :** Timeline verticale des événements (créé, validé, assigné, fixed).

### 6.7 `CodeDiff.tsx`
**Rôle :** Rendu diff avant/après pour suggestions de fix.
**Librairie :** `react-diff-viewer` ou custom.

---

## 7. Composants partagés (réutilisables)

### 7.1 `SeverityBadge.tsx`
**Rôle :** Badge coloré `Critical|High|Medium|Low|Info` avec point de couleur.
**Pourquoi centralisé :** Utilisé dans 10+ endroits — cohérence visuelle.

### 7.2 `StatusBadge.tsx`
**Rôle :** Badge de statut `Open|In Review|Fixed|Running|Completed|Failed`.

### 7.3 `EmptyState.tsx`
**Rôle :** État vide (aucune donnée) avec illustration et CTA.

### 7.4 `LoadingSpinner.tsx` / `SkeletonLoader.tsx`
**Rôle :** Indicateurs de chargement.

### 7.5 `ErrorBoundary.tsx`
**Rôle :** Capture les erreurs React et affiche un fallback.

### 7.6 `ConfirmDialog.tsx`
**Rôle :** Modale de confirmation (ex: "Supprimer ce projet ?").

### 7.7 `Toast.tsx` (via shadcn/ui)
**Rôle :** Notifications temporaires (succès, erreur).
**Usage :** Scan démarré, finding créé, erreur réseau.

### 7.8 `FloatingMascot.tsx`
**Rôle :** Mascotte en bas à droite (hors page chat) avec bulle de dialogue proactive.

---

## 8. Composants UI de base (shadcn/ui)

À installer via `npx shadcn-ui add` :
- `button`, `input`, `textarea`, `select`, `checkbox`, `switch`
- `dialog`, `drawer`, `sheet`, `popover`, `tooltip`
- `table`, `tabs`, `accordion`
- `badge`, `avatar`, `separator`, `scroll-area`
- `toast`, `alert`, `skeleton`
- `dropdown-menu`, `command` (pour palette de commandes future)

---

## 9. Hooks custom

### 9.1 `useWebSocket.ts`
**Rôle :** Hook principal de connexion WS à FastAPI.
**Responsabilités :**
- Connexion/reconnexion automatique avec backoff exponentiel.
- Dispatch des events reçus vers les stores Zustand.
- Envoi de messages typés.
**Interface :** `const { send, lastMessage, status } = useWebSocket(sessionId)`.

### 9.2 `useChat.ts`
**Rôle :** Gestion d'une session de chat (messages, envoi, streaming).
**Retourne :** `{ messages, sendMessage, isStreaming, activeTools }`.

### 9.3 `useToolStream.ts`
**Rôle :** Écoute les events d'un outil spécifique (par toolCallId).
**Pourquoi :** Chaque `ToolExecutionBlock` consomme ses propres events.

### 9.4 `useFindings.ts` *(via TanStack Query)*
**Rôle :** Fetch + cache des findings avec invalidation sur WS events.

### 9.5 `useProject.ts`
**Rôle :** Récupère projet + targets + memory + files.

### 9.6 `useDebounce.ts`
**Rôle :** Debounce pour la barre de recherche des findings.

### 9.7 `useIntersectionObserver.ts`
**Rôle :** Infinite scroll ou lazy load des messages.

---

## 10. Stores Zustand (état global)

### 10.1 `authStore.ts`
**État :** `user`, `session`, `login()`, `logout()`.
**Source :** NextAuth.

### 10.2 `chatStore.ts`
**État :** `sessions`, `activeSessionId`, `messages[]`, `isStreaming`.
**Pourquoi Zustand :** Les messages arrivent via WS et doivent être accessibles partout (MessageList, ToolsPanel, LogsStream).

### 10.3 `toolsStore.ts`
**État :** `activeTools[]`, `completedTools[]`, `toolOutputs{}`.
**Update source :** Events WS `tool.*`.

### 10.4 `findingsStore.ts`
**État :** `findings[]`, `filters`, `selectedIds[]`.

### 10.5 `uiStore.ts`
**État :** `sidebarCollapsed`, `mascotEnabled`, `theme`.

---

## 11. Clients API et WebSocket

### 11.1 `lib/api-client.ts`
**Rôle :** Wrapper fetch typé pour Next.js API Routes (utilise Prisma).
**Méthodes :** `api.projects.list()`, `api.findings.get(id)`, etc.

### 11.2 `lib/fastapi-client.ts`
**Rôle :** Client REST vers FastAPI (endpoints IA, scans, memory).
**Auth :** JWT en header depuis la session NextAuth.

### 11.3 `lib/websocket-client.ts`
**Rôle :** Singleton WebSocket avec :
- Reconnexion automatique.
- Heartbeat (ping/pong toutes les 30s).
- Queue des messages en cas de déconnexion.
- Type-safety via schémas Zod des événements.

### 11.4 `lib/event-schemas.ts`
**Rôle :** Schémas Zod de TOUS les événements WebSocket (validation runtime).
**Exemples :** `ChatMessageSchema`, `ToolStartedSchema`, `ToolOutputSchema`, `FindingCreatedSchema`.

---

## 12. Types TypeScript (types/*.ts)

### 12.1 `types/chat.ts`
```
Message, ChatSession, ToolCall, StreamingState
```

### 12.2 `types/scan.ts`
```
Scan, ScanStatus, ScanResult
```

### 12.3 `types/finding.ts`
```
Finding, Severity, FindingStatus, Evidence, Remediation
```

### 12.4 `types/websocket.ts`
```
WSEvent (union discriminée de tous les events), WSStatus
```

### 12.5 `types/project.ts`
```
Project, Target, MemoryEntry, ProjectFile
```

---

## 13. Communication FastAPI — Stratégie REST vs WebSocket

### 13.1 REST (requêtes ponctuelles, CRUD)
| Action | Endpoint | Client |
|--------|----------|--------|
| Liste projets | `GET /api/projects` | Next.js API + Prisma |
| Créer projet | `POST /api/projects` | Next.js API + Prisma |
| Liste findings filtrés | `GET /api/findings` | Next.js API + Prisma |
| Détail finding | `GET /api/findings/:id` | Next.js API + Prisma |
| Stats dashboard | `GET /api/dashboard/overview` | Next.js API + Prisma |
| Upload fichier | `POST /api/files/upload` | FastAPI (stockage S3) |
| Memory entries | `GET /fastapi/memory/:projectId` | FastAPI (pgvector) |
| Lancer scan manuel | `POST /fastapi/scans/start` | FastAPI |

### 13.2 WebSocket (temps réel, streaming)
**Endpoint :** `ws://localhost:8000/ws/chat/:sessionId` (FastAPI).

**Events client → serveur :**
| Event | Payload | Usage |
|-------|---------|-------|
| `chat.message` | `{ content, attachments? }` | Envoi message user |
| `chat.cancel` | `{ messageId }` | Annule une génération |
| `tool.approve` | `{ toolCallId }` | Approuve un outil sensible |
| `ping` | `{}` | Heartbeat |

**Events serveur → client :**
| Event | Payload | Consommateur |
|-------|---------|--------------|
| `message.start` | `{ messageId }` | `AssistantMessage` crée le conteneur |
| `message.token` | `{ messageId, token }` | Stream texte caractère par caractère |
| `message.complete` | `{ messageId }` | Fin du stream texte |
| `tool.started` | `{ toolCallId, name, args }` | `ToolExecutionBlock` apparaît |
| `tool.output` | `{ toolCallId, line, level }` | Append dans `TerminalOutput` |
| `tool.progress` | `{ toolCallId, percent }` | Update `ProgressBar` |
| `tool.completed` | `{ toolCallId, result }` | Icône ✓ verte |
| `tool.failed` | `{ toolCallId, error }` | Icône ✗ rouge |
| `finding.created` | `{ finding }` | `FindingPreview` inline + panneau droit |
| `log.entry` | `{ timestamp, message, level }` | `LogsStream` |
| `pong` | `{}` | Heartbeat réponse |

**Pourquoi WebSocket :**
- Le LLM streame sa réponse token par token.
- Les outils (nmap, nuclei) émettent des lignes de sortie en continu (parfois pendant plusieurs minutes).
- Plusieurs composants doivent réagir simultanément (MessageList + ToolsPanel + LogsStream) — un seul flux alimente tout.

### 13.3 SSE (Server-Sent Events) — alternative
Si WebSocket bidirectionnel pas nécessaire, SSE suffit pour le streaming serveur → client. FastAPI supporte les deux. **Recommandation : WebSocket** car l'utilisateur peut vouloir annuler une tâche en cours.

---

## 14. Flux complet : message utilisateur → réponse streamée

```
1. User tape "Scanne api.example.com" dans ChatInput
   │
2. ChatInput.onSend() → chatStore.addMessage({ role: 'user', content })
   │                  → websocketClient.send({ type: 'chat.message', content })
   │
3. FastAPI reçoit, appelle Claude API avec tool_use
   │
4. Claude répond → FastAPI streame vers le client :
   │  • message.start → AssistantMessage créé (vide)
   │  • message.token * N → MessageList affiche texte qui se construit
   │
5. Claude demande tool_use nuclei :
   │  • tool.started → ToolExecutionBlock ajouté + ActiveToolsList update
   │
6. FastAPI lance nuclei dans Docker, streame stdout :
   │  • tool.output * N → TerminalOutput append lignes
   │  • tool.progress → ProgressBar avance
   │
7. nuclei trouve SQLi :
   │  • finding.created → FindingPreview inline + FindingsPreviewList + Toast
   │  • Sidebar badge "Findings" incrémente via counts.updated
   │
8. Tool termine :
   │  • tool.completed → ProgressBar 100% + icône ✓
   │
9. Claude résume les findings :
   │  • message.token * N → texte final
   │  • message.complete → curseur de typing disparaît
   │
10. log.entry tout le long alimente LogsStream
```

---

## 15. Ordre de développement recommandé

1. **Fondations** : AppShell, Sidebar, SidebarNav, routing, auth NextAuth.
2. **UI de base** : installer shadcn/ui, créer SeverityBadge, StatusBadge, Pagination.
3. **Dashboard** : StatCard, StatsGrid, SeverityChart, RecentFindingsTable (données mock d'abord).
4. **Findings** : FindingsTable, FindingsFilters, FindingDetailPage.
5. **WebSocket client** : `lib/websocket-client.ts`, `useWebSocket`, store tools.
6. **Chat (structure)** : ChatLayout, ContextPanel, ToolsPanel (sans logique).
7. **Chat (messages)** : MessageList, UserMessage, AssistantMessage, ChatInput.
8. **Chat (temps réel)** : ToolExecutionBlock, TerminalOutput, streaming messages.
9. **Polish** : animations mascotte, toasts, empty states, skeleton loaders.
10. **Optimisations** : virtualisation listes, code splitting, suspense boundaries.

---

## 16. Synthèse — Pourquoi cette architecture

| Choix | Raison |
|-------|--------|
| **Composants atomiques** | Un `ToolExecutionBlock` autonome → testable + réutilisable |
| **Stores Zustand** | Les events WS alimentent plusieurs composants sans prop drilling |
| **TanStack Query** | Cache + revalidation automatique pour les données REST |
| **WebSocket unique par session** | Un seul flux alimente chat + tools + logs → cohérence garantie |
| **Zod sur les events** | Validation runtime = pas de crash si FastAPI change un payload |
| **Next.js API Routes + Prisma pour CRUD** | Tu gardes ta stack connue, FastAPI ne fait que l'IA/outils |
| **shadcn/ui** | Composants copiés dans le projet, full control, zéro dépendance UI |

Résultat : interface fluide, 60fps même pendant un scan qui produit 1000 lignes de logs, reconnexion WS transparente, et chaque composant a une responsabilité unique.
