#!/usr/bin/env bash
# Deploy script pour le VPS Nullify — idempotent.
# Appelé par ~/scripts/deploy-api.sh après git pull.
#
# Responsabilités :
#   1. Dépendances Python à jour
#   2. Binaires de sécurité présents (nmap + httpx/subfinder/nuclei)
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
BIN_DIR="${API_DIR}/bin"

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

# ─── 2. Outils de sécurité ──────────────────────────────────
log "2/5 Outils de sécurité"
bash "${NULLIFY_ROOT}/docker/deploy-tools.sh"

# ─── 3. Override systemd (PATH) ─────────────────────────────
log "3/5 Override systemd"

OVERRIDE_DIR="/etc/systemd/system/${SERVICE_NAME}.service.d"
OVERRIDE_FILE="${OVERRIDE_DIR}/override.conf"
EXPECTED_PATH="${BIN_DIR}:${VENV_DIR}/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

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
sleep 2

# ─── 5. Healthcheck ─────────────────────────────────────────
log "5/5 Healthcheck"

HEALTH=$(curl -sf http://127.0.0.1:8000/health || echo "FAILED")
echo "  ${HEALTH}"

if [[ "${HEALTH}" == "FAILED" ]]; then
  log "❌ API ne répond pas. Logs récents :"
  sudo journalctl -u "${SERVICE_NAME}" -n 30 --no-pager
  exit 1
fi

# Extraire tools_available du JSON (sans dépendre de jq)
TOOLS_OK=$(echo "${HEALTH}" | python3 -c "import sys,json;print(json.load(sys.stdin)['tools_available'])")
if [[ "${TOOLS_OK}" != "4" ]]; then
  log "tools_available=${TOOLS_OK} (attendu 4) — vérifier bin/ et PATH"
  exit 1
fi

log "Deploy OK — ${TOOLS_OK}/4 outils disponibles"
