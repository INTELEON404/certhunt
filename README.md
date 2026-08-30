<div align="center">
  <img src="https://github.com/INTELEON404/Template/blob/main/certhunt.png" width="700" alt="CERTHUNT Logo"/>
  <br><br>
</div>

# CERTHUNT v1.4

**Passive Subdomain Reconnaissance & Validation Tool**

CERTHUNT is a multi-threaded reconnaissance utility for security researchers and penetration testers. It aggregates subdomain data from 20 passive OSINT sources, validates discovered hosts via DNS resolution, and optionally probes live services using HTTPX.

---

## Features

- **20 Passive Sources:** Certificate transparency logs, search engines, crawlers, and passive DNS APIs.
- **RFC 1123 Validation:** Strict hostname normalization with domain boundary enforcement.
- **DNS Verification:** Concurrent resolution to confirm live hosts.
- **HTTPX Integration:** Optional HTTP/HTTPS probing with status code reporting.
- **Controlled Concurrency:** Bounded thread pools to prevent resource exhaustion.
- **Dual Output Modes:** Interactive TTY with color-coded output, or clean stdout for piping.
- **Graceful Degradation:** Per-source error isolation ensures one failed API does not abort the scan.

---

## Sources

| Category | Sources |
| --- | --- |
| Certificate Transparency | Crt.sh, CertSpotter, Crt.name |
| Search & Archives | Wayback Machine, CommonCrawl, URLScan.io |
| Passive DNS / APIs | AbuseIPDB, AlienVault OTX, Anubis, BeVigil, BufferOver, FullHunt, HackerTarget, Omnisint, RapidDNS, SubdomainCenter, Synapsint, VirusTotal |
| Web Intelligence | Netcraft, SiteDossier |

---

## Installation

### Automated

```bash
wget -q https://raw.githubusercontent.com/INTELEON404/certhunt/main/install.sh -O install.sh
chmod +x install.sh && ./install.sh
rm install.sh
```

### Manual

```bash
git clone https://github.com/INTELEON404/certhunt.git
cd certhunt
pip install requests
chmod +x certhunt.py
```

### Optional: HTTPX

Required for `--http` and `--status` functionality:

```bash
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
```

Verify installation:

```bash
python3 -c "import requests; print('OK')"
which httpx
```

---

## Usage

### Passive Enumeration

```bash
python3 certhunt.py -d example.com
```

### With DNS Verification

```bash
python3 certhunt.py -d example.com --verify
```

### With HTTPX Filtering

```bash
python3 certhunt.py -d example.com --http
```

### Full Workflow

```bash
python3 certhunt.py -d example.com --verify --http --status
```

### Non-Interactive (Piping)

```bash
python3 certhunt.py -d example.com | sort > subdomains.txt
```

---

## Arguments

| Short | Long | Description |
| --- | --- | --- |
| `-d` | `--domain` | Target domain (required) |
| `-v` | `--verify` | Verify live hosts via DNS resolution |
| `-t` | `--threads` | Thread count for HTTPX (default: 60, range: 1-1000) |
| | `--http` | Enable HTTP/HTTPS probing via httpx |
| | `--status` | Display HTTP status codes (requires `--http`) |

---

## Workflow

1. **Normalization** — Strips protocols, paths, wildcards, and trailing dots. Validates against RFC 1123.
2. **Harvesting** — Queries all 20 sources concurrently (max 20 workers).
3. **Deduplication** — Set-based normalization with strict domain boundary checks.
4. **Verification** — Optional DNS resolution (max 100 workers).
5. **HTTP Probing** — Optional httpx execution with dynamic timeout scaling (60–300s).
6. **Output** — Interactive export prompt or clean stdout for scripts.

---

## Performance

| Phase | Workers | Timeout |
| --- | --- | --- |
| Passive Sources | 20 | 35s per request |
| DNS Verification | 100 | System default |
| HTTPX Probing | User-defined (`-t`) | 60–300s (dynamic) |

Typical memory usage: ~5–10 MB for 10,000 subdomains.  
Typical runtime: 30–120 seconds depending on API availability.

---

## Error Handling

Source failures are categorized without terminating the scan:

| Category | Cause |
| --- | --- |
| TIMEOUT | Request exceeded 35 seconds |
| CONNECT_ERROR | Network-level connection failure |
| HTTP_ERROR | 4xx client error |
| SERVER_ERROR | 5xx server error |
| INVALID_JSON | Response received but JSON parsing failed |

---

## Security

- Subprocess calls use argument arrays; `shell=True` is never used.
- All hostnames are normalized and validated before API or subprocess interaction.
- File operations use UTF-8 encoding with proper exception handling.

---

## Requirements

- Python 3.6+
- `requests` library
- Internet connectivity
- `httpx` (optional, for `--http` / `--status`)

---

## Limitations

- Passive sources may rate-limit or require external API availability.
- DNS verification requires network connectivity.
- HTTPX is optional; without it, HTTP filtering is unavailable.
- No authentication support for premium APIs.
- Results are held in memory only; no database persistence.

---

## Disclaimer

This tool is intended for authorized security research and educational purposes only. Use only on systems you own or have explicit permission to test. The author assumes no liability for misuse.

---

## License & Contributions

Developed by [INTELEON404](https://github.com/INTELEON404).

