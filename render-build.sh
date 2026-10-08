#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Installing Playwright system dependencies for Chrome (fixes Error 127)..."
# Render comes with node/npx installed. We can use playwright's install-deps script to install all OS libraries for Chromium!
npx playwright install-deps chromium

echo "Build complete."
