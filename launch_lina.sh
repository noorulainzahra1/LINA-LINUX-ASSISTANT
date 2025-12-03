#!/bin/bash
# LINA Launcher - Auto-detects location and launches installer

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to that directory
cd "$SCRIPT_DIR"

# Execute the main installer/launcher
exec "$SCRIPT_DIR/install_and_run.sh"
