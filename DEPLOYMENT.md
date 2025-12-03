# LINA Deployment Guide

Complete guide for transferring and running LINA on a new system.

## 📋 Prerequisites

The target system needs:
- **Python 3.8+** (Python 3.11+ recommended)
- **Node.js 18+** and npm
- **Internet connection** (for initial dependency installation)

## 🚀 Quick Start (Easiest Method)

### For Linux/macOS:

1. **Transfer the project folder** to the target machine
2. **Make the startup script executable:**
   ```bash
   chmod +x start_lina.sh
   ```
3. **Run the startup script:**
   ```bash
   ./start_lina.sh
   ```

That's it! The script will:
- ✅ Check for required dependencies
- ✅ Create Python virtual environment
- ✅ Install all dependencies automatically
- ✅ Start both backend and frontend servers
- ✅ Show you the access URLs

## 📦 Manual Setup (Step-by-Step)

If you prefer to set up manually or the script doesn't work:

### Step 1: Transfer Files

Copy the entire project folder to the target machine. Required files:
- All `api/`, `agent/`, `core/`, `frontend/`, `utils/` directories
- `requirements.txt`, `main.py`
- `env` file (with GOOGLE_API_KEY)
- `start_lina.sh`, `run_dev.sh`

### Step 2: Install System Dependencies

**On Linux (Debian/Ubuntu/Kali):**
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nodejs npm
```

**On macOS:**
```bash
brew install python3 node
```

**On Windows:**
- Install Python from https://python.org
- Install Node.js from https://nodejs.org

### Step 3: Setup Environment

```bash
# Navigate to project directory
cd /path/to/transfer

# Create Python virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### Step 4: Configure API Key

Edit the `env` file and add your Google API key:
```bash
# LINA AI Configuration
GOOGLE_API_KEY=your_actual_api_key_here
```

### Step 5: Start Servers

**Option A: Using the startup script (recommended)**
```bash
chmod +x start_lina.sh
./start_lina.sh
```

**Option B: Manual start (two terminals)**

Terminal 1 - Backend:
```bash
source venv/bin/activate
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Terminal 2 - Frontend:
```bash
cd frontend
npm run dev
```

## 🌐 Access the Application

Once running:
- **Frontend UI:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/api/docs

## 🛠️ Troubleshooting

### Port Already in Use

If you get port conflict errors:

**Backend (port 8000):**
```bash
# Find and kill process using port 8000
lsof -ti:8000 | xargs kill -9  # macOS/Linux
# Or change port in start_lina.sh: --port 8001
```

**Frontend (port 3000):**
```bash
# Find and kill process using port 3000
lsof -ti:3000 | xargs kill -9  # macOS/Linux
# Or edit frontend/vite.config.ts to change port
```

### Python/Node Not Found

Make sure Python 3 and Node.js are in your PATH:
```bash
which python3
which node
which npm
```

### Dependencies Installation Fails

**Python dependencies:**
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt --no-cache-dir
```

**Frontend dependencies:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

### Session Errors

If you see "Session not found" errors:
1. Clear browser localStorage
2. Select your role again to create a new session
3. This is normal if the server was restarted

### API Key Issues

Make sure:
1. The `env` file exists in the project root
2. It contains: `GOOGLE_API_KEY=your_key_here`
3. No extra spaces around the `=` sign
4. Restart the server after changing the env file

## 📝 What to Transfer to Client

**Essential files/folders:**
```
transfer/
├── api/              (Backend API code)
├── agent/            (AI agent code)
├── core/             (Configuration and registries)
├── frontend/         (React frontend - without node_modules)
├── utils/            (Utility modules)
├── main.py           (Main initialization)
├── requirements.txt  (Python dependencies)
├── start_lina.sh     (Startup script)
├── env               (API key configuration)
└── README.md         (This file)
```

**DO NOT transfer:**
- `venv/` (virtual environment - will be created)
- `frontend/node_modules/` (will be installed)
- `__pycache__/` (Python cache)
- `.git/` (unless using git)

**Or transfer everything** and let the script handle it - it will recreate what's needed.

## 🔒 Security Notes

1. **Never commit `env` file to version control**
2. **Share API key securely** (not via email/chat)
3. **Use environment variables** in production instead of `env` file

## 📞 Support

If you encounter issues:
1. Check the logs: `/tmp/lina_backend.log` and `/tmp/lina_frontend.log`
2. Verify all prerequisites are installed
3. Make sure ports 3000 and 8000 are available
4. Check that the `env` file has a valid API key

---

**Last Updated:** 2025-11-01
**Version:** 1.0

