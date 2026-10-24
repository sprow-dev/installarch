#!/usr/bin/env bash

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}Initializing Sprow Install Arch...${NC}"

ARCHIVE_FILE="installscripts.tar.gz"
TARGET_DIR=".SIATEMP_DONOTDELETE"

echo -e "${BLUE}Downloading runtime files...${NC}"
curl -fsSL -o "$ARCHIVE_FILE" "https://raw.githubusercontent.com/sprow-dev/installarch/main/$ARCHIVE_FILE"

if [ -f "$ARCHIVE_FILE" ]; then
    echo -e "${BLUE}Extracting runtime files...${NC}"
    mkdir -p "$TARGET_DIR"
    tar -xzf "$ARCHIVE_FILE" -C "$TARGET_DIR"
    rm "$ARCHIVE_FILE"
else
    echo "${RED}FATAL: RUNTIMEERROR: Downloaded artifact not found in runtime dir."
    exit 1
fi

cd "${TARGET_DIR}"

echo -e "${BLUE}Building venv${NC}"
pacman -Sy --noconfirm uv python3 # assumes correct iso which allows root on script runtime automatically
uv venv
uv pip install rich

# Run the main application
echo -e "${GREEN}Sprow Install Arch ready. Please standby for takeoff...${NC}"
uv run main.py # error handling will be integrated into script
trap 'rm -rf "$TARGET_DIR"' EXIT
