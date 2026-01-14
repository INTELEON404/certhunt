<div align="center">
  <img src="https://github.com/INTELEON404/Template/blob/main/certhunt.png" width="700" alt="TEMPLATE-PLUS Logo"/>
  <br><br>
</div>

# 🏹 CERTHUNT v1.3

### **“Automated Passive Domain Enumeration & DNS Validation”**

**CERTHUNT v1** (also known as **HUNTER**) is a high-performance, multi-threaded reconnaissance tool designed for security researchers and Bug Bounty hunters. It streamlines the "Passive Reconnaissance" phase by querying multiple public APIs and databases to discover subdomains without interacting directly with the target infrastructure.

---

## 🌟 Key Features

* **12+ Passive Sources:** Aggregates data from reliable sources like Crt.sh, AlienVault, Wayback Machine, and more.
* **Intelligent Deduplication:** Automatically cleans, normalizes, and removes duplicate entries from different sources.
* **Active DNS Verification:** Optional high-speed DNS resolution to identify which discovered subdomains are actually "Live."
* **Multi-threaded Engine:** Powered by `ThreadPoolExecutor` for simultaneous API querying and rapid verification.
* **Global Access:** Easily installable as a system-wide command for seamless usage.
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

Choose one of the two methods below. The **Automated Install** is recommended for quick setup.

### 1. Quick Automated Install (Recommended)

Run this command in your terminal to install the tool and its dependencies automatically:

```bash
wget -q https://raw.githubusercontent.com/INTELEON404/certhunt/main/install.sh -O install.sh && chmod +x install.sh && ./install.sh
```
```
rm install.sh
```

### 2. Manual Installation

If you prefer to set it up manually:

#### Clone the repository
```
git clone https://github.com/INTELEON404/certhunt.git
cd certhunt
```
#### Install dependencies
```
pip install requests urllib3 --break-system-packages
```
#### Move to /usr/bin for global access
```
chmod +x certhunt
sudo mv certhunt /usr/local/bin/

```

---

## 💻 Usage

After installation, you can run the tool from any directory using the `certhunt` command.

### Basic Enumeration

To find subdomains via passive APIs:

```bash
certhunt -d google.com

```

### Full Recon (Discovery + Live Validation)

Find subdomains and verify if they resolve to an active IP address:

```bash
certhunt -d example.com -v

```

### Advanced Threading

Speed up the verification process for large result sets by increasing the thread count:

```bash
certhunt -d example.com -v -t 100

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

1. **Input Normalization:** Strips protocols (http/https) and 'www' to ensure a clean target domain.
2. **Parallel Harvesting:** Launches threads for each API source simultaneously for maximum speed.
3. **Data Cleaning:** Filters out out-of-scope domains and normalizes the text.
4. **Verification (Optional):** Performs DNS lookups to validate the existence of the discovered hosts.
5. **Reporting:** Displays a color-coded summary and offers to save the output locally as a `.txt` file.

---

## ⚖️ Disclaimer

This tool is intended for **legal** security auditing and educational purposes only. Unauthorized scanning of targets without prior consent is illegal. The developer is not responsible for any misuse or damage caused by this program.

---

### 👨‍💻 About the Author

Developed by **[INTELEON404](https://www.google.com/search?q=https://github.com/INTELEON404)**.

Contributions, issues, and feature requests are welcome!
