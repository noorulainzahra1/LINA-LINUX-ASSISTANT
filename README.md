# LINA - AI-Powered Cybersecurity Assistant

## Quick Start Guide

### Option 1: Double-Click Desktop File (Easiest)

1. **Install the desktop shortcut** (recommended for first time):
   ```bash
   cd /path/to/FinalReady
   ./install_desktop_shortcut.sh
   ```
   This will add LINA to your applications menu and make the desktop file work properly.

2. **Or double-click the `LINA.desktop` file** directly in this folder

3. The installer will automatically:
   - Check and install system dependencies (Python, Node.js)
   - Install all required cybersecurity tools (nmap, hydra, sqlmap, etc.)
   - Set up Python virtual environment
   - Install Python and frontend dependencies
   - Start both backend and frontend servers
   - Open separate terminal windows showing real-time logs

3. **Access LINA** at: http://localhost:3000

### Option 2: Run from Terminal

```bash
cd /path/to/FinalReady
chmod +x install_and_run.sh
./install_and_run.sh
```

## First-Time Setup

### API Key Configuration

Before using LINA, you need to configure your Google Gemini API key:

1. Get a free API key from: https://aistudio.google.com/apikey
2. Edit the `env` file in this folder:
   ```bash
   nano env
   # or use any text editor
   ```
3. Replace `your_api_key_here` with your actual API key:
   ```
   GOOGLE_API_KEY=your_actual_api_key_here
   ```
4. Save and restart LINA if it's already running

## What Gets Installed

### System Dependencies
- Python 3.8+ and pip
- Node.js 18+ and npm

### Cybersecurity Tools (via apt)
- Network scanning: nmap, masscan, rustscan
- Web enumeration: gobuster, dirb, nikto, wfuzz
- Exploitation: sqlmap, hydra
- Subdomain discovery: subfinder, sublist3r, httpx
- Web analysis: whatweb, wafw00f, wpscan
- Forensics: volatility3, foremost, autopsy, sleuthkit, binwalk, testdisk
- Network tools: tcpdump, tshark, dig, whois, netcat
- Utilities: curl, wget, tmux

### Python Dependencies
All packages from `requirements.txt` including:
- FastAPI, uvicorn (backend framework)
- google-generativeai (AI integration)
- And many more...

### Frontend Dependencies
All packages from `frontend/package.json` including:
- React, TypeScript, Vite
- Tailwind CSS
- And more...

## Features

- **Natural Language Interface**: Talk to LINA like a colleague
- **Command Generation**: LINA suggests and executes security tools
- **Risk Assessment**: Built-in safety checks for dangerous commands
- **Tool Integration**: Works with 82+ cybersecurity tools
- **Real-time Execution**: See command output in real-time
- **Separate Log Windows**: Backend and frontend logs in separate terminals

## Access Points

Once running:
- **Frontend UI**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs

## Log Files

- **Backend logs**: `/tmp/lina_backend.log`
- **Frontend logs**: `/tmp/lina_frontend.log`

Separate terminal windows will automatically open showing real-time logs.

## Stopping LINA

Press `Ctrl+C` in the terminal where you ran the installer, or:

```bash
pkill -f "uvicorn.*api.main:app"
pkill -f "vite"
```

## Troubleshooting

### Desktop File Not Working

If double-clicking `LINA.desktop` doesn't work:

**For XFCE (Kali Linux default):**
1. Right-click `LINA.desktop` → Properties → Permissions
2. Check "Allow executing file as program" 
3. Right-click again → Select "Open with Other Application" → Choose "Terminal Emulator"
4. Or run the installer shortcut:
   ```bash
   cd /path/to/FinalReady
   ./install_desktop_shortcut.sh
   ```

**For other desktop environments:**
1. Right-click `LINA.desktop` → Properties → Permissions
2. Check "Allow executing file as program"
3. Or run from terminal:
   ```bash
   cd /path/to/FinalReady
   ./launch_lina.sh
   ```

**Alternative: Always works from terminal**
```bash
cd /path/to/FinalReady
./install_and_run.sh
```

### Port Already in Use

If ports 8000 or 3000 are already in use:

```bash
# Find and kill process on port 8000
sudo lsof -ti:8000 | xargs kill -9

# Find and kill process on port 3000
sudo lsof -ti:3000 | xargs kill -9
```

### Installation Fails

1. Make sure you have internet connection
2. Check that you have sudo privileges (for installing system tools)
3. Try running manually:
   ```bash
   sudo apt update
   sudo apt install -y python3 python3-pip python3-venv nodejs npm
   ```

### API Key Issues

- Make sure the `env` file exists in the FinalReady folder
- Check that the API key is correctly formatted (no spaces around `=`)
- Restart LINA after changing the env file

## System Requirements

- **OS**: Kali Linux (or other Debian-based Linux)
- **Python**: 3.8 or higher
- **Node.js**: 18 or higher
- **RAM**: Minimum 2GB, recommended 4GB+
- **Disk Space**: ~500MB for dependencies
- **Internet**: Required for first-time installation

## Support

For detailed documentation, see:
- `DEPLOYMENT.md` - Deployment guide
- `CLIENT_README.md` - Client instructions
- `docs/` folder - Full documentation

---

**Enjoy using LINA!** 🚀
