# LINA FinalReady Package - Transfer Summary

## Package Contents

This FinalReady folder contains everything needed to run LINA on a new Kali Linux system.

### Key Files

1. **`install_and_run.sh`** - Main installer and launcher script
   - Automatically installs all dependencies
   - Installs system security tools
   - Sets up Python and Node.js environments
   - Starts both servers
   - Opens separate log terminal windows

2. **`LINA.desktop`** - Desktop launcher file
   - Double-click to launch LINA
   - Automatically runs the installer on first use

3. **`README.md`** - User instructions
   - Quick start guide
   - Troubleshooting tips
   - API key setup instructions

4. **`fix_desktop_path.sh`** - Helper script
   - Fixes desktop file path if moved to different location

### Source Code Directories

- `api/` - FastAPI backend code
- `agent/` - AI agent core logic
- `core/` - Configuration and tool registries
- `utils/` - Utility functions
- `frontend/src/` - React frontend source code

### Configuration Files

- `requirements.txt` - Python dependencies
- `frontend/package.json` - Frontend dependencies
- `core/config.yaml` - Main configuration
- `env` - Environment variables (API key)

### Documentation

- All `.md` files in root and `docs/` folder

### Data Files

- `core/registry/` - Tool and risk registries
- `core/registries/` - Individual tool registries (76 files)
- `data/` - Database and output directories
- `uploads/` - User uploads directory

## What's NOT Included (Will be Created)

- `venv/` - Python virtual environment (created on first run)
- `frontend/node_modules/` - Node.js packages (installed on first run)
- `__pycache__/` - Python cache (created at runtime)

## Transfer Instructions

### For You (Sender)

1. Compress the FinalReady folder:
   ```bash
   cd /home/kali/Desktop
   tar -czf FinalReady.tar.gz FinalReady/
   # Or use zip:
   zip -r FinalReady.zip FinalReady/
   ```

2. Transfer the archive to the recipient via:
   - Cloud storage (Google Drive, Dropbox, etc.)
   - USB drive
   - Network transfer
   - Any preferred method

### For Recipient

1. Extract the archive:
   ```bash
   tar -xzf FinalReady.tar.gz
   # Or
   unzip FinalReady.zip
   ```

2. Navigate to FinalReady folder:
   ```bash
   cd FinalReady
   ```

3. **Option A**: Double-click `LINA.desktop` file

   **Option B**: Run from terminal:
   ```bash
   chmod +x install_and_run.sh
   ./install_and_run.sh
   ```

4. Wait for installation (first time takes 5-10 minutes)

5. Configure API key in `env` file (see README.md)

6. Access LINA at http://localhost:3000

## System Requirements

- **OS**: Kali Linux (or Debian-based Linux)
- **Python**: 3.8+ (will be installed if missing)
- **Node.js**: 18+ (will be installed if missing)
- **Internet**: Required for first-time installation
- **Sudo**: Required for installing system tools
- **Disk Space**: ~500MB for dependencies

## What Gets Installed Automatically

### System Tools (via apt)
- Network scanning tools (nmap, masscan, rustscan)
- Web enumeration tools (gobuster, dirb, nikto)
- Exploitation tools (sqlmap, hydra)
- Forensics tools (volatility3, foremost, autopsy, etc.)
- And 20+ more tools

### Python Packages
- FastAPI, uvicorn (web framework)
- google-generativeai (AI integration)
- All dependencies from requirements.txt

### Frontend Packages
- React, TypeScript, Vite
- Tailwind CSS
- All dependencies from package.json

## Package Size

- **Source code**: ~136 MB
- **After installation**: ~500 MB (with dependencies)

## Verification Checklist

Before transferring, verify:
- [ ] All source directories are present (api/, agent/, core/, utils/, frontend/src/)
- [ ] Configuration files are present (requirements.txt, package.json, config.yaml, env)
- [ ] install_and_run.sh is executable
- [ ] LINA.desktop file exists
- [ ] README.md is present
- [ ] Tool registries are present (core/registries/ has 76+ JSON files)
- [ ] Data directories exist (data/, uploads/)

## Notes

- The `env` file contains a template API key - recipient must add their own
- First run will take longer due to dependency installation
- Recipient needs sudo access for system tool installation
- All logs will be visible in separate terminal windows

---

**Ready for Transfer!** 🚀

