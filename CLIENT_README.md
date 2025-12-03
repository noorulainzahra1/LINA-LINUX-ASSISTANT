# LINA - AI-Powered Cybersecurity Assistant

Welcome to LINA! This is an AI-powered cybersecurity assistant that helps you with penetration testing, digital forensics, and security operations.

## 🚀 Quick Start

### Step 1: Check Requirements

Make sure you have:
- Python 3.8 or higher
- Node.js 18 or higher
- npm (comes with Node.js)

**Check if installed:**
```bash
python3 --version
node --version
npm --version
```

If any are missing, install them first (see DEPLOYMENT.md for instructions).

### Step 2: Run LINA

Simply run:
```bash
chmod +x start_lina.sh
./start_lina.sh
```

The script will:
- ✅ Check all dependencies
- ✅ Install everything needed automatically
- ✅ Start the servers
- ✅ Show you where to access the application

### Step 3: Configure API Key

Before using LINA, you need a Google Gemini API key:

1. Get an API key from: https://aistudio.google.com/apikey
2. Edit the `env` file in the project folder
3. Replace `your_api_key_here` with your actual API key
4. Save and restart LINA

### Step 4: Access LINA

Once running, open your web browser and go to:
**http://localhost:3000**

## 🎯 Using LINA

1. **Select Your Role:** Choose between Student, Forensic Expert, or Penetration Tester
2. **Start Chatting:** Type your questions or commands in natural language
3. **LINA Responds:** Get AI-powered assistance with cybersecurity tasks

## 📖 Features

- **Natural Language Interface:** Talk to LINA like a colleague
- **Command Generation:** LINA suggests and executes security tools
- **Risk Assessment:** Built-in safety checks for dangerous commands
- **Tool Integration:** Works with 82+ cybersecurity tools
- **Real-time Execution:** See command output in real-time

## 🛑 Stopping LINA

Press `Ctrl+C` in the terminal where you ran `start_lina.sh`, or:

```bash
pkill -f "uvicorn api.main:app"
pkill -f "vite"
```

## ❓ Need Help?

- Check `DEPLOYMENT.md` for detailed setup instructions
- Check logs at `/tmp/lina_backend.log` and `/tmp/lina_frontend.log`
- Verify your API key is set correctly in the `env` file

## 📝 Notes

- First startup may take a few minutes to install dependencies
- Keep the terminal window open while using LINA
- Sessions are stored in memory - restarting the server will create a new session

---

**Enjoy using LINA!** 🚀

