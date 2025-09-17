"""
FastAPI application for Google Sheets ID extraction.
This API provides endpoints to extract Google Sheets document IDs and sheet IDs from URLs.
"""

from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from typing import Dict, Any, Optional, List
import re
import os
from datetime import datetime
from security import (
    security, 
    sanitize_input_text, 
    create_secure_response_headers,
    check_rate_limit
)

# Initialize FastAPI app
app = FastAPI(
    title="Google Sheets ID Extraction API",
    description="A production-ready API for extracting Google Sheets document IDs and sheet IDs from URLs",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Environment variables
API_TOKEN = os.getenv("API_TOKEN", "your-secret-token-here")

# Pydantic models
class SheetsExtractionRequest(BaseModel):
    """Request model for Google Sheets ID extraction."""
    url: str = Field(..., description="The Google Sheets URL or document ID to extract from", min_length=1, max_length=2048)
    
    @field_validator('url')
    @classmethod
    def validate_url(cls, v):
        """Validate and sanitize input URL."""
        return sanitize_input_text(v)

class SheetsExtractionResponse(BaseModel):
    """Response model for extracted Google Sheets IDs."""
    success: bool = Field(..., description="Whether the extraction was successful")
    document_id: Optional[str] = Field(None, description="The Google Sheets document ID")
    sheet_ids: List[str] = Field(default_factory=list, description="List of individual sheet IDs found in the URL")
    original_url: str = Field(..., description="The original input URL")
    timestamp: str = Field(..., description="ISO timestamp of when extraction was performed")
    url_type: str = Field(..., description="Type of URL processed (full_url, document_id, or invalid)")

class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str = Field(..., description="API status")
    timestamp: str = Field(..., description="Current timestamp")
    version: str = Field(..., description="API version")

# Authentication dependency
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify the API token."""
    if credentials.credentials != API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials

# Google Sheets ID extraction functions
def extract_document_id(url: str) -> Optional[str]:
    """
    Extract the Google Sheets document ID from a URL or return the ID if it's already clean.
    
    Args:
        url: Google Sheets URL or document ID
        
    Returns:
        Document ID if found, None otherwise
    """
    if not url or not isinstance(url, str):
        return None
    
    # Step 1: Try to extract the ID from a URL pattern.
    # This pattern looks for a string of valid characters that comes after "/spreadsheets/d/".
    url_pattern = r'spreadsheets/d/([a-zA-Z0-9-_]+)'
    match = re.search(url_pattern, url)
    
    if match:
        # The ID is in the first capturing group.
        return match.group(1)

    # Step 2: If no URL pattern matches, assume the input is the ID itself.
    # Validate it to make sure it looks like a plausible ID.
    # This pattern checks for valid characters and a reasonable length (25-50 chars).
    id_pattern = r'^[a-zA-Z0-9-_]{25,50}$'
    if re.match(id_pattern, url.strip()):
        return url.strip()

    # If neither pattern matches, return None.
    return None

def extract_sheet_ids(url: str) -> List[str]:
    """
    Extract individual sheet IDs (gid parameters) from a Google Sheets URL.
    
    Args:
        url: Google Sheets URL
        
    Returns:
        List of sheet IDs found in the URL
    """
    sheet_ids = []
    
    # Pattern to match gid parameters
    gid_patterns = [
        r'gid=(\d+)',  # Standard gid parameter
        r'#gid=(\d+)',  # Fragment gid parameter
    ]
    
    for pattern in gid_patterns:
        matches = re.findall(pattern, url)
        sheet_ids.extend(matches)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_sheet_ids = []
    for sheet_id in sheet_ids:
        if sheet_id not in seen:
            seen.add(sheet_id)
            unique_sheet_ids.append(sheet_id)
    
    return unique_sheet_ids

def determine_url_type(url: str, document_id: Optional[str], sheet_ids: List[str]) -> str:
    """
    Determine the type of URL that was processed.
    
    Args:
        url: Original URL input
        document_id: Extracted document ID
        sheet_ids: Extracted sheet IDs
        
    Returns:
        URL type classification
    """
    if not document_id:
        return "invalid"
    
    # Check if it's already a clean document ID (25-50 characters, valid pattern)
    if re.match(r'^[a-zA-Z0-9-_]{25,50}$', url.strip()):
        return "document_id"
    
    # Check if it contains Google Sheets URL patterns
    if 'docs.google.com/spreadsheets' in url or 'spreadsheets/d/' in url:
        if sheet_ids:
            return "full_url_with_sheets"
        else:
            return "full_url"
    
    return "partial_url"

def extract_sheets_info(url: str) -> Dict[str, Any]:
    """
    Extract all Google Sheets information from a URL or document ID.
    
    Args:
        url: Google Sheets URL or document ID
        
    Returns:
        Dictionary containing extracted information
    """
    document_id = extract_document_id(url)
    sheet_ids = extract_sheet_ids(url)
    url_type = determine_url_type(url, document_id, sheet_ids)
    
    return {
        "document_id": document_id,
        "sheet_ids": sheet_ids,
        "url_type": url_type
    }

# API Routes
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses."""
    response = await call_next(request)
    
    # Add security headers
    security_headers = create_secure_response_headers()
    for header, value in security_headers.items():
        response.headers[header] = value
    
    return response

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0"
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0"
    )

@app.post("/extract", response_model=SheetsExtractionResponse)
async def extract_sheets_ids(
    request: SheetsExtractionRequest,
    http_request: Request,
    token: str = Depends(verify_token)
):
    """
    Extract Google Sheets document ID and sheet IDs from a URL.
    
    - **url**: The Google Sheets URL or document ID to extract from
    
    Returns structured JSON with extracted Google Sheets information.
    
    **Supported URL formats:**
    - Full URL: `https://docs.google.com/spreadsheets/d/12itafHpvKAvPWUWl9XWtNJfG9T4kMw0sxqz9MFv0Xdk/edit?gid=1058109381#gid=1058109381`
    - Document ID only: `12itafHpvKAvPWUWl9XWtNJfG9T4kMw0sxqz9MFv0Xdk`
    - Partial URL: `spreadsheets/d/12itafHpvKAvPWUWl9XWtNJfG9T4kMw0sxqz9MFv0Xdk`
    """
    try:
        # Rate limiting is handled in the security module via the SecureHTTPBearer
        
        extracted_info = extract_sheets_info(request.url)
        
        return SheetsExtractionResponse(
            success=extracted_info["document_id"] is not None,
            document_id=extracted_info["document_id"],
            sheet_ids=extracted_info["sheet_ids"],
            original_url=request.url,
            url_type=extracted_info["url_type"],
            timestamp=datetime.utcnow().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Extraction failed: {str(e)}"
        )

# For local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

