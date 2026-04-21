#!/usr/bin/env bash
# Build toutes les images Docker d'outils de sécurité.
#
# Usage :
#   bash docker/deploy-tools.sh            # build les images manquantes
#   bash docker/deploy-tools.sh --force    # rebuild toutes les images
#   bash docker/deploy-tools.sh --only network web  # build seulement certaines

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DOCKER_DIR="${REPO_ROOT}/docker"

FORCE=0
ONLY=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --force) FORCE=1; shift ;;
    --only) shift; while [[ $# -gt 0 && ! "$1" =~ ^-- ]]; do ONLY+=("$1"); shift; done ;;
    *) shift ;;
  esac
done

# Toutes les images disponibles
declare -A IMAGES=(
  ["tools"]="Dockerfile.tools"
  ["network"]="Dockerfile.tools-network"
  ["web"]="Dockerfile.tools-web"
  ["auth"]="Dockerfile.tools-auth"
  ["binary"]="Dockerfile.tools-binary"
  ["cloud"]="Dockerfile.tools-cloud"
  ["forensics"]="Dockerfile.tools-forensics"
  ["osint"]="Dockerfile.tools-osint"
  ["browser"]="Dockerfile.tools-browser"
)

BUILT=0
SKIPPED=0
FAILED=0

for key in "${!IMAGES[@]}"; do
  # Filtre --only
  if [[ ${#ONLY[@]} -gt 0 ]]; then
    match=0
    for o in "${ONLY[@]}"; do
      [[ "$key" == "$o" ]] && match=1
    done
    [[ $match -eq 0 ]] && continue
  fi

  DOCKERFILE="${IMAGES[$key]}"
  if [[ "$key" == "tools" ]]; then
    IMAGE="nullify-tools:latest"
  else
    IMAGE="nullify-tools-${key}:latest"
  fi

  if [[ ! -f "${DOCKER_DIR}/${DOCKERFILE}" ]]; then
    echo "[deploy-tools] ⚠ ${DOCKERFILE} non trouvé, skip"
    SKIPPED=$((SKIPPED + 1))
    continue
  fi

  # Skip si l'image existe déjà, Dockerfile n'a pas changé, et pas --force
  HASH_DIR="/tmp/nullify-docker-hashes"
  mkdir -p "${HASH_DIR}"
  CURRENT_HASH=$(sha256sum "${DOCKER_DIR}/${DOCKERFILE}" | cut -d' ' -f1)
  STORED_HASH=""
  [[ -f "${HASH_DIR}/${DOCKERFILE}.sha256" ]] && STORED_HASH=$(cat "${HASH_DIR}/${DOCKERFILE}.sha256")

  if [[ $FORCE -eq 0 ]] && docker image inspect "${IMAGE}" >/dev/null 2>&1 && [[ "${CURRENT_HASH}" == "${STORED_HASH}" ]]; then
    echo "[deploy-tools] ${IMAGE} déjà à jour, skip"
    SKIPPED=$((SKIPPED + 1))
    continue
  fi

  echo "[deploy-tools] Building ${IMAGE} ($(date '+%H:%M:%S'))..."
  BUILD_LOG="/tmp/nullify-build-${key}.log"
  if docker build --progress=plain -t "${IMAGE}" -f "${DOCKER_DIR}/${DOCKERFILE}" "${DOCKER_DIR}" > "${BUILD_LOG}" 2>&1; then
    echo "[deploy-tools] ✓ ${IMAGE} ($(date '+%H:%M:%S'))"
    echo "${CURRENT_HASH}" > "${HASH_DIR}/${DOCKERFILE}.sha256"
    BUILT=$((BUILT + 1))
  else
    echo "[deploy-tools] ✗ ${IMAGE} — échec du build. Dernières lignes :"
    tail -20 "${BUILD_LOG}" 2>/dev/null || true
    FAILED=$((FAILED + 1))
  fi
done

echo ""
echo "[deploy-tools] Résultat: ${BUILT} buildées, ${SKIPPED} skippées, ${FAILED} échouées"

# Lister les images Nullify présentes
echo ""
echo "[deploy-tools] Images Docker Nullify disponibles :"
docker images --filter "reference=nullify-tools*" --format "  {{.Repository}}:{{.Tag}} ({{.Size}})" 2>/dev/null || true

# Smoke test: verify key binaries exist in each image
echo ""
echo "[deploy-tools] Vérification des binaires clés :"
declare -A SMOKE_TESTS=(
  ["nullify-tools:latest"]="nmap nuclei httpx subfinder"
  ["nullify-tools-network:latest"]="nmap masscan amass fierce"
  ["nullify-tools-web:latest"]="gobuster ffuf katana nikto sqlmap whatweb"
  ["nullify-tools-auth:latest"]="hydra john hashid"
  ["nullify-tools-binary:latest"]="gdb binwalk checksec strings"
)

for image in "${!SMOKE_TESTS[@]}"; do
  if ! docker image inspect "${image}" >/dev/null 2>&1; then
    continue
  fi
  binaries="${SMOKE_TESTS[$image]}"
  echo "  ${image}:"
  for bin in ${binaries}; do
    if docker run --rm "${image}" which "${bin}" >/dev/null 2>&1; then
      echo "    ✓ ${bin}"
    else
      echo "    ✗ ${bin} NOT FOUND"
    fi
  done
done
