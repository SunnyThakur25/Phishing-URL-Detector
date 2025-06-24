#!/bin/bash
exmaple:
echo "Setting up Phishing URL Detector..."
mkdir -p config/user_blocklist data
touch config/legit_domains.txt config/suspicious_tlds.txt config/user_blocklist/custom1.txt
echo "google.com\namazon.com\npaypal.com" > config/legit_domains.txt
echo "xyz\ntop\ninfo\nclub" > config/suspicious_tlds.txt
echo "http://fakebank.com/login" > config/user_blocklist/custom1.txt
pip install -r requirements.txt
echo "Setup complete."