#!/usr/bin/env bash
# Build docker/Dockerfile.tools et extrait les binaires dans apps/api/bin/
# À exécuter sur le VPS après chaque deploy si apps/api/bin est vide.
#
# Usage :
#   bash docker/deploy-tools.sh
#   bash docker/deploy-tools.sh --force   # rebuild même si les binaires existent

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BIN_DIR="${REPO_ROOT}/apps/api/bin"
IMAGE_NAME="nullify-tools:latest"
# Binaires Go statiques extractibles depuis l'image Alpine (glibc-compatibles)
GO_TOOLS=(httpx subfinder nuclei)
# nmap Alpine = musl, incompatible glibc → installé via apt sur l'host

FORCE=0
[[ "${1:-}" == "--force" ]] && FORCE=1

# 1. Installer nmap via apt si absent (binaire glibc natif host)
if ! command -v nmap >/dev/null 2>&1; then
  echo "[deploy-tools] Installation de nmap via apt..."
  sudo apt-get update -qq
  sudo apt-get install -y nmap
fi

# 2. Skip l'extraction si les binaires Go sont déjà présents et --force absent
if [[ $FORCE -eq 0 ]]; then
  all_present=1
  for t in "${GO_TOOLS[@]}"; do
    [[ -x "${BIN_DIR}/${t}" ]] || { all_present=0; break; }
  done
  if [[ $all_present -eq 1 ]]; then
    echo "[deploy-tools] Binaires Go déjà présents dans ${BIN_DIR}, skip."
    echo "[deploy-tools] Utilise --force pour rebuild."
    exit 0
  fi
fi

echo "[deploy-tools] Build image ${IMAGE_NAME}..."
docker build -t "${IMAGE_NAME}" -f "${REPO_ROOT}/docker/Dockerfile.tools" "${REPO_ROOT}/docker"

echo "[deploy-tools] Extraction des binaires Go vers ${BIN_DIR}..."
mkdir -p "${BIN_DIR}"
CID=$(docker create "${IMAGE_NAME}")
trap 'docker rm -f "${CID}" >/dev/null' EXIT

for t in "${GO_TOOLS[@]}"; do
  docker cp "${CID}:/usr/local/bin/${t}" "${BIN_DIR}/${t}"
  chmod +x "${BIN_DIR}/${t}"
  echo "  + ${t}"
done

echo "[deploy-tools] Verification :"
command -v nmap && nmap --version | head -1
for t in "${GO_TOOLS[@]}"; do
  "${BIN_DIR}/${t}" -version 2>&1 | head -1 || echo "  ! ${t} semble cassé"
done

echo ""
echo "[deploy-tools] OK. Redémarre FastAPI : sudo systemctl restart nullify-api"
