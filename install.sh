#!/bin/bash

GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
ORANGE='\033[38;5;214m'
NC='\033[0m'

unbuffered_sed() {
    if echo | sed -u -e "" >/dev/null 2>&1; then
        sed -nu "$@"
    elif echo | sed -l -e "" >/dev/null 2>&1; then
        sed -nl "$@"
    else
        local pad="$(printf "\n%512s" "")"
        sed -ne "s/$/\\${pad}/" "$@"
    fi
}

print_progress() {
    local bytes="$1"
    local length="$2"
    [ "$length" -gt 0 ] || return 0

    local width=50
    local percent=$(( bytes * 100 / length ))
    [ "$percent" -gt 100 ] && percent=100
    local on=$(( percent * width / 100 ))
    local off=$(( width - on ))

    local filled=$(printf "%*s" "$on" "")
    filled=${filled// /■}
    local empty=$(printf "%*s" "$off" "")
    empty=${empty// /･}

    printf "\r${ORANGE}%s%s %3d%%${NC}" "$filled" "$empty" "$percent" >&4
}

download_with_progress() {
    local url="$1"
    local output="$2"

    if [ -t 2 ]; then
        exec 4>&2
    else
        exec 4>/dev/null
    fi

    local tmp_dir=${TMPDIR:-/tmp}
    local basename="${tmp_dir}/certhunt_download_$$"
    local tracefile="${basename}.trace"

    rm -f "$tracefile"
    mkfifo "$tracefile"

    printf "\033[?25l" >&4

    trap "trap - RETURN; rm -f \"$tracefile\"; printf '\033[?25h' >&4; exec 4>&-" RETURN

    (
        curl --trace-ascii "$tracefile" -s -L -o "$output" "$url"
    ) &
    local curl_pid=$!

    unbuffered_sed \
        -e 'y/ACDEGHLNORTV/acdeghlnortv/' \
        -e '/^0000: content-length:/p' \
        -e '/^<= recv data/p' \
        "$tracefile" | \
    {
        local length=0
        local bytes=0

        while IFS=" " read -r -a line; do
            [ "${#line[@]}" -lt 2 ] && continue
            local tag="${line[0]} ${line[1]}"

            if [ "$tag" = "0000: content-length:" ]; then
                length="${line[2]}"
                length=$(echo "$length" | tr -d '\r')
                bytes=0
            elif [ "$tag" = "<= recv" ]; then
                local size="${line[3]}"
                bytes=$(( bytes + size ))
                if [ "$length" -gt 0 ]; then
                    print_progress "$bytes" "$length"
                fi
            fi
        done
    }

    wait $curl_pid
    local ret=$?
    echo "" >&4
    return $ret
}


echo -e "${CYAN}=======================================${NC}"
echo -e "${CYAN}    CERTHUNT AUTOMATED INSTALLER       ${NC}"
echo -e "${CYAN}=======================================${NC}"

echo -e "${YELLOW}[*] Installing python dependencies...${NC}"
sudo pip3 install requests urllib3 --break-system-packages 2>/dev/null || sudo pip3 install requests urllib3

echo -e "${YELLOW}[*] Downloading Certhunt from repository...${NC}"

download_with_progress "https://raw.githubusercontent.com/INTELEON404/certhunt/main/certhunt.py" "/tmp/certhunt"

if [ $? -ne 0 ]; then
    echo -e "${RED}[!] Download failed! Please check your network connection.${NC}"
    exit 1
fi

echo -e "${YELLOW}[*] Moving binary to /usr/local/bin/certhunt...${NC}"
sudo mv /tmp/certhunt /usr/local/bin/certhunt

echo -e "${YELLOW}[*] Granting executable permissions...${NC}"
sudo chmod +x /usr/local/bin/certhunt

echo -e "---------------------------------------"
echo -e "${GREEN}[✓] Installation Successful!${NC}"
echo -e "${CYAN}Usage: ${NC}certhunt -d example.com"
echo -e "---------------------------------------"
