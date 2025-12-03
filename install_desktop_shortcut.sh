#!/bin/bash
# Install LINA desktop shortcut to make it work properly in XFCE/GNOME

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DESKTOP_FILE="$SCRIPT_DIR/LINA.desktop"
APPLICATIONS_DIR="$HOME/.local/share/applications"
INSTALLED_FILE="$APPLICATIONS_DIR/LINA.desktop"

echo "=========================================="
echo "LINA Desktop Shortcut Installer"
echo "=========================================="
echo ""

# Update desktop file with current path
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

# Make scripts executable
chmod +x "$SCRIPT_DIR/launch_lina.sh"
chmod +x "$SCRIPT_DIR/install_and_run.sh"
chmod +x "$DESKTOP_FILE"

# Create applications directory if it doesn't exist
mkdir -p "$APPLICATIONS_DIR"

# Copy desktop file to applications directory
cp "$DESKTOP_FILE" "$INSTALLED_FILE"
chmod +x "$INSTALLED_FILE"

# Update desktop database (if available)
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$APPLICATIONS_DIR" 2>/dev/null || true
fi

echo "✅ Desktop shortcut installed!"
echo ""
echo "The LINA launcher should now appear in your applications menu."
echo "You can also double-click the LINA.desktop file in the FinalReady folder."
echo ""
echo "To test, try running:"
echo "  $INSTALLED_FILE"
echo ""
echo "Or search for 'LINA' in your application menu."

