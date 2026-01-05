# 🏹 CERTHUNT v1

### **“AUTOMATED PASSIVE DOMAIN ENUMERATION”**

**HUNTER v1** is a high-performance, multi-threaded reconnaissance tool designed for security researchers and Bug Bounty hunters. It streamlines the "Passive Reconnaissance" phase by querying multiple public APIs and databases to discover subdomains without interacting directly with the target infrastructure.

---

## 🌟 Key Features

* **12+ Passive Sources:** Aggregates data from the most reliable sources in the industry (Crt.sh, AlienVault, Wayback Machine, etc.).
* **Intelligent Deduplication:** Automatically cleans, normalizes, and removes duplicate entries from different sources.
* **Active DNS Verification:** Optional high-speed DNS resolution to identify which discovered subdomains are actually "Live."
* **Multi-threaded Engine:** Powered by `ThreadPoolExecutor` for simultaneous API querying and rapid verification.
* **Developer Friendly:** Clean Python code, modular source functions, and professional ANSI-colored CLI output.
* **Automatic Export:** Interactive prompt to save discovered targets into a structured `.txt` file.

---

## 🛠 Supported OSINT Sources

| Category | Sources Integrated |
| --- | --- |
| **Certificate Transparency** | Crt.sh, CertSpotter |
| **Search & Crawlers** | Wayback Machine, URLScan.io, Riddler.io |
| **Passive DNS/APIs** | AlienVault OTX, HackerTarget, Anubis, RapidDNS, ThreatMiner, BeVigil, SubdomainCenter |

---

## 🚀 Installation

Ensure you have **Python 3.7+** installed on your system.


### Clone the repository
```
git clone https://github.com/INTELEON404/certhunt.git
```

### Navigate to the directory
```
cd certhunt
```

### Install dependencies
```
pip install -r requirements.txt

```

*(Note: If you haven't created a requirements.txt, just run: `pip install requests urllib3`)*

---

## 💻 Usage

### Basic Enumeration

Simply find subdomains via passive APIs:

```bash
python3 hunter.py -d google.com

```

### Full Recon (Discovery + Live Validation)

Find subdomains and verify if they resolve to an IP address:

```bash
python3 hunter.py -d example.com -v

```

### Advanced Threading

Speed up the verification process for large result sets:

```bash
python3 hunter.py -d example.com -v -t 100

```

---

## ⚙️ Command Line Arguments

| Argument | Long Form | Description |
| --- | --- | --- |
| `-d` | `--domain` | **(Required)** The target domain to scan (e.g., target.com) |
| `-v` | `--verify` | Enable DNS resolution to check if subdomains are active |
| `-t` | `--threads` | Set number of concurrent threads for verification (Default: 20) |

---

## 🔄 Workflow Logic

1. **Input Normalization:** Strips protocols (http/https) and 'www' from the target.
2. **Parallel Harvesting:** Launches threads for each API source simultaneously.
3. **Data Cleaning:** Filters out out-of-scope domains and normalizes text.
4. **Verification (Optional):** Performs DNS lookups to validate the existence of the host.
5. **Reporting:** Displays a color-coded summary and offers to save the output locally.

---

## ⚖️ Disclaimer

This tool is intended for **legal** security auditing and educational purposes only. Unauthorized scanning of targets without prior consent is illegal. The developer is not responsible for any misuse or damage caused by this program.

---

### 👨‍💻 About the Author

Developed by **[INTELEON404](https://www.google.com/search?q=https://github.com/INTELEON404)**.


