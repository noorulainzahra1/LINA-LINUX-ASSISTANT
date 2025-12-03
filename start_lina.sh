#!/bin/bash

##############################################################################
# LINA - AI-Powered Cybersecurity Assistant
# Startup Script - Automatically starts both backend and frontend servers
##############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "${CYAN}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║         LINA - AI Cybersecurity Assistant                  ║"
echo "║         Starting Development Environment...                ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python
echo -e "${YELLOW}[1/5]${NC} Checking Python..."
if ! command_exists python3; then
    echo -e "${RED}❌ Python 3 is not installed!${NC}"
    echo "   Please install Python 3.8+ first"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✅ Found: $PYTHON_VERSION${NC}"

# Check Node.js
echo -e "${YELLOW}[2/5]${NC} Checking Node.js..."
if ! command_exists node; then
    echo -e "${RED}❌ Node.js is not installed!${NC}"
    echo "   Please install Node.js 18+ first"
    exit 1
fi
NODE_VERSION=$(node --version)
echo -e "${GREEN}✅ Found: $NODE_VERSION${NC}"

# Check npm
echo -e "${YELLOW}[3/5]${NC} Checking npm..."
if ! command_exists npm; then
    echo -e "${RED}❌ npm is not installed!${NC}"
    exit 1
fi
NPM_VERSION=$(npm --version)
echo -e "${GREEN}✅ Found: npm $NPM_VERSION${NC}"

# Setup Python virtual environment
echo -e "${YELLOW}[4/5]${NC} Setting up Python environment..."
if [ ! -d "venv" ]; then
    echo "   Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies if needed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "   Installing Python dependencies (this may take a minute)..."
    pip install --upgrade pip -q
    pip install python-dotenv rich requests typing-extensions dotenv google-generativeai aiohttp pydantic fastapi 'uvicorn[standard]' websockets python-socketio python-multipart psutil sqlalchemy cryptography urllib3 pytest pytest-asyncio pytest-cov black flake8 isort -q
    echo -e "${GREEN}✅ Python dependencies installed${NC}"
else
    echo -e "${GREEN}✅ Python dependencies already installed${NC}"
fi

# Setup frontend dependencies
echo -e "${YELLOW}[5/5]${NC} Setting up frontend..."
if [ ! -d "frontend/node_modules" ]; then
    echo "   Installing frontend dependencies (this may take a minute)..."
    cd frontend
    npm install --silent
    cd ..
    echo -e "${GREEN}✅ Frontend dependencies installed${NC}"
else
    echo -e "${GREEN}✅ Frontend dependencies already installed${NC}"
fi

# Check for env file
if [ ! -f "env" ] && [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  Warning: No env file found!${NC}"
    echo "   Creating template env file..."
    echo "# LINA AI Configuration" > env
    echo "GOOGLE_API_KEY=your_api_key_here" >> env
    echo -e "${YELLOW}   Please edit 'env' file and add your GOOGLE_API_KEY${NC}"
fi

# Kill any existing servers
echo ""
echo -e "${CYAN}Cleaning up existing servers...${NC}"
pkill -f "uvicorn api.main:app" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true
sleep 1

# Start backend
echo -e "${CYAN}🚀 Starting Backend API on http://localhost:8000${NC}"
cd "$SCRIPT_DIR"
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000 > /tmp/lina_backend.log 2>&1 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"

# Wait for backend to start
sleep 3

# Check if backend started (check root endpoint instead of health)
echo "   Waiting for backend to be ready..."
sleep 2
for i in {1..10}; do
    if curl -s http://localhost:8000/ > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend is ready!${NC}"
        break
    fi
    if [ $i -eq 10 ]; then
        echo -e "${YELLOW}⚠️  Backend may still be starting (check /tmp/lina_backend.log)${NC}"
        echo "   Continuing anyway..."
    fi
    sleep 1
done

# Start frontend
echo -e "${CYAN}🚀 Starting Frontend on http://localhost:3000${NC}"
cd "$SCRIPT_DIR/frontend"
npm run dev > /tmp/lina_frontend.log 2>&1 &
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID"

# Wait a bit for frontend
sleep 3

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    ✅ LINA is Running!                     ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}📍 Access Points:${NC}"
echo -e "   Frontend:  ${GREEN}http://localhost:3000${NC}"
echo -e "   Backend:   ${GREEN}http://localhost:8000${NC}"
echo -e "   API Docs:  ${GREEN}http://localhost:8000/api/docs${NC}"
echo ""
echo -e "${YELLOW}📝 Logs:${NC}"
echo -e "   Backend:  /tmp/lina_backend.log"
echo -e "   Frontend: /tmp/lina_frontend.log"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop both servers${NC}"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down servers...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    pkill -f "uvicorn api.main:app" 2>/dev/null || true
    pkill -f "vite" 2>/dev/null || true
    echo -e "${GREEN}✅ Servers stopped${NC}"
    exit 0
}

# Trap Ctrl+C
trap cleanup INT TERM

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID 2>/dev/null || wait

