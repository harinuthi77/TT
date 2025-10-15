# ============================================
# COMPLETE PROJECT SETUP SCRIPT
# ============================================

Write-Host "`n🚀 Autonomous Agent Setup - Creating all files...`n" -ForegroundColor Cyan

# Create .env
Write-Host "📝 Creating .env file..." -ForegroundColor Green
@"
ANTHROPIC_API_KEY=your_claude_key_here
OPENAI_API_KEY=your_openai_key_here
GOOGLE_API_KEY=
"@ | Out-File -FilePath .env -Encoding UTF8 -NoNewline

Write-Host "✅ .env created" -ForegroundColor Green
Write-Host "`n⚠️  IMPORTANT: Edit .env and add your REAL API keys!`n" -ForegroundColor Yellow
Start-Sleep -Seconds 2
notepad .env
Read-Host "`nPress Enter after saving your API keys"

# docker-compose.yml
Write-Host "`n📝 Creating docker-compose.yml..." -ForegroundColor Green
@"
version: '3.8'

services:
  backend:
    build: ./backend
    container_name: agent-backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
      - ./results:/app/results
    env_file: .env
    command: uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build: ./frontend
    container_name: agent-frontend
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - VITE_API_URL=http://localhost:8000
    command: npm run dev -- --host 0.0.0.0
"@ | Out-File -FilePath docker-compose.yml -Encoding UTF8 -NoNewline

# .gitignore
@"
__pycache__/
*.pyc
node_modules/
.env
.env.local
results/
screenshots/
*.db
*.log
"@ | Out-File -FilePath .gitignore -Encoding UTF8 -NoNewline

# BACKEND FILES
Write-Host "📝 Creating backend files..." -ForegroundColor Green

# backend/Dockerfile
@"
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y wget gnupg && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install chromium
RUN playwright install-deps chromium
COPY . .
EXPOSE 8000
"@ | Out-File -FilePath backend/Dockerfile -Encoding UTF8 -NoNewline

# backend/requirements.txt
@"
fastapi==0.104.1
uvicorn[standard]==0.24.0
websockets==12.0
pydantic==2.5.0
anthropic==0.7.8
openai==1.3.0
playwright==1.40.0
python-dotenv==1.0.0
"@ | Out-File -FilePath backend/requirements.txt -Encoding UTF8 -NoNewline

# backend/api/__init__.py
"" | Out-File -FilePath backend/api/__init__.py -Encoding UTF8 -NoNewline

# backend/api/main.py
@'
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

app = FastAPI(title="Autonomous Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/api/tasks")
async def create_task(task: dict):
    return {"session_id": "test123", "status": "running"}

@app.websocket("/ws/tasks/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
'@ | Out-File -FilePath backend/api/main.py -Encoding UTF8 -NoNewline

Write-Host "✅ Backend files created" -ForegroundColor Green

# FRONTEND FILES
Write-Host "📝 Creating frontend files..." -ForegroundColor Green

# frontend/Dockerfile
@"
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 5173
"@ | Out-File -FilePath frontend/Dockerfile -Encoding UTF8 -NoNewline

# frontend/package.json
@'
{
  "name": "agent-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "framer-motion": "^10.16.4",
    "zustand": "^4.4.6"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.2.0",
    "tailwindcss": "^3.3.5",
    "vite": "^5.0.0"
  }
}
'@ | Out-File -FilePath frontend/package.json -Encoding UTF8 -NoNewline

# frontend/vite.config.js
@"
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: { host: '0.0.0.0', port: 5173 }
})
"@ | Out-File -FilePath frontend/vite.config.js -Encoding UTF8 -NoNewline

# frontend/index.html
@"
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Autonomous Agent</title>
</head>
<body>
  <div id="root"></div>
  <script type="module" src="/src/main.jsx"></script>
</body>
</html>
"@ | Out-File -FilePath frontend/index.html -Encoding UTF8 -NoNewline

# frontend/src/main.jsx
@"
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(<App />)
"@ | Out-File -FilePath frontend/src/main.jsx -Encoding UTF8 -NoNewline

# frontend/src/index.css
@"
@tailwind base;
@tailwind components;
@tailwind utilities;

body { margin: 0; font-family: system-ui, sans-serif; }
"@ | Out-File -FilePath frontend/src/index.css -Encoding UTF8 -NoNewline

# frontend/src/App.jsx
@'
import { useState } from 'react'

export default function App() {
  const [task, setTask] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    alert('Task submitted: ' + task)
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        <h1 className="text-5xl font-bold text-center mb-8">
          What do you want done?
        </h1>
        <form onSubmit={handleSubmit}>
          <textarea
            value={task}
            onChange={(e) => setTask(e.target.value)}
            placeholder="Describe what you want the agent to do..."
            className="w-full p-4 border rounded-lg mb-4"
            rows={5}
          />
          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  )
}
'@ | Out-File -FilePath frontend/src/App.jsx -Encoding UTF8 -NoNewline

# frontend/tailwind.config.js
@"
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: { extend: {} },
  plugins: []
}
"@ | Out-File -FilePath frontend/tailwind.config.js -Encoding UTF8 -NoNewline

# frontend/postcss.config.js
@"
export default {
  plugins: { tailwindcss: {}, autoprefixer: {} }
}
"@ | Out-File -FilePath frontend/postcss.config.js -Encoding UTF8 -NoNewline

Write-Host "✅ Frontend files created" -ForegroundColor Green

Write-Host "`n✅ ALL FILES CREATED SUCCESSFULLY!`n" -ForegroundColor Green
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "  1. Make sure Docker Desktop is running" -ForegroundColor White
Write-Host "  2. Run: docker-compose up --build" -ForegroundColor White
Write-Host "  3. Wait 2-3 minutes for build" -ForegroundColor White
Write-Host "  4. Open: http://localhost:5173`n" -ForegroundColor White

Read-Host "Press Enter to continue"