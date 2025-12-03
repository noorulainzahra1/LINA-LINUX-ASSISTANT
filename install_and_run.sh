#!/bin/bash

##############################################################################
# LINA - AI-Powered Cybersecurity Assistant
# Comprehensive Installer and Launcher Script
# Automatically installs dependencies, system tools, and starts servers
##############################################################################

# Don't exit on error - we want to continue even if some tools fail to install
set +e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Configuration
BACKEND_PORT=8000
FRONTEND_PORT=3000
BACKEND_LOG="/tmp/lina_backend.log"
FRONTEND_LOG="/tmp/lina_frontend.log"
PID_FILE="/tmp/lina.pid"

# Function to print colored output
print_status() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_header() {
    echo -e "${CYAN}"
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║         LINA - AI Cybersecurity Assistant                  ║"
    echo "║         Comprehensive Installer & Launcher                 ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to detect terminal emulator
detect_terminal() {
    if command_exists gnome-terminal; then
        echo "gnome-terminal"
    elif command_exists xterm; then
        echo "xterm"
    elif command_exists konsole; then
        echo "konsole"
    else
        echo ""
    fi
}

# Function to open log terminal window
open_log_terminal() {
    local terminal=$(detect_terminal)
    local log_file=$1
    local title=$2
    
    if [ -z "$terminal" ]; then
        print_warning "No terminal emulator found. Logs will be in: $log_file"
        return
    fi
    
    case $terminal in
        gnome-terminal)
            gnome-terminal --title="$title" -- bash -c "tail -f $log_file; exec bash" 2>/dev/null &
            ;;
        xterm)
            xterm -title "$title" -e "tail -f $log_file" 2>/dev/null &
            ;;
        konsole)
            konsole --title "$title" -e "tail -f $log_file" 2>/dev/null &
            ;;
    esac
}

# Function to cleanup on exit
cleanup() {
    # Only cleanup if servers were actually started
    if [ -f "$PID_FILE" ] || pgrep -f "uvicorn.*api.main:app" >/dev/null 2>&1 || pgrep -f "vite" >/dev/null 2>&1; then
        echo ""
        print_status "Shutting down LINA servers..."
        
        # Kill processes
        if [ -f "$PID_FILE" ]; then
            while read -r pid; do
                if kill -0 "$pid" 2>/dev/null; then
                    kill "$pid" 2>/dev/null
                fi
            done < "$PID_FILE"
            rm -f "$PID_FILE"
        fi
        
        # Kill any remaining uvicorn/vite processes
        pkill -f "uvicorn.*api.main:app" 2>/dev/null || true
        pkill -f "vite" 2>/dev/null || true
        
        print_success "Shutdown complete"
    fi
    exit 0
}

# Trap signals - only cleanup if servers are running
# We'll set a flag when servers start, and only cleanup if that flag is set
SERVERS_STARTED=false

trap 'if [ "$SERVERS_STARTED" = true ]; then cleanup; else exit 0; fi' SIGINT SIGTERM
trap 'if [ "$SERVERS_STARTED" = true ] && [ -f "$PID_FILE" ]; then cleanup; fi' EXIT

# Print header
clear
print_header

# ============================================================================
# STEP 1: Check and Install System Dependencies
# ============================================================================
echo -e "${YELLOW}[1/7]${NC} Checking system dependencies..."

# Check Python
if ! command_exists python3; then
    print_error "Python 3 is not installed!"
    print_status "Installing Python 3..."
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv
else
    PYTHON_VERSION=$(python3 --version)
    print_success "Found: $PYTHON_VERSION"
fi

# Check Node.js
if ! command_exists node; then
    print_error "Node.js is not installed!"
    print_status "Installing Node.js..."
    sudo apt update
    sudo apt install -y nodejs npm
    # If Node.js version is too old, install from NodeSource
    NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -lt 18 ]; then
        print_status "Node.js version is too old. Installing Node.js 18+..."
        curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
        sudo apt install -y nodejs
    fi
else
    NODE_VERSION=$(node --version)
    print_success "Found: $NODE_VERSION"
fi

# Check npm
if ! command_exists npm; then
    print_error "npm is not installed!"
    print_status "Installing npm..."
    sudo apt install -y npm
else
    NPM_VERSION=$(npm --version)
    print_success "Found: npm $NPM_VERSION"
fi

# ============================================================================
# STEP 2: Install System Security Tools
# ============================================================================
echo ""
echo -e "${YELLOW}[2/7]${NC} Installing system security tools..."

# List of tools to install
SYSTEM_TOOLS=(
    "nmap"
    "masscan"
    "rustscan"
    "gobuster"
    "dirb"
    "nikto"
    "sqlmap"
    "hydra"
    "wfuzz"
    "subfinder"
    "sublist3r"
    "httpx"
    "whatweb"
    "wafw00f"
    "wpscan"
    "volatility3"
    "foremost"
    "autopsy"
    "sleuthkit"
    "binwalk"
    "testdisk"
    "photorec"
    "scrounge-ntfs"
    "magicrescue"
    "curl"
    "wget"
    "netcat"
    "tcpdump"
    "tshark"
    "dig"
    "whois"
    "nslookup"
    "tmux"
)

INSTALLED_COUNT=0
SKIPPED_COUNT=0
FAILED_COUNT=0

for tool in "${SYSTEM_TOOLS[@]}"; do
    if command_exists "$tool"; then
        ((SKIPPED_COUNT++))
    else
        print_status "Installing $tool..."
        # Don't fail the script if a tool installation fails
        if sudo apt install -y "$tool" >/dev/null 2>&1; then
            print_success "$tool installed"
            ((INSTALLED_COUNT++))
        else
            # Try installing via pip for Python tools
            if [[ "$tool" == "sqlmap" ]] || [[ "$tool" == "sublist3r" ]] || [[ "$tool" == "volatility3" ]]; then
                print_status "Trying to install $tool via pip..."
                if pip3 install "$tool" >/dev/null 2>&1; then
                    print_success "$tool installed (via pip)"
                    ((INSTALLED_COUNT++))
                else
                    print_warning "Failed to install $tool (non-critical)"
                    ((FAILED_COUNT++))
                fi
            else
                print_warning "Failed to install $tool (non-critical)"
                ((FAILED_COUNT++))
            fi
        fi
    fi
done

# Re-enable exit on error for critical operations
set -e

print_status "Tools summary: $INSTALLED_COUNT installed, $SKIPPED_COUNT already installed, $FAILED_COUNT failed"

# ============================================================================
# STEP 3: Setup Python Virtual Environment
# ============================================================================
echo ""
echo -e "${YELLOW}[3/7]${NC} Setting up Python environment..."

if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_success "Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip -q

# Install Python dependencies
if ! python -c "import fastapi" 2>/dev/null; then
    print_status "Installing Python dependencies (this may take a few minutes)..."
    pip install -r requirements.txt -q
    print_success "Python dependencies installed"
else
    print_success "Python dependencies already installed"
fi

# ============================================================================
# STEP 4: Setup Frontend Dependencies
# ============================================================================
echo ""
echo -e "${YELLOW}[4/7]${NC} Setting up frontend..."

if [ ! -d "frontend/node_modules" ]; then
    print_status "Installing frontend dependencies (this may take a few minutes)..."
    cd frontend
    npm install --silent
    cd ..
    print_success "Frontend dependencies installed"
else
    print_success "Frontend dependencies already installed"
fi

# ============================================================================
# STEP 5: Check/Create Environment File
# ============================================================================
echo ""
echo -e "${YELLOW}[5/7]${NC} Checking environment configuration..."

if [ ! -f "env" ] && [ ! -f ".env" ]; then
    print_warning "No env file found!"
    print_status "Creating template env file..."
    cat > env << EOF
# LINA AI Configuration
# Get your API key from: https://aistudio.google.com/apikey
GOOGLE_API_KEY=your_api_key_here
EOF
    print_warning "Please edit 'env' file and add your GOOGLE_API_KEY"
    print_status "You can continue, but LINA won't work until API key is set"
else
    print_success "Environment file found"
fi

# ============================================================================
# STEP 6: Cleanup Existing Servers
# ============================================================================
echo ""
echo -e "${YELLOW}[6/7]${NC} Cleaning up existing servers..."

pkill -f "uvicorn.*api.main:app" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true
sleep 1

# Clear old log files
> "$BACKEND_LOG"
> "$FRONTEND_LOG"

# ============================================================================
# STEP 7: Start Servers
# ============================================================================
echo ""
echo -e "${YELLOW}[7/7]${NC} Starting LINA servers..."

# Mark that servers are starting (so cleanup will work if interrupted)
SERVERS_STARTED=true

# Start backend
print_status "Starting Backend API on http://localhost:$BACKEND_PORT"
cd "$SCRIPT_DIR"
source venv/bin/activate
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port $BACKEND_PORT > "$BACKEND_LOG" 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > "$PID_FILE"

# Wait for backend to start
print_status "Waiting for backend to initialize..."
sleep 3
for i in {1..30}; do
    if curl -s http://localhost:$BACKEND_PORT/ > /dev/null 2>&1 || \
       curl -s http://localhost:$BACKEND_PORT/api/health > /dev/null 2>&1; then
        print_success "Backend is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        print_warning "Backend may still be starting..."
    fi
    sleep 1
done

# Start frontend
print_status "Starting Frontend on http://localhost:$FRONTEND_PORT"
cd "$SCRIPT_DIR/frontend"
npm run dev > "$FRONTEND_LOG" 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID >> "$PID_FILE"
cd "$SCRIPT_DIR"

# Wait for frontend to start
print_status "Waiting for frontend to initialize..."
sleep 5
for i in {1..30}; do
    if curl -s http://localhost:$FRONTEND_PORT > /dev/null 2>&1; then
        print_success "Frontend is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        print_warning "Frontend may still be starting..."
    fi
    sleep 1
done

# ============================================================================
# STEP 8: Open Log Terminal Windows
# ============================================================================
echo ""
print_status "Opening log terminal windows..."

# Open backend log terminal
open_log_terminal "$BACKEND_LOG" "LINA Backend Logs"
sleep 1

# Open frontend log terminal
open_log_terminal "$FRONTEND_LOG" "LINA Frontend Logs"
sleep 1

# ============================================================================
# Success Message
# ============================================================================
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    ✅ LINA is Running!                     ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}📍 Access Points:${NC}"
echo -e "   Frontend:  ${GREEN}http://localhost:$FRONTEND_PORT${NC}"
echo -e "   Backend:   ${GREEN}http://localhost:$BACKEND_PORT${NC}"
echo -e "   API Docs:  ${GREEN}http://localhost:$BACKEND_PORT/api/docs${NC}"
echo ""
echo -e "${YELLOW}📝 Logs:${NC}"
echo -e "   Backend:  $BACKEND_LOG"
echo -e "   Frontend: $FRONTEND_LOG"
echo -e "   (Separate terminal windows have been opened for real-time logs)"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop both servers${NC}"
echo ""

# Try to open browser
if command_exists xdg-open; then
    print_status "Opening browser..."
    sleep 2
    xdg-open "http://localhost:$FRONTEND_PORT" > /dev/null 2>&1 &
fi

# Keep script running and monitor processes
while true; do
    # Check if processes are still alive
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        print_error "Backend process died. Check $BACKEND_LOG"
        break
    fi
    
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        print_error "Frontend process died. Check $FRONTEND_LOG"
        break
    fi
    
    sleep 5
done

cleanup

