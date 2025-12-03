# LINA Application Launcher

## Quick Start

### Option 1: Run from Terminal
```bash
./lina
```

### Option 2: Desktop Shortcut
Double-click the `LINA.desktop` file on your desktop (if copied).

### Option 3: Create System-wide Command
```bash
sudo cp lina /usr/local/bin/lina
sudo chmod +x /usr/local/bin/lina
```

Then you can run LINA from anywhere:
```bash
lina
```

## Commands

- `./lina` - Start LINA (both backend and frontend)
- `./lina stop` - Stop LINA servers
- `./lina restart` - Restart LINA servers
- `./lina status` - Check if servers are running

## What It Does

1. ✅ Checks for virtual environment and dependencies
2. ✅ Starts backend server on port 8000
3. ✅ Starts frontend server on port 3000
4. ✅ Waits for both servers to be ready
5. ✅ Automatically opens browser
6. ✅ Monitors processes and handles cleanup on exit

## Logs

- Backend logs: `/tmp/lina_backend.log`
- Frontend logs: `/tmp/lina_frontend.log`

## Troubleshooting

If servers don't start:
1. Check logs: `tail -f /tmp/lina_backend.log`
2. Check if ports are in use: `netstat -tlnp | grep -E ':(8000|3000)'`
3. Stop any existing instances: `./lina stop`

