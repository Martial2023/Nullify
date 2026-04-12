# Nullify — Document de Synthèse

## 1. Résumé du Projet

### Qu'est-ce que Nullify ?

Nullify est une **plateforme web d'ingénierie de sécurité assistée par intelligence artificielle**. Elle permet d'automatiser les tâches de tests de sécurité informatique (pentest, scan de vulnérabilités, reconnaissance, audit de conformité) via une interface conversationnelle (chat).

### Le problème adressé

Les audits de sécurité informatique sont aujourd'hui :
- **Manuels** : un ingénieur doit lancer des dizaines d'outils un par un
- **Lents** : un audit complet prend plusieurs jours à plusieurs semaines
- **Coûteux** : nécessite des experts hautement qualifiés
- **Sujets aux erreurs** : des vulnérabilités passent inaperçues par manque de temps ou d'expertise

### La solution

Nullify centralise et automatise ce processus :

1. L'utilisateur décrit sa demande en langage naturel (ex : *"Teste la sécurité du site example.com"*)
2. L'IA analyse la demande et sélectionne les outils de sécurité appropriés
3. Les outils s'exécutent automatiquement dans un environnement isolé (sandbox)
4. L'IA analyse les résultats, élimine les faux positifs, et produit un rapport clair avec les vulnérabilités détectées et les recommandations de remédiation

### Fonctionnalités principales

| Fonctionnalité | Description |
|----------------|-------------|
| **Chat intelligent** | Interface conversationnelle pour piloter les audits de sécurité |
| **Reconnaissance automatique** | Découverte d'actifs : sous-domaines, ports ouverts, technologies utilisées |
| **Scan de vulnérabilités** | Détection automatique de failles de sécurité (injections SQL, XSS, CVE connues, etc.) |
| **Agents IA spécialisés** | Agents dédiés par domaine : reconnaissance, test web, revue de code, triage |
| **Exécution isolée** | Chaque outil tourne dans un conteneur Docker sécurisé |
| **Rapports automatisés** | Génération de rapports avec sévérité, preuves et recommandations |
| **Mémoire contextuelle** | L'IA retient les résultats précédents pour améliorer ses analyses |
| **Gestion de projets** | Organisation des cibles et historique des scans par projet |

### Cas d'usage

- Audit de sécurité d'applications web
- Reconnaissance d'infrastructure réseau
- Détection de vulnérabilités connues (CVE)
- Revue de code source pour failles de sécurité
- Vérification de conformité (OWASP, etc.)
- Automatisation de workflows de bug bounty

---

## 2. Liste des Outils et Technologies Requis

### 2.1 Technologies de développement

| Catégorie | Outil / Technologie | Rôle | Licence |
|-----------|---------------------|------|---------|
| **Frontend** | Next.js 14 | Framework web (interface utilisateur) | Open Source (MIT) |
| **Frontend** | React 18 | Bibliothèque UI | Open Source (MIT) |
| **Frontend** | Tailwind CSS | Framework CSS | Open Source (MIT) |
| **Frontend** | shadcn/ui | Composants UI pré-construits | Open Source (MIT) |
| **Frontend** | TypeScript | Langage de programmation typé | Open Source (Apache 2.0) |
| **Backend** | Python 3.11+ | Langage de programmation backend | Open Source (PSF) |
| **Backend** | FastAPI | Framework API REST + WebSocket | Open Source (MIT) |
| **Backend** | Celery | Gestionnaire de tâches asynchrones | Open Source (BSD) |
| **ORM** | Prisma | Gestion de la base de données (côté Next.js) | Open Source (Apache 2.0) |
| **Auth** | NextAuth.js | Authentification utilisateur | Open Source (ISC) |

### 2.2 Infrastructure et services

| Catégorie | Outil / Technologie | Rôle | Coût estimé |
|-----------|---------------------|------|-------------|
| **Base de données** | PostgreSQL 16 + pgvector | Stockage des données + mémoire vectorielle IA | Gratuit (Open Source) |
| **Cache / Queue** | Redis 7 | File d'attente des tâches + cache | Gratuit (Open Source) |
| **Conteneurisation** | Docker | Isolation des outils de sécurité | Gratuit (Open Source) |
| **Reverse proxy** | Nginx | Routage du trafic + SSL | Gratuit (Open Source) |
| **CI/CD** | GitHub Actions | Tests automatisés et déploiement | Gratuit (2000 min/mois) |
| **Hébergement** | VPS Linux (Ubuntu) | Serveur de production | 10-20 €/mois |
| **Domaine + SSL** | Let's Encrypt | Certificat HTTPS | Gratuit |

### 2.3 Services externes (API)

| Service | Rôle | Coût estimé |
|---------|------|-------------|
| **Anthropic Claude API** | Intelligence artificielle (raisonnement, orchestration des outils) | ~20-50 $/mois selon usage |
| **GitHub** | Hébergement du code source | Gratuit |

### 2.4 Outils de sécurité intégrés à la plateforme

Ces outils sont open source et seront intégrés dans la plateforme pour être pilotés par l'IA.

#### Reconnaissance et découverte

| Outil | Fonction | Licence |
|-------|----------|---------|
| subfinder | Découverte de sous-domaines | Open Source (MIT) |
| amass | Cartographie de surface d'attaque | Open Source (Apache 2.0) |
| httpx | Vérification de serveurs HTTP actifs | Open Source (MIT) |
| dnsx | Résolution et analyse DNS | Open Source (MIT) |

#### Scan réseau

| Outil | Fonction | Licence |
|-------|----------|---------|
| nmap | Scan de ports et services | Open Source (NPSL) |
| rustscan | Scan de ports rapide | Open Source (GPL 3.0) |
| masscan | Scan de ports à grande échelle | Open Source (AGPL) |

#### Scan de vulnérabilités web

| Outil | Fonction | Licence |
|-------|----------|---------|
| nuclei | Scan de vulnérabilités basé sur des templates | Open Source (MIT) |
| sqlmap | Détection et exploitation d'injections SQL | Open Source (GPL 2.0) |
| nikto | Scan de serveurs web | Open Source (GPL) |
| ffuf | Fuzzing web (découverte de répertoires/fichiers) | Open Source (MIT) |
| gobuster | Brute force de répertoires et DNS | Open Source (Apache 2.0) |
| wapiti | Scan de vulnérabilités web | Open Source (GPL 2.0) |
| dalfox | Détection de failles XSS | Open Source (MIT) |

#### Analyse et fingerprinting

| Outil | Fonction | Licence |
|-------|----------|---------|
| whatweb | Identification des technologies web | Open Source (GPL 2.0) |
| wappalyzer | Détection de stack technologique | Open Source (MIT) |
| wafw00f | Détection de Web Application Firewalls | Open Source (BSD) |

#### OSINT (Renseignement en sources ouvertes)

| Outil | Fonction | Licence |
|-------|----------|---------|
| theHarvester | Collecte d'emails, noms, sous-domaines | Open Source (GPL 2.0) |
| shodan (CLI) | Recherche d'appareils connectés | Freemium |

#### Analyse de code

| Outil | Fonction | Licence |
|-------|----------|---------|
| semgrep | Analyse statique de code source | Open Source (LGPL) |
| bandit | Analyse de sécurité de code Python | Open Source (Apache 2.0) |
| trivy | Scan de vulnérabilités dans les dépendances et conteneurs | Open Source (Apache 2.0) |

---

## 3. Estimation budgétaire

### Coûts mensuels de fonctionnement (production)

| Poste | Coût mensuel |
|-------|-------------|
| VPS Hébergement (4 GB RAM, 2 vCPU) | 10 - 20 € |
| Claude API (Anthropic) | 20 - 50 $ |
| Domaine (.com) | ~1 €/mois (12 €/an) |
| **Total estimé** | **30 - 70 €/mois** |

> Tous les outils de sécurité et technologies de développement utilisés sont **open source et gratuits**.

---

## 4. Livrables attendus

| # | Livrable | Description |
|---|----------|-------------|
| 1 | **Application web fonctionnelle** | Interface chat + dashboard, accessible via navigateur |
| 2 | **Backend API** | Serveur FastAPI avec orchestration IA et exécution des outils |
| 3 | **Intégration de 20+ outils de sécurité** | Outils opérationnels, pilotables par l'IA via le chat |
| 4 | **4+ agents IA spécialisés** | Reconnaissance, test web, revue de code, triage |
| 5 | **Système d'exécution isolé** | Sandbox Docker pour chaque outil |
| 6 | **Base de données** | Stockage des utilisateurs, projets, scans, findings |
| 7 | **Documentation technique** | Architecture, installation, utilisation |
| 8 | **Environnement de déploiement** | Docker Compose prêt pour la production |

---

*Document rédigé le 11 avril 2026*
