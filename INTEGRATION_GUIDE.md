# LINA Frontend Integration Guide

This guide explains how to set up and run the complete LINA system with the new web frontend.

## Architecture Overview

```
┌─────────────────┐
│  React Frontend │ (Port 3000)
│  (TypeScript)   │
└────────┬────────┘
         │ HTTP/REST + WebSocket
         ▼
┌─────────────────┐
│  FastAPI Backend│ (Port 8000)
│  (Python)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LINA Backend   │ (Original CLI code - UNTOUCHED)
│  (Brain/Agents) │
└─────────────────┘
```

## Prerequisites

1. **Python 3.8+** (Python 3.11.8 recommended)
2. **Node.js 18+** and npm
3. **Google Gemini API Key** (in `env` file as `GOOGLE_API_KEY`)
4. Virtual environment activated

## Quick Start

### Option 1: Automated Setup (Recommended)

```bash
cd /Users/ideofuzion/Downloads/Final-lina-new

# Activate virtual environment
source venv/bin/activate  # or: venv\Scripts\activate on Windows

# Install Python dependencies (includes FastAPI)
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..

# Run both servers
./run_dev.sh
```

This will start:
- Backend API at `http://localhost:8000`
- Frontend at `http://localhost:3000`
- API documentation at `http://localhost:8000/api/docs`

### Option 2: Manual Setup

#### Step 1: Backend Setup

```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start FastAPI server
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

#### Step 2: Frontend Setup (New Terminal)

```bash
cd frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

## Verifying the Setup

### 1. Check Backend API

Visit `http://localhost:8000/api/docs` - You should see FastAPI's interactive documentation.

Test endpoints:
- `GET /api/health` - Health check
- `GET /api/tools/list` - List all tools

### 2. Check Frontend

Visit `http://localhost:3000` - You should see the role selection screen.

### 3. Test Full Flow

1. Select a role (Student/Forensic Expert/Penetration Tester)
2. Chat interface should appear
3. Try commands like:
   - "explain nmap"
   - "scan localhost"
   - "what tools are available"

## API Endpoints

### Session Management
- `POST /api/session/create` - Create new session
- `GET /api/session/{session_id}/status` - Get session status
- `GET /api/session/{session_id}/analytics` - Get analytics
- `DELETE /api/session/{session_id}` - Delete session

### Request Processing
- `POST /api/request/process` - Process natural language request

### Command Execution
- `POST /api/command/execute` - Execute command
- `GET /api/command/execution/{execution_id}` - Get execution status

### Tools
- `GET /api/tools/list` - List all tools
- `GET /api/tools/{tool_name}` - Get tool info

### WebSocket
- `WS /ws/session/{session_id}` - Real-time command output streaming

## Project Structure

```
Final-lina-new/
├── api/                    # NEW: FastAPI backend wrapper
│   ├── main.py            # FastAPI application
│   ├── models.py          # Pydantic models
│   ├── routers/           # API route handlers
│   └── services/          # Business logic layer
├── frontend/              # NEW: React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── contexts/      # React contexts
│   │   ├── hooks/         # Custom hooks
│   │   └── services/      # API client
│   └── package.json
├── agent/                 # ORIGINAL: Unchanged
├── core/                  # ORIGINAL: Unchanged
├── main.py               # ORIGINAL: Still works as CLI
├── requirements.txt       # Modified: Added FastAPI deps
└── run_dev.sh            # NEW: Combined dev script
```

## Troubleshooting

### Backend Issues

**Import Errors:**
```bash
# Make sure you're in the project root
cd /Users/ideofuzion/Downloads/Final-lina-new

# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

**Port Already in Use:**
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9  # macOS/Linux
```

### Frontend Issues

**npm install fails:**
```bash
# Clear cache and try again
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Can't connect to backend:**
- Check backend is running on `http://localhost:8000`
- Check CORS settings in `api/main.py`
- Check browser console for errors

### WebSocket Issues

If real-time streaming doesn't work:
1. Check browser console for WebSocket connection errors
2. Verify WebSocket endpoint: `ws://localhost:8000/ws/session/{session_id}`
3. Check backend logs for WebSocket errors

## Development Workflow

### Making Backend Changes

1. Edit files in `api/` directory
2. FastAPI auto-reloads (if using `--reload`)
3. Test via `http://localhost:8000/api/docs`

### Making Frontend Changes

1. Edit files in `frontend/src/`
2. Vite auto-reloads the browser
3. Check browser console for errors

### Testing

**Test CLI (Original Backend):**
```bash
python main.py
```

**Test API:**
```bash
curl http://localhost:8000/api/health
```

**Test Frontend:**
Just open `http://localhost:3000` in browser

## Production Deployment

For production:

1. **Build Frontend:**
   ```bash
   cd frontend
   npm run build
   ```
   Output in `frontend/dist/`

2. **Serve Frontend:**
   - Option 1: Serve `dist/` with nginx/apache
   - Option 2: Serve from FastAPI (add static file serving)

3. **Backend:**
   ```bash
   uvicorn api.main:app --host 0.0.0.0 --port 8000
   ```
   Or use gunicorn for production

## Important Notes

✅ **Original Backend Untouched**: All original code in `agent/`, `core/`, `main.py` works exactly as before

✅ **CLI Still Works**: You can still run `python main.py` for CLI interface

✅ **API is Wrapper**: The FastAPI layer only wraps existing functionality, doesn't modify it

✅ **Additive Changes Only**: Only `requirements.txt` was modified (additions), no code removed

## Next Steps

1. ✅ Backend API - Complete
2. ✅ Frontend Application - Complete
3. ⏳ Testing & Integration - In Progress
4. ⏳ Documentation - In Progress

## Support

If you encounter issues:
1. Check this guide
2. Check browser/terminal console for errors
3. Verify all dependencies are installed
4. Ensure virtual environment is activated

