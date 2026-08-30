#!/usr/bin/env python3
import re
import argparse
import requests
import sys
import socket
import time
import shutil
import itertools
import threading
import subprocess
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

# =============================================================================
# CONFIGURATION & CONSTANTS
# =============================================================================

VERSION = "HUNTER v2.1 FINAL"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
}
TIMEOUT = 35
HTTPX_TIMEOUT = 300
MAX_THREADS = 1000
MIN_THREADS = 1

# =============================================================================
# COLORS & UI
# =============================================================================

class Colors:
    MINT     = '\033[38;5;121m'
    SKY      = '\033[38;5;117m'
    GOLD     = '\033[38;5;222m'
    CORAL    = '\033[38;5;210m'
    LAVENDER = '\033[38;5;183m'
    SILVER   = '\033[38;5;249m'
    SLATE    = '\033[38;5;241m'
    BOLD     = '\033[1m'
    ENDC     = '\033[0m'

# Global state
stop_animation = None  # Will be threading.Event
session = None  # Will be requests.Session

def init_globals():
    """Initialize global objects."""
    global stop_animation, session
    stop_animation = threading.Event()
    session = requests.Session()
    session.headers.update(HEADERS)
    # Suppress SSL warnings only for this session
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def status_log(msg, color=Colors.SILVER):
    """Log status message if interactive terminal."""
    if sys.stdout.isatty():
        print(f"{color}{msg}{Colors.ENDC}", file=sys.stderr)

def loading_animation():
    """Spinner animation for interactive mode."""
    spinner = itertools.cycle(['⠏', '⠛', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠍'])
    while not stop_animation.is_set():
        char = next(spinner)
        sys.stderr.write(f"\r {Colors.MINT}{char}{Colors.ENDC} {Colors.GOLD}EXTRACTING DEEP DATA...{Colors.ENDC}")
        sys.stderr.flush()
        time.sleep(0.1)
    sys.stderr.write("\r" + " " * 50 + "\r")

def get_banner():
    """Display banner if interactive."""
    if sys.stdout.isatty():
        columns = shutil.get_terminal_size().columns
        width = max(columns, 70)
        art = [
            "░█▀▀░█▀▀░█▀▄░▀█▀░█░█░█░█░█▀█░▀█▀",
            "░█░░░█▀▀░█▀▄░░█░░█▀█░█░█░█░█░░█░",
            "░▀▀▀░▀▀▀░▀░▀░░▀░░▀░▀░▀▀▀░▀░▀░░▀░"
        ]
        print(f"{Colors.SKY}{Colors.BOLD}")
        for line in art:
            print(line.center(width))
        info = f"DEVELOPED BY INTELEON404 | VERSION {VERSION}"
        tagline = "ADVANCED SUBDOMAIN RECONNAISSANCE"
        print(f"\n{Colors.LAVENDER}{info.center(width)}{Colors.ENDC}")
        print(f"{Colors.SLATE}{tagline.center(width)}{Colors.ENDC}\n")

# =============================================================================
# TARGET NORMALIZATION
# =============================================================================

def clean_target(domain):
    """Parse and normalize target domain."""
    domain = re.sub(r'^https?://', '', domain.lower().strip())
    domain = domain.replace('www.', '', 1)
    domain = re.sub(r'[/?#].*$', '', domain)
    domain = domain.rstrip('.')
    return domain

def normalize_hostname(hostname):
    """Normalize hostname for consistent processing."""
    hostname = hostname.lower().strip()
    if hostname.endswith('.'):
        hostname = hostname[:-1]
    if hostname.startswith('*.'):
        hostname = hostname[2:]
    return hostname

def is_valid_hostname(hostname):
    """RFC 1123 hostname validation."""
    if not hostname or len(hostname) > 253:
        return False
    if not re.match(r'^[a-z0-9]([a-z0-9-\.]*[a-z0-9])?$', hostname):
        return False
    labels = hostname.split('.')
    for label in labels:
        if not label or len(label) > 63:
            return False
        if not re.match(r'^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$', label):
            return False
    return True

def belongs_to_domain(hostname, domain):
    """Strict domain boundary check."""
    hostname = normalize_hostname(hostname)
    domain = normalize_hostname(domain)
    
    if not is_valid_hostname(hostname) or not is_valid_hostname(domain):
        return False
    
    # Apex domain not included as subdomain of itself
    if hostname == domain:
        return False
    
    # Must end with domain boundary
    if hostname.endswith('.' + domain):
        return True
    
    return False

def extract_all(text, domain):
    """Extract valid subdomains from text."""
    pattern = r'(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?'
    matches = re.findall(pattern, str(text).lower())
    valid = set()
    for m in matches:
        if belongs_to_domain(m.strip(), domain):
            valid.add(m.strip())
    return valid

# =============================================================================
# HTTP REQUEST HELPER
# =============================================================================

class SourceResult:
    """Container for source execution results."""
    def __init__(self):
        self.found = set()
        self.status = "OK"  # OK, TIMEOUT, CONNECT_ERROR, HTTP_ERROR, INVALID_JSON, EMPTY

def request_api(url, is_json=True, timeout=TIMEOUT):
    """Make API request with detailed error handling."""
    result = SourceResult()
    try:
        resp = session.get(url, timeout=timeout, verify=False)
        if resp.status_code == 200:
            if is_json:
                try:
                    return resp.json()
                except (json.JSONDecodeError, ValueError):
                    result.status = "INVALID_JSON"
                    return None
            else:
                text = resp.text.strip()
                return text if text else None
        elif resp.status_code >= 500:
            result.status = "SERVER_ERROR"
        elif resp.status_code >= 400:
            result.status = "HTTP_ERROR"
        return None
    except requests.exceptions.Timeout:
        result.status = "TIMEOUT"
        return None
    except requests.exceptions.ConnectionError:
        result.status = "CONNECT_ERROR"
        return None
    except requests.exceptions.HTTPError:
        result.status = "HTTP_ERROR"
        return None
    except requests.exceptions.RequestException:
        result.status = "REQUEST_ERROR"
        return None
    except Exception:
        result.status = "UNKNOWN_ERROR"
        return None

# =============================================================================
# PASSIVE SOURCE ENGINES
# =============================================================================

def source_abuseipdb(domain):
    """AbuseIPDB WHOIS."""
    res = request_api(f"https://www.abuseipdb.com/whois/{domain}", is_json=False)
    return extract_all(res, domain) if res else set()

def source_alienvault(domain):
    """AlienVault OTX passive DNS."""
    data = request_api(f"https://otx.alienvault.com/api/v1/indicators/domain/{domain}/passive_dns")
    subs = set()
    if data and isinstance(data, dict):
        for entry in data.get("passive_dns", []):
            if isinstance(entry, dict):
                hostname = entry.get("hostname", "").strip()
                if hostname and belongs_to_domain(hostname, domain):
                    subs.add(normalize_hostname(hostname))
    return subs

def source_anubis(domain):
    """Jldc.me Anubis."""
    data = request_api(f"https://jldc.me/anubis/subdomains/{domain}")
    subs = set()
    if data and isinstance(data, list):
        for s in data:
            if isinstance(s, str) and belongs_to_domain(s, domain):
                subs.add(normalize_hostname(s))
    return subs

def source_bevigil(domain):
    """BeVigil OSINT."""
    data = request_api(f"https://osint.bevigil.com/api/{domain}/subdomains/")
    subs = set()
    if data and isinstance(data, dict):
        for s in data.get("subdomains", []):
            if isinstance(s, str) and belongs_to_domain(s, domain):
                subs.add(normalize_hostname(s))
    return subs

def source_bufferover(domain):
    """BufferOver DNS."""
    data = request_api(f"https://dns.bufferover.run/dns?q=.{domain}")
    subs = set()
    if data and isinstance(data, dict):
        for entry in data.get("FDNS_A", []):
            if isinstance(entry, str) and "," in entry:
                try:
                    hostname = entry.split(",")[1].strip()
                    if hostname and belongs_to_domain(hostname, domain):
                        subs.add(normalize_hostname(hostname))
                except (IndexError, ValueError):
                    pass
    return subs

def source_certspotter(domain):
    """Certspotter API."""
    data = request_api(f"https://api.certspotter.com/v1/issuances?domain={domain}&include_subdomains=true&expand=dns_names")
    subs = set()
    if data and isinstance(data, list):
        for entry in data:
            if isinstance(entry, dict):
                for name in entry.get("dns_names", []):
                    if isinstance(name, str) and belongs_to_domain(name, domain):
                        subs.add(normalize_hostname(name))
    return subs

def source_commoncrawl(domain):
    """Common Crawl API."""
    url = f"http://index.commoncrawl.org/CC-MAIN-2023-50-index?url=*.{domain}/*&output=json"
    res = request_api(url, is_json=False)
    return extract_all(res, domain) if res else set()

def source_crtsh(domain):
    """Crt.sh Certificate Transparency."""
    data = request_api(f"https://crt.sh/?q=%.{domain}&output=json")
    subs = set()
    if data and isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                for name in item.get("name_value", "").split("\n"):
                    if name.strip() and belongs_to_domain(name, domain):
                        subs.add(normalize_hostname(name))
    return subs

def source_crtname(domain):
    """Crt.name Certificate Transparency."""
    try:
        data = request_api(f"https://crt.name/v1/search?apex={domain}")
        subs = set()
        if data and isinstance(data, dict):
            subdomains = data.get("subdomains", [])
            if isinstance(subdomains, list):
                for entry in subdomains:
                    if isinstance(entry, str) and belongs_to_domain(entry, domain):
                        subs.add(normalize_hostname(entry))
        return subs
    except Exception:
        return set()

def source_fullhunt(domain):
    """FullHunt API."""
    data = request_api(f"https://fullhunt.io/api/v1/domain/{domain}/subdomains")
    subs = set()
    if data and isinstance(data, dict):
        for s in data.get("hosts", []):
            if isinstance(s, str) and belongs_to_domain(s, domain):
                subs.add(normalize_hostname(s))
    return subs

def source_hackertarget(domain):
    """HackerTarget API."""
    res = request_api(f"https://api.hackertarget.com/hostsearch/?q={domain}", is_json=False)
    return extract_all(res, domain) if res else set()

def source_netcraft(domain):
    """Netcraft SearchDNS."""
    res = request_api(f"https://searchdns.netcraft.com/?restriction=site+ends+with&host={domain}", is_json=False)
    return extract_all(res, domain) if res else set()

def source_omnisint(domain):
    """Omnisint Sonar."""
    data = request_api(f"https://sonar.omnisint.io/all/{domain}")
    subs = set()
    if data and isinstance(data, list):
        for s in data:
            if isinstance(s, str) and belongs_to_domain(s, domain):
                subs.add(normalize_hostname(s))
    return subs

def source_rapiddns(domain):
    """RapidDNS."""
    res = request_api(f"https://rapiddns.io/s/{domain}?full=1&down=1", is_json=False)
    return extract_all(res, domain) if res else set()

def source_sitedossier(domain):
    """Site Dossier."""
    res = request_api(f"http://www.sitedossier.com/parentdomain/{domain}", is_json=False)
    return extract_all(res, domain) if res else set()

def source_subdomaincenter(domain):
    """Subdomain Center."""
    data = request_api(f"https://api.subdomain.center/?domain={domain}")
    subs = set()
    if data and isinstance(data, list):
        for s in data:
            if isinstance(s, str) and belongs_to_domain(s, domain):
                subs.add(normalize_hostname(s))
    return subs

def source_synapsint(domain):
    """Synapsint."""
    data = request_api(f"https://synapsint.com/report.php?domain={domain}", is_json=False)
    return extract_all(data, domain) if data else set()

def source_urlscan(domain):
    """urlscan.io."""
    data = request_api(f"https://urlscan.io/api/v1/search/?q=domain:{domain}")
    subs = set()
    if data and isinstance(data, dict) and "results" in data:
        for item in data["results"]:
            if isinstance(item, dict):
                sub = item.get("page", {}).get("domain", "").strip()
                if sub and belongs_to_domain(sub, domain):
                    subs.add(normalize_hostname(sub))
    return subs

def source_virustotal(domain):
    """VirusTotal."""
    data = request_api(f"https://www.virustotal.com/ui/domains/{domain}/subdomains?limit=40")
    subs = set()
    if data and isinstance(data, dict):
        for entry in data.get("data", []):
            if isinstance(entry, dict):
                sub = entry.get("id", "").strip()
                if sub and belongs_to_domain(sub, domain):
                    subs.add(normalize_hostname(sub))
    return subs

def source_wayback(domain):
    """Wayback Machine CDX."""
    url = f"https://web.archive.org/cdx/search/cdx?url=*.{domain}/*&output=json&collapse=urlkey&fl=original"
    res = request_api(url, is_json=False)
    return extract_all(res, domain) if res else set()

# =============================================================================
# DNS VERIFICATION
# =============================================================================

def dns_resolver(domain):
    """Resolve hostname to check if live."""
    try:
        socket.gethostbyname(domain)
        return True
    except (socket.gaierror, OSError, socket.error):
        return False

# =============================================================================
# HTTPX INTEGRATION
# =============================================================================

def check_httpx_available():
    """Check if ProjectDiscovery httpx is in PATH."""
    return shutil.which("httpx") is not None

def run_httpx(hostnames, threads=60):
    """Execute httpx on discovered hosts. Returns dict of {url: status_code}."""
    if not hostnames:
        return {}
    
    try:
        # Input: normalized hostnames (let httpx probe http + https)
        input_data = "\n".join(hostnames)
        
        # Build command safely
        cmd = ['httpx', '-silent', '-json', '-threads', str(threads)]
        
        # Subprocess timeout: scale with input size
        timeout = min(HTTPX_TIMEOUT, max(60, len(hostnames) // 10))
        
        result = subprocess.run(
            cmd,
            input=input_data.encode(),
            capture_output=True,
            timeout=timeout,
            text=False
        )
        
        if result.returncode != 0:
            return None
        
        # Parse JSON/JSONL
        results = {}
        output_text = result.stdout.decode('utf-8', errors='ignore')
        
        for line in output_text.split('\n'):
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
                url = entry.get('url', '').strip()
                status = entry.get('status_code', 0)
                if url:
                    results[url] = status
            except json.JSONDecodeError:
                continue
        
        return results if results else {}
    except subprocess.TimeoutExpired:
        return None
    except FileNotFoundError:
        return None
    except Exception:
        return None

# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """Main orchestration."""
    init_globals()
    
    parser = argparse.ArgumentParser(
        prog='certhunt.py',
        description='CERTHUNT — Passive subdomain reconnaissance',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 certhunt.py -d example.com
  python3 certhunt.py -d example.com --verify
  python3 certhunt.py -d example.com --http
  python3 certhunt.py -d example.com --http --status
  python3 certhunt.py -d example.com --verify --http --status
        """
    )
    
    parser.add_argument("-d", "--domain", required=True, help="Target domain")
    parser.add_argument("-v", "--verify", action="store_true", help="Verify live via DNS")
    parser.add_argument("-t", "--threads", type=int, default=60, help="Thread count (1-1000)")
    parser.add_argument("--http", action="store_true", help="HTTP/HTTPS filtering")
    parser.add_argument("--status", action="store_true", help="Display HTTP status (requires --http)")
    
    args = parser.parse_args()
    
    # Validate domain
    target = clean_target(args.domain)
    if not target or not is_valid_hostname(target):
        print(f"{Colors.CORAL}[!] Invalid domain{Colors.ENDC}", file=sys.stderr)
        sys.exit(1)
    
    # Validate threads
    if args.threads < MIN_THREADS or args.threads > MAX_THREADS:
        print(f"{Colors.CORAL}[!] Invalid thread count (1-1000){Colors.ENDC}", file=sys.stderr)
        sys.exit(1)
    
    # Validate --status without --http
    if args.status and not args.http:
        print(f"{Colors.CORAL}[!] --status requires --http{Colors.ENDC}", file=sys.stderr)
        sys.exit(1)
    
    get_banner()
    
    status_log(f"[*] TARGETING : {target.upper()}", Colors.SKY)
    
    # Define all sources
    engines = [
        source_abuseipdb, source_alienvault, source_anubis, source_bevigil,
        source_bufferover, source_certspotter, source_commoncrawl, source_crtsh,
        source_crtname, source_fullhunt, source_hackertarget, source_netcraft,
        source_omnisint, source_rapiddns, source_sitedossier, source_subdomaincenter,
        source_synapsint, source_urlscan, source_virustotal, source_wayback
    ]
    
    status_log(f"[*] SOURCES   : {len(engines)} PASSIVE ENGINES ACTIVATED", Colors.GOLD)
    status_log(f"{Colors.SLATE}{'-' * 60}{Colors.ENDC}")
    
    discovered = set()
    results_map = {}
    
    # Spinner thread
    anim_thread = None
    if sys.stdout.isatty():
        anim_thread = threading.Thread(target=loading_animation, daemon=True)
        anim_thread.start()
    
    try:
        # Execute sources concurrently
        with ThreadPoolExecutor(max_workers=min(len(engines), 20)) as executor:
            task_map = {
                executor.submit(eng, target): eng.__name__.replace('source_', '').upper()
                for eng in engines
            }
            for task in as_completed(task_map):
                name = task_map[task]
                try:
                    found = task.result()
                    results_map[name] = found if found else set()
                    if found:
                        discovered.update(found)
                except Exception:
                    results_map[name] = set()
    finally:
        stop_animation.set()
        if anim_thread:
            anim_thread.join(timeout=1)
    
    # Display source results
    for name in sorted(results_map.keys()):
        count = len(results_map[name])
        if count > 0:
            status_log(f" {Colors.MINT}[✓]{Colors.ENDC} {name:<18} : {Colors.BOLD}{count}{Colors.ENDC} FOUND", Colors.SILVER)
        else:
            status_log(f" {Colors.CORAL}[✗]{Colors.ENDC} {name:<18} : 0 FOUND", Colors.SLATE)
    
    # Normalize and deduplicate
    final_list = {normalize_hostname(s) for s in discovered if belongs_to_domain(s, target)}
    final_list = sorted(list(final_list))
    
    status_log(f"{Colors.SLATE}{'-' * 60}{Colors.ENDC}")
    status_log(f" {Colors.LAVENDER}[★] TOTAL UNIQUE DISCOVERED: {len(final_list)}{Colors.ENDC}", Colors.BOLD)
    
    # DNS Verification
    if args.verify and final_list:
        status_log(f" [*] VERIFYING LIVE STATUS...", Colors.GOLD)
        live = []
        with ThreadPoolExecutor(max_workers=min(args.threads, 100)) as v_exec:
            v_tasks = {v_exec.submit(dns_resolver, s): s for s in final_list}
            for vt in as_completed(v_tasks):
                if vt.result():
                    live.append(v_tasks[vt])
        final_list = sorted(live)
        status_log(f" {Colors.MINT}[✓] DNS LIVE HOSTS: {len(final_list)}{Colors.ENDC}", Colors.BOLD)
    
    # HTTPX Filtering
    httpx_results = {}
    if args.http:
        if not check_httpx_available():
            status_log(f" {Colors.CORAL}[!] httpx not in PATH{Colors.ENDC}", Colors.GOLD)
        elif final_list:
            status_log(f" [*] FILTERING LIVE HOSTS WITH HTTPX...", Colors.GOLD)
            httpx_results = run_httpx(final_list, args.threads)
            if httpx_results is None:
                status_log(f" {Colors.CORAL}[!] HTTPX FAILED{Colors.ENDC}", Colors.GOLD)
            elif httpx_results:
                status_log(f" {Colors.MINT}[✓] HTTPX LIVE HOSTS: {len(httpx_results)}{Colors.ENDC}", Colors.BOLD)
                final_list = sorted(list(httpx_results.keys()))
            else:
                status_log(f" {Colors.CORAL}[✗] HTTPX: 0 LIVE HOSTS{Colors.ENDC}", Colors.SLATE)
                final_list = []
    
    # Output
    if not sys.stdout.isatty():
        # Pipe mode: clean output only
        for item in final_list:
            print(item)
    else:
        # Interactive mode
        if final_list:
            print(f"\n{Colors.SKY}{Colors.BOLD}{'='*25} RESULTS {'='*25}{Colors.ENDC}")
            for url_or_host in final_list:
                if args.http and args.status and httpx_results:
                    status = httpx_results.get(url_or_host, 0)
                    print(f" {Colors.MINT}→{Colors.ENDC} {Colors.SILVER}{url_or_host}{Colors.ENDC} {Colors.GOLD}[{status}]{Colors.ENDC}")
                else:
                    print(f" {Colors.MINT}→{Colors.ENDC} {Colors.SILVER}{url_or_host}{Colors.ENDC}")
            print(f"{Colors.SKY}{Colors.BOLD}{'='*59}{Colors.ENDC}")
            
            try:
                save_opt = input(f"\n{Colors.GOLD}[?] EXPORT RESULTS? (Y/N): {Colors.ENDC}").lower().strip()
                if save_opt == 'y':
                    fname = input(f"{Colors.GOLD}[?] FILENAME: {Colors.ENDC}").strip() or f"hunter_{target}.txt"
                    with open(fname, "w", encoding='utf-8') as f:
                        f.write("\n".join(final_list))
                    print(f" {Colors.MINT}[✓] EXPORTED TO: {fname}{Colors.ENDC}")
            except (IOError, OSError) as e:
                print(f" {Colors.CORAL}[!] EXPORT ERROR: {e}{Colors.ENDC}")
            except KeyboardInterrupt:
                print()
        else:
            status_log(f" {Colors.CORAL}[!] NO RESULTS FOUND{Colors.ENDC}")
    
    status_log(f"\n {Colors.SKY}[!] SCAN COMPLETED. HAPPY HUNTING!{Colors.ENDC}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        stop_animation.set()
        status_log("\n [!] SESSION TERMINATED.", Colors.CORAL)
        sys.exit(0)
    except Exception as e:
        stop_animation.set()
        status_log(f"\n [!] ERROR: {e}", Colors.CORAL)
        sys.exit(1)
