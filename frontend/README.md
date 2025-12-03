# LINA Frontend

React-based frontend for the LINA AI-Powered Cybersecurity Assistant.

## Tech Stack

- **React 18** with TypeScript
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling
- **React Router** - Routing
- **React Query** - Data fetching and caching
- **Axios** - HTTP client

## Setup

### Prerequisites

- Node.js 18+ and npm/yarn
- Backend API running on `http://localhost:8000`

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

Frontend will be available at `http://localhost:3000`

### Build for Production

```bash
npm run build
```

## Project Structure

```
frontend/
├── src/
│   ├── components/      # Reusable UI components
│   ├── pages/           # Page components
│   ├── contexts/        # React contexts
│   ├── hooks/           # Custom React hooks
│   ├── services/        # API client
│   ├── types/           # TypeScript types
│   └── main.tsx         # Entry point
```

## Features

- **Role Selection**: Choose between Student, Forensic Expert, or Penetration Tester
- **Chat Interface**: Natural language interaction with LINA
- **Command Execution**: Execute commands with risk assessment
- **Real-time Output**: WebSocket streaming for command output
- **Tools Management**: Browse and filter available cybersecurity tools
- **Plan Viewer**: Visualize multi-step execution plans
- **Analytics Dashboard**: View session statistics and insights

## Environment Variables

Create a `.env` file:

```
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

