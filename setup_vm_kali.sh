#!/bin/bash

# LINA VM Setup Script for Kali Linux
# Run this INSIDE a Kali Linux VM to set up LINA

echo "🚀 LINA Setup for Kali Linux VM"
echo "================================="
echo ""

# Check if running on Kali Linux
if ! grep -q "Kali" /etc/os-release 2>/dev/null; then
    echo "⚠️  Warning: This script is optimized for Kali Linux"
    echo "   It may work on other Debian-based systems too"
    echo ""
fi

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
echo ""
echo "🐍 Installing Python and dependencies..."
sudo apt install -y python3 python3-pip python3-venv git curl wget

# Install common cybersecurity tools (many should already be in Kali)
echo ""
echo "🛠️  Installing/Updating cybersecurity tools..."
sudo apt install -y \
    nmap \
    masscan \
    gobuster \
    nikto \
    sqlmap \
    hydra \
    john \
    hashcat \
    aircrack-ng \
    tcpdump \
    wireshark \
    feroxbuster \
    ffuf \
    wpscan \
    searchsploit \
    metasploit-framework \
    volatility3 \
    foremost \
    binwalk \
    sleuthkit \
    autopsy \
    dig \
    whois \
    netcat \
    curl \
    wget

echo ""
echo "✅ System tools installed"
echo ""

# Create virtual environment
echo "📦 Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Install frontend dependencies (if Node.js available)
if command -v node &> /dev/null; then
    echo ""
    echo "📦 Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
    echo "✅ Frontend dependencies installed"
else
    echo ""
    echo "⚠️  Node.js not found. Installing..."
    curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
    sudo apt install -y nodejs
    cd frontend
    npm install
    cd ..
fi

echo ""
echo "===================================="
echo "✅ LINA Setup Complete!"
echo "===================================="
echo ""
echo "📋 Next Steps:"
echo "   1. Create .env file with your GOOGLE_API_KEY:"
echo "      cp .env.example .env"
echo "      nano .env"
echo ""
echo "   2. Start LINA servers:"
echo "      ./run_dev.sh"
echo ""
echo "   3. Open browser to: http://localhost:3000"
echo ""
echo "🎉 Ready to use all 82 tools!"

