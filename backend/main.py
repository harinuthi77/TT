from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI(title="FORGE Agent Backend")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TaskRequest(BaseModel):
    task: str
    model: str
    tools: List[str]

@app.get("/")
async def root():
    return {"message": "🔨 FORGE Backend is Running!", "status": "healthy"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/execute")
async def execute_task(request: TaskRequest):
    """
    Receives task from FORGE frontend and processes it
    """
    print("=" * 60)
    print("🔨 FORGE Task Received:")
    print(f"   Task: {request.task}")
    print(f"   Model: {request.model}")
    print(f"   Tools: {request.tools}")
    print("=" * 60)
    
    # TODO: Add your actual agent execution logic here
    # This is where your agent orchestrator code will go
    
    return {
        "status": "success",
        "message": "Task received and processing",
        "task": request.task,
        "model": request.model,
        "tools": request.tools
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)