#!/bin/bash
# Helper script to fix the desktop file path
# Run this if the desktop file doesn't work from a different location

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DESKTOP_FILE="$SCRIPT_DIR/LINA.desktop"

echo "=========================================="
echo "LINA Desktop File Path Fixer"
echo "=========================================="
echo ""
echo "Current FinalReady location: $SCRIPT_DIR"
echo ""

# Create a new desktop file with absolute path
cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=LINA
Comment=AI-Powered Cybersecurity Assistant - Install and Launch
Exec=$SCRIPT_DIR/launch_lina.sh
Icon=terminal
Terminal=true
Categories=Security;Network;Development;
StartupNotify=true
Path=$SCRIPT_DIR
EOF

chmod +x "$DESKTOP_FILE"
chmod +x "$SCRIPT_DIR/launch_lina.sh"
chmod +x "$SCRIPT_DIR/install_and_run.sh"

echo "✅ Desktop file updated successfully!"
echo "✅ Scripts are executable"
echo ""
echo "You can now double-click LINA.desktop to launch"
echo ""
echo "If it still doesn't work:"
echo "  1. Right-click LINA.desktop → Properties → Permissions"
echo "  2. Check 'Allow executing file as program'"
echo "  3. Or run: ./launch_lina.sh from terminal"
