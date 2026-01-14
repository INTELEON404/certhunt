#!/bin/bash

GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}=======================================${NC}"
echo -e "${CYAN}    CERTHUNT AUTOMATED INSTALLER       ${NC}"
echo -e "${CYAN}=======================================${NC}"

echo -e "${YELLOW}[*] Installing python dependencies...${NC}"
pip3 install requests urllib3 --break-system-packages 2>/dev/null || pip3 install requests urllib3

echo -e "${YELLOW}[*] Downloading Certhunt from repository...${NC}"
wget -q https://raw.githubusercontent.com/INTELEON404/certhunt/main/certhunt -O certhunt

if [ $? -ne 0 ]; then
    echo -e "${RED}[!] Download failed! Please check your network connection.${NC}"
    exit 1
fi

echo -e "${YELLOW}[*] Moving binary to /usr/bin/certhunt...${NC}"
sudo mv certhunt /usr/local/bin/

echo -e "${YELLOW}[*] Granting executable permissions...${NC}"
sudo chmod +x /usr/bin/certhunt

echo -e "---------------------------------------"
echo -e "${GREEN}[✓] Installation Successful!${NC}"
echo -e "${CYAN}Usage: ${NC}certhunt -d example.com"
echo -e "---------------------------------------"
