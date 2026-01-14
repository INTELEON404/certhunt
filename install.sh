#!/bin/bash

GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

clear

echo -e "${CYAN}${BOLD}===============================================${NC}"
echo -e "${CYAN}${BOLD}      CERTHUNT - INSTALLER                     ${NC}"
echo -e "${CYAN}${BOLD}===============================================${NC}"

echo -e "${YELLOW}[*] Checking dependencies...${NC}"
deps=(python3 pip3 wget sudo)

for d in "${deps[@]}"; do
    command -v "$d" &>/dev/null || {
        echo -e "${RED}[!] Missing dependency: $d${NC}"
        exit 1
    }
done
echo -e "${GREEN}[✓] Dependencies OK${NC}"

echo -e "${YELLOW}[*] Installing Python libraries...${NC}"
pip3 install requests urllib3 argparse --break-system-packages 2>/dev/null \
|| pip3 install requests urllib3 argparse || {
    echo -e "${RED}[!] Python library install failed${NC}"
    exit 1
}
echo -e "${GREEN}[✓] Python libraries installed${NC}"

TARGET_BIN="/usr/local/bin/certhunt"

echo -e "${YELLOW}[*] Installing certhunt...${NC}"
[ -f certhunt.py ] || {
    echo -e "${RED}[!] certhunt not found${NC}"
    exit 1
}

sudo cp certhunt "$TARGET_BIN"
sudo chmod +x "$TARGET_BIN"

echo -e "${GREEN}${BOLD}[✓] Installation complete${NC}"
echo -e "${CYAN}Run: ${BOLD}certhunt -d target.com${NC}"
