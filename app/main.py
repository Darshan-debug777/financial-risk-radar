
# app/main.py
from fastapi import FastAPI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
api_secret = os.getenv("GEMINI_API_SECRET")

# Create FastAPI app
app = FastAPI(title="Financial Risk Radar API")

# Include routers
from .routers.upload import router as upload_router
app.include_router(upload_router, prefix="/upload", tags=["upload"])

# Root endpoint
@app.get("/")
def root():
    return {"status": "Financial Risk Radar API is running."}
