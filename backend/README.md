# AI Portfolio Generator Backend

FastAPI backend for generating AI-powered portfolio websites with GitHub integration.

## Features

- ✅ GitHub OAuth authentication flow
- ✅ Repository creation in user's GitHub account
- ✅ RESTful API endpoints
- 🚧 AI portfolio generation (stub implemented)
- 🚧 PDF parsing integration (placeholder)
- 🚧 LLM content generation (placeholder)

## Project Structure

```
backend/
├── main.py           # FastAPI application entry point
├── auth.py           # GitHub OAuth authentication logic
├── github_api.py     # GitHub API integration for repo operations
├── ai_agent.py       # AI portfolio generation agent (stub)
├── requirements.txt  # Python dependencies
├── .env.example      # Environment variables template
└── README.md         # This file
```

## Setup Instructions

1. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables**

   ```bash
   copy .env.example .env
   # Edit .env with your GitHub OAuth credentials
   ```

3. **Create GitHub OAuth App**

   - Go to GitHub Settings > Developer settings > OAuth Apps
   - Create a new OAuth App with:
     - Application name: AI Portfolio Generator
     - Homepage URL: http://localhost:8000
     - Authorization callback URL: http://localhost:8000/auth/callback
   - Copy Client ID and Client Secret to your .env file

4. **Run the Application**

   ```bash
   python main.py
   ```

   Or using uvicorn directly:

   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## API Endpoints

### Authentication

- `GET /login/github` - Redirect to GitHub OAuth
- `GET /auth/callback` - Handle OAuth callback

### Repository Management

- `POST /create_repo` - Create GitHub repository
  ```json
  {
    "name": "my-portfolio"
  }
  ```

### AI Portfolio Generation

- `POST /generate_portfolio` - Generate AI portfolio (stub)
  ```json
  {
    "name": "John Doe",
    "email": "john@example.com",
    "template": "modern"
  }
  ```

## Integration Points

### PDF Parsing Module (TODO)

Location: `ai_agent.py > parse_student_documents()`

- Extract student information from uploaded PDFs
- Parse education, skills, projects, experience
- Structure data for content generation

### LLM Agent Integration (TODO)

Location: `ai_agent.py > generate_portfolio_content()`

- Generate personalized bio and descriptions
- Create compelling project narratives
- Optimize content for professional presentation
- Suggested APIs: OpenAI GPT, Anthropic Claude

### Template System (TODO)

Location: `ai_agent.py > apply_portfolio_template()`

- Professional responsive HTML/CSS templates
- Multiple theme options (modern, classic, creative)
- SEO optimization and accessibility features
- Mobile-first responsive design

## Testing

Test the GitHub OAuth flow:

1. Start the server: `python main.py`
2. Visit: http://localhost:8000/login/github
3. Complete GitHub OAuth flow
4. Test repository creation via API

## Production Considerations

- Replace in-memory session storage with database
- Implement proper JWT token management
- Add rate limiting and security headers
- Set up environment-specific configurations
- Configure CORS properly for frontend domain
- Add comprehensive error handling and logging

## Next Steps

1. Integrate PDF parsing library (PyPDF2, pdfplumber, or similar)
2. Connect LLM API for content generation
3. Implement professional portfolio templates
4. Add file upload handling for student documents
5. Create comprehensive test suite
6. Set up GitHub Actions for deployment
