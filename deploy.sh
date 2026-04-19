#!/usr/bin/env bash
# Deploy script pour le VPS Nullify — API uniquement.
# Appelé par ~/scripts/deploy-api.sh après git pull.
# La partie web (Next.js) est gérée par un service séparé.
#
# Responsabilités :
#   1. Dépendances Python à jour
#   2. Build des images Docker de sécurité (9 images)
#   3. PATH systemd correct
#   4. Service redémarré
#   5. Healthcheck
#
# Variables d'environnement attendues :
#   NULLIFY_ROOT   — racine du repo (défaut : /home/dev/Nullify)
#   SERVICE_NAME   — nom du service systemd (défaut : nullify-api)

set -euo pipefail

NULLIFY_ROOT="${NULLIFY_ROOT:-/home/dev/Nullify}"
SERVICE_NAME="${SERVICE_NAME:-nullify-api}"
API_DIR="${NULLIFY_ROOT}/apps/api"
VENV_DIR="${API_DIR}/.venv"
DOCKER_DIR="${NULLIFY_ROOT}/docker"

log() { echo "[deploy] $*"; }

# ─── 1. Python venv + deps ──────────────────────────────────
log "1/5 Python dépendances"

if [[ ! -d "${VENV_DIR}" ]]; then
  log "  Création du venv…"
  python3.11 -m venv "${VENV_DIR}"
fi

# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"
pip install --quiet --upgrade pip
pip install --quiet -e "${API_DIR}"
deactivate

# ─── 2. Build des images Docker de sécurité ──────────────────
log "2/5 Build des images Docker de sécurité"

# Liste des images à construire : nom_image:dockerfile
TOOL_IMAGES=(
  "nullify-tools:Dockerfile.tools"
  "nullify-tools-network:Dockerfile.tools-network"
  "nullify-tools-web:Dockerfile.tools-web"
  "nullify-tools-auth:Dockerfile.tools-auth"
  "nullify-tools-binary:Dockerfile.tools-binary"
  "nullify-tools-cloud:Dockerfile.tools-cloud"
  "nullify-tools-forensics:Dockerfile.tools-forensics"
  "nullify-tools-osint:Dockerfile.tools-osint"
  "nullify-tools-browser:Dockerfile.tools-browser"
)

BUILT=0
FAILED=0
SKIPPED=0

for entry in "${TOOL_IMAGES[@]}"; do
  IMAGE="${entry%%:*}:latest"
  DOCKERFILE="${entry##*:}"

  if [[ ! -f "${DOCKER_DIR}/${DOCKERFILE}" ]]; then
    log "  ⚠ ${DOCKERFILE} non trouvé, skip"
    ((SKIPPED++))
    continue
  fi

  # Rebuild si l'image n'existe pas ou si le Dockerfile a changé
  # depuis le dernier build (comparaison par date de modification)
  NEEDS_BUILD=0
  if ! docker image inspect "${IMAGE}" >/dev/null 2>&1; then
    NEEDS_BUILD=1
  elif [[ "${FORCE_REBUILD:-0}" == "1" ]]; then
    NEEDS_BUILD=1
  fi

  if [[ ${NEEDS_BUILD} -eq 1 ]]; then
    log "  Building ${IMAGE} (${DOCKERFILE})..."
    if docker build -t "${IMAGE}" -f "${DOCKER_DIR}/${DOCKERFILE}" "${DOCKER_DIR}" 2>&1 | tail -5; then
      log "  ✓ ${IMAGE}"
      ((BUILT++))
    else
      log "  ✗ ${IMAGE} — build échoué, skip"
      ((FAILED++))
    fi
  else
    log "  ${IMAGE} déjà présente, skip (FORCE_REBUILD=1 pour rebuild)"
    ((SKIPPED++))
  fi
done

log "  Résultat: ${BUILT} buildées, ${SKIPPED} skippées, ${FAILED} échouées"

# ─── 3. Override systemd (PATH) ─────────────────────────────
log "3/5 Override systemd"

OVERRIDE_DIR="/etc/systemd/system/${SERVICE_NAME}.service.d"
OVERRIDE_FILE="${OVERRIDE_DIR}/override.conf"
EXPECTED_PATH="${VENV_DIR}/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

sudo mkdir -p "${OVERRIDE_DIR}"

NEEDS_RELOAD=0
if [[ ! -f "${OVERRIDE_FILE}" ]] || ! grep -q "${EXPECTED_PATH}" "${OVERRIDE_FILE}"; then
  log "  Écriture de ${OVERRIDE_FILE}"
  sudo tee "${OVERRIDE_FILE}" >/dev/null <<EOF
[Service]
Environment=
Environment="PATH=${EXPECTED_PATH}"
EOF
  NEEDS_RELOAD=1
else
  log "  Override déjà à jour, skip"
fi

# ─── 4. Restart service ─────────────────────────────────────
log "4/5 Restart ${SERVICE_NAME}"

if [[ ${NEEDS_RELOAD} -eq 1 ]]; then
  sudo systemctl daemon-reload
fi
sudo systemctl restart "${SERVICE_NAME}"

# Laisser uvicorn démarrer
sleep 3

# ─── 5. Healthcheck ─────────────────────────────────────────
log "5/5 Healthcheck"

HEALTH=$(curl -sf http://127.0.0.1:8000/health || echo "FAILED")
echo "  ${HEALTH}"

if [[ "${HEALTH}" == "FAILED" ]]; then
  log "❌ API ne répond pas. Logs récents :"
  sudo journalctl -u "${SERVICE_NAME}" -n 30 --no-pager
  exit 1
fi

# Extraire tools_available et agents_available du JSON
TOOLS_OK=$(echo "${HEALTH}" | python3 -c "import sys,json;d=json.load(sys.stdin);print(d.get('tools_available',0))")
AGENTS_OK=$(echo "${HEALTH}" | python3 -c "import sys,json;d=json.load(sys.stdin);print(d.get('agents_available',0))" 2>/dev/null || echo "?")

log "Deploy OK — ${TOOLS_OK} outils, ${AGENTS_OK} agents disponibles"
