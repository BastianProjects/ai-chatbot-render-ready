#!/usr/bin/env bash
set -e

echo "Installing Google Chrome..."
wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt-get update
apt-get install -y ./google-chrome-stable_current_amd64.deb

echo "Installing ChromeDriver..."
CHROME_VERSION=$(google-chrome --version | grep -oP '[0-9]+' | head -1)
CHROMEDRIVER_VERSION=$(curl -sSL "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}")
wget -q "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
unzip chromedriver_linux64.zip
chmod +x chromedriver
mv chromedriver /usr/local/bin/chromedriver