#!/bin/sh

# Configure environment
sudo apt-get update -y
sudo apt-get install chromium-browser -y
sudo apt-get install chromium-chromedriver -y
sudo apt-get install python-pip -y
sudo pip install requests
sudo pip install selenium

# Phase 1: Run the crawler
echo "Phase 1: Starting the crawler"
scrapy crawl scrapeTarget
echo "Phase 1: Completed"

# Phase 2 & 3: Generate and Inject the Payloads
echo "Phase 2 & 3: Generating and Injecting the Payloads"
mkdir response

declare -a categories=("SQL Injection" "Server Side Code Injection" "Directory Traversal" "Cross Site Request Forgery" "Open Redirect" "Shell Command Injection")

for category in "${categories[@]}"
do
	python payloadInjection.py "$category"
done
echo "Phase 2 & 3: Completed"

# Phase 4: Generate the Exploits
echo "Phase 4: Generating the exploit scripts"
mkdir exploits

python generateExploits.py
echo "Phase 4: Completed"

echo "Check vulnerableEndpoints.json file to find all the vulnerable endpoints."
