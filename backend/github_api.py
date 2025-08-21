"""
GitHub API Integration Module

Handles GitHub repository operations:
1. Create repositories
2. Upload files to repositories
3. Manage repository settings
4. Push generated portfolio files

This module will be extended to push the AI-generated portfolio files
to the user's GitHub repository.
"""

import requests
from fastapi import HTTPException
from typing import Dict, Any, Optional

class GitHubAPI:
    """GitHub API client for repository operations"""
    
    BASE_URL = "https://api.github.com"
    
    def __init__(self, access_token: str):
        """
        Initialize GitHub API client
        
        Args:
            access_token: GitHub OAuth access token
        """
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        }
    
    async def create_repo(self, repo_name: str, description: str = None, private: bool = False) -> dict:
        """
        Create a new repository in user's GitHub account
        
        Args:
            repo_name: Name of the repository
            description: Repository description
            private: Whether the repository should be private
            
        Returns:
            dict: Repository information from GitHub API
            
        Raises:
            HTTPException: If repository creation fails
        """
        url = f"{self.BASE_URL}/user/repos"
        
        data = {
            "name": repo_name,
            "description": description or f"AI-generated portfolio website for {repo_name}",
            "private": private,
            "auto_init": True,  # Initialize with README
            "gitignore_template": "Node",  # For web projects
            "license_template": "mit"
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            
            repo_data = response.json()
            return {
                "name": repo_data["name"],
                "full_name": repo_data["full_name"],
                "html_url": repo_data["html_url"],
                "clone_url": repo_data["clone_url"],
                "ssh_url": repo_data["ssh_url"],
                "default_branch": repo_data["default_branch"]
            }
            
        except requests.RequestException as e:
            if hasattr(e, 'response') and e.response is not None:
                error_data = e.response.json() if e.response.content else {}
                error_message = error_data.get("message", str(e))
            else:
                error_message = str(e)
            
            raise HTTPException(
                status_code=400,
                detail=f"Failed to create repository: {error_message}"
            )
    
    async def upload_file(self, repo_name: str, file_path: str, content: str, commit_message: str = None) -> dict:
        """
        Upload a file to the repository
        
        Args:
            repo_name: Repository name (owner/repo)
            file_path: Path where file should be created in repo
            content: File content (base64 encoded for binary files)
            commit_message: Commit message
            
        Returns:
            dict: Upload response from GitHub API
            
        Note:
            This will be used to push AI-generated portfolio files
        """
        import base64
        
        url = f"{self.BASE_URL}/repos/{repo_name}/contents/{file_path}"
        
        # Encode content to base64
        encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        
        data = {
            "message": commit_message or f"Add {file_path}",
            "content": encoded_content
        }
        
        try:
            response = requests.put(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to upload file: {str(e)}"
            )
    
    async def update_file(self, repo_name: str, file_path: str, content: str, sha: str, commit_message: str = None) -> dict:
        """
        Update an existing file in the repository
        
        Args:
            repo_name: Repository name (owner/repo)
            file_path: Path to the file in repo
            content: New file content
            sha: SHA of the file being replaced
            commit_message: Commit message
            
        Returns:
            dict: Update response from GitHub API
        """
        import base64
        
        url = f"{self.BASE_URL}/repos/{repo_name}/contents/{file_path}"
        
        encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        
        data = {
            "message": commit_message or f"Update {file_path}",
            "content": encoded_content,
            "sha": sha
        }
        
        try:
            response = requests.put(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to update file: {str(e)}"
            )
    
    async def get_file_content(self, repo_name: str, file_path: str) -> dict:
        """
        Get file content from repository
        
        Args:
            repo_name: Repository name (owner/repo)  
            file_path: Path to the file in repo
            
        Returns:
            dict: File information including content and SHA
        """
        url = f"{self.BASE_URL}/repos/{repo_name}/contents/{file_path}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            raise HTTPException(
                status_code=404,
                detail=f"File not found: {str(e)}"
            )

async def create_repository(access_token: str, repo_name: str, description: str = None) -> dict:
    """
    Create a new GitHub repository
    
    Args:
        access_token: GitHub OAuth access token
        repo_name: Name of the repository to create
        description: Optional repository description
        
    Returns:
        dict: Repository information
        
    Raises:
        HTTPException: If repository creation fails
    """
    github_client = GitHubAPI(access_token)
    return await github_client.create_repo(repo_name, description)

async def push_portfolio_files(access_token: str, repo_name: str, portfolio_files: Dict[str, str]) -> dict:
    """
    Push AI-generated portfolio files to GitHub repository
    
    Args:
        access_token: GitHub OAuth access token
        repo_name: Repository name (owner/repo format)
        portfolio_files: Dictionary mapping file paths to content
        
    Returns:
        dict: Results of file uploads
        
    Note:
        This function will be called after AI agent generates the portfolio
        TODO: Integrate with AI agent output
    """
    github_client = GitHubAPI(access_token)
    results = {}
    
    for file_path, content in portfolio_files.items():
        try:
            result = await github_client.upload_file(
                repo_name=repo_name,
                file_path=file_path,
                content=content,
                commit_message=f"Add AI-generated {file_path}"
            )
            results[file_path] = {"status": "success", "data": result}
        except Exception as e:
            results[file_path] = {"status": "error", "error": str(e)}
    
    return results

async def setup_github_pages(access_token: str, repo_name: str) -> dict:
    """
    Enable GitHub Pages for the repository
    
    Args:
        access_token: GitHub OAuth access token
        repo_name: Repository name (owner/repo format)
        
    Returns:
        dict: GitHub Pages configuration
        
    Note:
        This will be used to automatically deploy the generated portfolio
        TODO: Integrate with portfolio generation workflow
    """
    github_client = GitHubAPI(access_token)
    
    url = f"{github_client.BASE_URL}/repos/{repo_name}/pages"
    
    data = {
        "source": {
            "branch": "main",
            "path": "/"
        }
    }
    
    try:
        response = requests.post(url, headers=github_client.headers, json=data)
        response.raise_for_status()
        return response.json()
        
    except requests.RequestException as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to setup GitHub Pages: {str(e)}"
        )
