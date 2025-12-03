#!/bin/bash

# LINA Tools Installation Script for macOS
# Installs common cybersecurity tools using Homebrew

echo "🛠️  LINA Tools Installation Script"
echo "===================================="
echo ""

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew is not installed!"
    echo ""
    echo "Please install Homebrew first:"
    echo "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    echo ""
    exit 1
fi

echo "✅ Homebrew detected"
echo ""

# Tools available via Homebrew
TOOLS=(
    "nmap"
    "masscan"
    "rustscan"
    "gobuster"
    "nikto"
    "feroxbuster"
    "ffuf"
    "hydra"
    "john-jumbo"
    "hashcat"
    "aircrack-ng"
    "tcpdump"
    "wireshark"
    "subfinder"
    "httpx"
    "sublist3r"
    "wget"
    "netcat"
)

echo "📦 Installing tools..."
echo ""

INSTALLED=0
SKIPPED=0
FAILED=0

for tool in "${TOOLS[@]}"; do
    # Handle special cases
    case $tool in
        "john-jumbo")
            tool_name="john"
            brew_name="john-jumbo"
            ;;
        *)
            tool_name="$tool"
            brew_name="$tool"
            ;;
    esac
    
    if command -v "$tool_name" &> /dev/null; then
        echo "✅ $tool_name (already installed)"
        ((SKIPPED++))
    else
        echo "⏳ Installing $tool_name..."
        if brew install "$brew_name" 2>/dev/null; then
            echo "   ✅ $tool_name installed"
            ((INSTALLED++))
        else
            echo "   ❌ Failed to install $tool_name"
            ((FAILED++))
        fi
    fi
done

echo ""
echo "===================================="
echo "📊 Summary:"
echo "  ✅ Installed: $INSTALLED"
echo "  ⏭️  Skipped: $SKIPPED"
echo "  ❌ Failed: $FAILED"
echo ""

echo "🐍 Python tools (install separately):"
echo "  pip install sqlmap volatility3 sublist3r"
echo ""

echo "✅ Done! Check Tools page in LINA to see what's installed."
