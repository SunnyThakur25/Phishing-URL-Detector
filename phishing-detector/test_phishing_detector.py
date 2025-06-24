import unittest
from unittest.mock import patch
import sys
from io import StringIO
from src.cli.phishing_detector import analyze_url, load_config, main
from src.cli.sandbox import open_browserling, open_cuckoo
from src.utils.blocklist import fetch_blocklist
from src.utils.typosquatting import check_typosquatting
from src.utils.homoglyph import check_homoglyph
from pathlib import Path

CONFIG_DIR = Path("config")
LEGIT_DOMAINS_FILE = CONFIG_DIR / "legit_domains.txt"
SUSPICIOUS_TLDS_FILE = CONFIG_DIR / "suspicious_tlds.txt"

class TestPhishingDetector(unittest.TestCase):
    def setUp(self):
        self.blocklist = fetch_blocklist()
        self.legit_domains = load_config(LEGIT_DOMAINS_FILE)
        self.suspicious_tlds = load_config(SUSPICIOUS_TLDS_FILE)

    def test_blocklist_check(self):
        url = "http://g0ogle-login.xyz/signin"
        result = analyze_url(url, self.blocklist, self.legit_domains, self.suspicious_tlds)
        self.assertIn("Phishing detected: URL in blocklist", result)

    def test_typosquatting_check(self):
        url = "http://g00gle.com/login"
        result = analyze_url(url, self.blocklist, self.legit_domains, self.suspicious_tlds)
        self.assertIn("Typosquatting detected: Similar to google.com", result)

    def test_homoglyph_check(self):
        url = "http://gοοgle.com/signin"
        result = analyze_url(url, self.blocklist, self.legit_domains, self.suspicious_tlds)
        self.assertIn("Homoglyph detected", result)

    def test_suspicious_tld_check(self):
        url = "https://example.site"
        result = analyze_url(url, self.blocklist, self.legit_domains, self.suspicious_tlds)
        self.assertIn("Suspicious TLD detected", result)

    def test_safe_url(self):
        url = "https://google.com"
        result = analyze_url(url, self.blocklist, self.legit_domains, self.suspicious_tlds)
        self.assertIn("Uncertain", result)

    @patch('webbrowser.open')
    def test_browserling_sandbox(self, mock_webbrowser):
        url = "https://example.com"
        result = open_browserling(url)
        self.assertIn("Opened in Browserling sandbox", result)
        mock_webbrowser.assert_called_with(f"https://www.browserling.com/browse/chrome/100/{url}")

    @patch('requests.post')
    def test_cuckoo_sandbox(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"task_id": 123}
        url = "https://example.com"
        result = open_cuckoo(url)
        self.assertIn("Cuckoo task created: ID=123", result)
        mock_post.assert_called_with("http://localhost:8090/tasks/create", json={"url": url}, timeout=5)

    @patch('sys.stdout', new_callable=StringIO)
    @patch('builtins.input', side_effect=['n', 'https://g0ogle-login.xyz/signin'])
    def test_main_blocklist(self, mock_input, mock_stdout):
        main()
        output = mock_stdout.getvalue()
        self.assertIn("Phishing detected: URL in blocklist", output)

    @patch('sys.stdout', new_callable=StringIO)
    @patch('builtins.input', side_effect=['n', 'https://example.com'])
    @patch('webbrowser.open')
    def test_main_sandbox(self, mock_webbrowser, mock_input, mock_stdout):
        main()
        output = mock_stdout.getvalue()
        self.assertIn("Uncertain. Open in Browserling sandbox? (y/n)", output)

if __name__ == '__main__':
    unittest.main()