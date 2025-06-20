from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os

# --- Import your agent from main.py ---
from main import agent

# --- FastAPI App Setup ---
app = FastAPI(title="Metrics Dictionary Q&A", description="Chatbot for metric definitions from Excel")

# Serve static files (put your HTML/CSS/JS in 'static/')
app.mount("/static", StaticFiles(directory="static"), name="static")

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@app.get("/")
def home():
    """Serve the main HTML page"""
    return FileResponse('static/index.html')

@app.get("/index.html")
def static_index():
    return FileResponse('static/index.html')

@app.post("/chat")
def chat(request: ChatRequest) -> ChatResponse:
    """Handle chat messages with the Pandas/Excel-based agent"""
    try:
        # Agent expects a plain question string
        # (No streaming needed for simple Q&A)
        response_text = agent.run(request.message)
        return ChatResponse(response=response_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Run with: uvicorn web_app:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
