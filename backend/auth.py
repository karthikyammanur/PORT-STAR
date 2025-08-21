"""
GitHub OAuth Authentication Module

Handles the complete OAuth flow:
1. Generate GitHub authorization URL
2. Exchange authorization code for access token
3. Store and manage user sessions
4. Provide user authentication dependencies
"""

import os
import secrets
import requests
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer
from typing import Dict, Optional
import urllib.parse

# In-memory storage for user sessions (use database in production)
user_sessions: Dict[str, dict] = {}
oauth_states: Dict[str, bool] = {}

# GitHub OAuth configuration
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "your_github_client_id")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "your_github_client_secret")
REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:8000/auth/callback")

# OAuth scopes - repo scope allows creating repositories
GITHUB_SCOPES = "repo user:email"

security = HTTPBearer()

def get_github_auth_url() -> str:
    """
    Generate GitHub OAuth authorization URL
    
    Returns:
        str: GitHub authorization URL with proper parameters
    """
    # Generate a random state parameter for CSRF protection
    state = secrets.token_urlsafe(32)
    oauth_states[state] = True
    
    # GitHub OAuth parameters
    params = {
        "client_id": GITHUB_CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": GITHUB_SCOPES,
        "state": state,
        "allow_signup": "true"
    }
    
    # Construct authorization URL
    base_url = "https://github.com/login/oauth/authorize"
    query_string = urllib.parse.urlencode(params)
    
    return f"{base_url}?{query_string}"

async def handle_github_callback(code: str, state: str = None) -> dict:
    """
    Handle GitHub OAuth callback and exchange code for access token
    
    Args:
        code: Authorization code from GitHub
        state: State parameter for CSRF protection
        
    Returns:
        dict: User data including username and access token
        
    Raises:
        HTTPException: If authentication fails
    """
    # Verify state parameter (CSRF protection)
    if state and state not in oauth_states:
        raise HTTPException(
            status_code=400,
            detail="Invalid state parameter"
        )
    
    # Clean up used state
    if state:
        oauth_states.pop(state, None)
    
    # Exchange code for access token
    token_data = await exchange_code_for_token(code)
    access_token = token_data["access_token"]
    
    # Get user information from GitHub API
    user_info = await get_github_user_info(access_token)
    
    # Store user session (in production, use proper session management)
    username = user_info["login"]
    user_sessions[username] = {
        "username": username,
        "access_token": access_token,
        "user_info": user_info
    }
    
    return {
        "username": username,
        "access_token": access_token,
        "user_info": user_info
    }

async def exchange_code_for_token(code: str) -> dict:
    """
    Exchange authorization code for access token
    
    Args:
        code: Authorization code from GitHub
        
    Returns:
        dict: Token response from GitHub
        
    Raises:
        HTTPException: If token exchange fails
    """
    token_url = "https://github.com/login/oauth/access_token"
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    data = {
        "client_id": GITHUB_CLIENT_ID,
        "client_secret": GITHUB_CLIENT_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI
    }
    
    try:
        response = requests.post(token_url, headers=headers, json=data)
        response.raise_for_status()
        
        token_data = response.json()
        
        if "error" in token_data:
            raise HTTPException(
                status_code=400,
                detail=f"GitHub OAuth error: {token_data.get('error_description', 'Unknown error')}"
            )
        
        return token_data
        
    except requests.RequestException as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to exchange code for token: {str(e)}"
        )

async def get_github_user_info(access_token: str) -> dict:
    """
    Get user information from GitHub API
    
    Args:
        access_token: GitHub access token
        
    Returns:
        dict: User information from GitHub
        
    Raises:
        HTTPException: If API request fails
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        response = requests.get("https://api.github.com/user", headers=headers)
        response.raise_for_status()
        return response.json()
        
    except requests.RequestException as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to get user info: {str(e)}"
        )

async def get_current_user(token: str = Depends(security)) -> dict:
    """
    Dependency to get current authenticated user
    
    Args:
        token: Bearer token from request header
        
    Returns:
        dict: Current user data
        
    Raises:
        HTTPException: If user is not authenticated
    """
    # In a real application, you'd validate the JWT token here
    # For now, we'll use a simple session lookup
    
    # Extract token from "Bearer <token>" format
    access_token = token.credentials
    
    # Find user by access token (inefficient, use proper session management in production)
    for username, user_data in user_sessions.items():
        if user_data.get("access_token") == access_token:
            return user_data
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

def get_user_by_username(username: str) -> Optional[dict]:
    """
    Get user data by username
    
    Args:
        username: GitHub username
        
    Returns:
        dict or None: User data if found
    """
    return user_sessions.get(username)
