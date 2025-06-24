import sys
from pathlib import Path
from src.utils.blocklist import fetch_blocklist
from src.utils.typosquatting import check_typosquatting
from src.utils.homoglyph import check_homoglyph
from src.cli.sandbox import open_browserling, open_cuckoo
import tldextract

CONFIG_DIR = Path("config")
LEGIT_DOMAINS_FILE = CONFIG_DIR / "legit_domains.txt"
SUSPICIOUS_TLDS_FILE = CONFIG_DIR / "suspicious_tlds.txt"

def load_config(file_path):
    try:
        with open(file_path, "r") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        sys.exit(1)

def analyze_url(url, blocklist, legit_domains, suspicious_tlds, expert_mode=False):
    # Blocklist check
    if url in blocklist:
        return "Phishing detected: URL in blocklist."
    
    # Extract domain
    extracted = tldextract.extract(url)
    domain = f"{extracted.domain}.{extracted.suffix}"
    
    # Typosquatting check
    typosquat, typo_msg = check_typosquatting(domain, legit_domains)
    if typosquat:
        return f"Phishing likely: {typo_msg}"
    
    # Homoglyph check
    homoglyph, homo_msg = check_homoglyph(url)
    if homoglyph:
        return f"Phishing likely: {homo_msg}"
    
    # Suspicious TLD check
    if extracted.suffix in suspicious_tlds:
        return "Phishing likely: Suspicious TLD detected."
    
    # Uncertain case
    return f"Uncertain. Open in {'Cuckoo' if expert_mode else 'Browserling'} sandbox? (y/n)"

def main():
    # Load configs
    legit_domains = load_config(LEGIT_DOMAINS_FILE)
    suspicious_tlds = load_config(SUSPICIOUS_TLDS_FILE)
    
    # Fetch blocklist
    blocklist = fetch_blocklist()
    
    # Get user input
    expert_mode = input("Expert mode (Cuckoo Sandbox)? (y/n): ").lower() == "y"
    url = input("Enter URL to check: ")
    
    # Analyze URL
    result = analyze_url(url, blocklist, legit_domains, suspicious_tlds, expert_mode)
    print(result)
    
    # Sandbox option
    if "Uncertain" in result and input().lower() == "y":
        sandbox_result = open_cuckoo(url) if expert_mode else open_browserling(url)
        print(sandbox_result)

if __name__ == "__main__":
    main()