#!/usr/bin/env bash
# Deploy script for Neuropuppet
# Pulls latest changes, installs dependencies, and launches the app.

set -euo pipefail

REPO_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$REPO_DIR"

# Update repository
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    if git remote | grep -q .; then
        echo "Updating repository..."
        git pull --ff-only
    else
        echo "No git remote configured; skipping pull"
    fi
fi

# Set up virtual environment
if [ ! -d venv ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

# Launch the main application
exec python main.py "$@"
