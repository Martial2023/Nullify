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

  # Skip si l'image existe déjà et pas --force
  if [[ $FORCE -eq 0 ]] && docker image inspect "${IMAGE}" >/dev/null 2>&1; then
    echo "[deploy-tools] ${IMAGE} déjà présente, skip"
    SKIPPED=$((SKIPPED + 1))
    continue
  fi

  echo "[deploy-tools] Building ${IMAGE}..."
  if docker build -t "${IMAGE}" -f "${DOCKER_DIR}/${DOCKERFILE}" "${DOCKER_DIR}"; then
    echo "[deploy-tools] ✓ ${IMAGE}"
    BUILT=$((BUILT + 1))
  else
    echo "[deploy-tools] ✗ ${IMAGE} — échec du build"
    FAILED=$((FAILED + 1))
  fi
done

echo ""
echo "[deploy-tools] Résultat: ${BUILT} buildées, ${SKIPPED} skippées, ${FAILED} échouées"

# Lister les images Nullify présentes
echo ""
echo "[deploy-tools] Images Docker Nullify disponibles :"
docker images --filter "reference=nullify-tools*" --format "  {{.Repository}}:{{.Tag}} ({{.Size}})" 2>/dev/null || true
