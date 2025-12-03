# 📦 Instructions for Transferring LINA to Client

## What You Need to Do

### Option 1: Transfer Everything (Recommended)

1. **Compress the entire project folder:**
   ```bash
   cd /home/kali/Desktop
   tar -czf lina_project.tar.gz transfer/
   # Or use zip:
   zip -r lina_project.zip transfer/
   ```

2. **Send the archive to your client** via:
   - Cloud storage (Google Drive, Dropbox, etc.)
   - Secure file transfer
   - USB drive
   - Any preferred method

3. **Give your client these instructions:**
   - Extract the archive
   - Open terminal in the `transfer` folder
   - Run: `chmod +x start_lina.sh && ./start_lina.sh`
   - See `CLIENT_README.md` for details

### Option 2: Transfer Only Essential Files

If you want to exclude large folders (to save space):

**Include:**
- All `api/`, `agent/`, `core/`, `frontend/src/`, `utils/` directories
- `main.py`, `requirements.txt`
- `start_lina.sh`, `run_dev.sh`
- `env` (with API key), or template
- All `.md` documentation files
- `frontend/package.json`, `frontend/vite.config.ts`, `frontend/tsconfig.json`

**Exclude (will be recreated):**
- `venv/` - Python virtual environment
- `frontend/node_modules/` - npm packages
- `__pycache__/` - Python cache
- `.git/` - Version control (unless needed)

**Commands to create minimal transfer:**
```bash
cd /home/kali/Desktop
mkdir lina_minimal
cp -r transfer/api transfer/agent transfer/core transfer/utils lina_minimal/
cp -r transfer/frontend/src lina_minimal/frontend/
cp transfer/main.py transfer/requirements.txt transfer/*.sh transfer/*.md lina_minimal/
cp transfer/frontend/package.json transfer/frontend/vite.config.ts transfer/frontend/tsconfig.json lina_minimal/frontend/
cp transfer/env lina_minimal/  # Or create template
tar -czf lina_minimal.tar.gz lina_minimal/
```

## 📋 Pre-Transfer Checklist

- [ ] Test that `./start_lina.sh` works on your system
- [ ] Update `env` file with a placeholder API key (client will replace)
- [ ] Ensure all documentation files are included
- [ ] Test that the project works after extraction
- [ ] Include instructions for getting Google API key

## 📝 Quick Transfer Command

**Complete project (recommended):**
```bash
cd /home/kali/Desktop
tar -czf lina_complete.tar.gz transfer/ --exclude='transfer/venv' --exclude='transfer/frontend/node_modules' --exclude='transfer/__pycache__'
```

This creates a compressed archive excluding large folders that will be recreated.

## 🎯 Client Setup Commands

Give your client these exact commands:

```bash
# 1. Extract the archive
tar -xzf lina_project.tar.gz
# OR
unzip lina_project.zip

# 2. Navigate to project
cd transfer

# 3. Make script executable
chmod +x start_lina.sh

# 4. Run LINA
./start_lina.sh
```

## 🔑 API Key Setup

Tell your client:

1. Get API key from: https://aistudio.google.com/apikey
2. Edit `env` file: `nano env` or use any text editor
3. Replace `your_api_key_here` with actual key
4. Save and restart LINA

## 📧 Email Template for Client

You can use this template:

```
Subject: LINA - AI Cybersecurity Assistant - Setup Instructions

Hi [Client Name],

I'm sending you LINA, an AI-powered cybersecurity assistant.

SETUP (3 steps):
1. Extract the attached archive
2. Open terminal in the extracted folder
3. Run: chmod +x start_lina.sh && ./start_lina.sh

REQUIREMENTS:
- Python 3.8+ and Node.js 18+ must be installed
- Internet connection for first-time setup

API KEY:
You'll need a Google Gemini API key (free):
- Get it from: https://aistudio.google.com/apikey
- Edit the 'env' file and add your key
- Restart the application

ACCESS:
Once running, open: http://localhost:3000

See CLIENT_README.md for detailed instructions.

Questions? Let me know!

Best regards,
[Your Name]
```

## ✅ Verification

After transfer, verify:
1. Client can extract the archive
2. Client has Python 3.8+ and Node.js 18+
3. `start_lina.sh` runs without errors
4. Servers start successfully
5. Client can access http://localhost:3000

---

**That's it!** The client just needs to extract and run `start_lina.sh`.

