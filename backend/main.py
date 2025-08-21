"""
FastAPI Backend for AI Portfolio Generator

Entry point for the application that brings together all modules:
- GitHub OAuth authentication
- Repository creation
- AI portfolio generation
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import uvicorn
import os
from dotenv import load_dotenv

from auth import get_github_auth_url, handle_github_callback, get_current_user
from github_api import create_repository
from ai_agent import generate_portfolio

# Load environment variables
load_dotenv()

app = FastAPI(
    title="AI Portfolio Generator API",
    description="Backend API for generating AI-powered portfolio websites",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes from other modules
@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "AI Portfolio Generator API is running"}

@app.get("/login/github")
async def login_github():
    """Redirect user to GitHub OAuth page"""
    auth_url = get_github_auth_url()
    return RedirectResponse(url=auth_url)

@app.get("/auth/callback")
async def auth_callback(code: str, state: str = None):
    """Handle GitHub OAuth callback"""
    try:
        user_data = await handle_github_callback(code)
        return {
            "message": "Authentication successful",
            "user": user_data["username"],
            "status": "authenticated"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Authentication failed: {str(e)}")

@app.post("/create_repo")
async def create_repo(
    repo_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Create a new GitHub repository"""
    try:
        repo_name = repo_data.get("name")
        if not repo_name:
            raise HTTPException(status_code=400, detail="Repository name is required")
        
        repo_info = await create_repository(current_user["access_token"], repo_name)
        return {
            "message": "Repository created successfully",
            "repository": repo_info
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create repository: {str(e)}")

@app.post("/generate_portfolio")
async def generate_portfolio_endpoint(
    student_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Generate AI portfolio for student"""
    try:
        # TODO: Integrate with PDF parsing module here
        # TODO: Connect LLM agent for content generation
        result = await generate_portfolio(student_data, current_user)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Portfolio generation failed: {str(e)}")

if __name__ == "__main__":
    # Development server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
