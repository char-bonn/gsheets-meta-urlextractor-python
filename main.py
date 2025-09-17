"""
FastAPI application for data extraction from strings.
This API provides endpoints to extract specific data from text strings and return structured JSON responses.
"""

from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from typing import Dict, Any, Optional
import re
import os
from datetime import datetime
from security import (
    security, 
    sanitize_input_text, 
    validate_extraction_type, 
    create_secure_response_headers,
    check_rate_limit
)

# Initialize FastAPI app
app = FastAPI(
    title="Data Extraction API",
    description="A production-ready API for extracting structured data from text strings",
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
class ExtractionRequest(BaseModel):
    """Request model for data extraction."""
    text: str = Field(..., description="The text string to extract data from", min_length=1, max_length=1048576)
    extraction_type: str = Field(
        default="email_phone", 
        description="Type of extraction to perform",
        pattern="^(email_phone|dates|numbers|urls|all)$"
    )
    
    @field_validator('text')
    @classmethod
    def validate_text(cls, v):
        """Validate and sanitize input text."""
        return sanitize_input_text(v)
    
    @field_validator('extraction_type')
    @classmethod
    def validate_extraction_type(cls, v):
        """Validate extraction type."""
        return validate_extraction_type(v)

class ExtractionResponse(BaseModel):
    """Response model for extracted data."""
    success: bool = Field(..., description="Whether the extraction was successful")
    extracted_data: Dict[str, Any] = Field(..., description="The extracted data organized by type")
    original_text: str = Field(..., description="The original input text")
    extraction_type: str = Field(..., description="The type of extraction performed")
    timestamp: str = Field(..., description="ISO timestamp of when extraction was performed")

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

# Data extraction functions
def extract_emails(text: str) -> list:
    """Extract email addresses from text."""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.findall(email_pattern, text)

def extract_phone_numbers(text: str) -> list:
    """Extract phone numbers from text."""
    # Pattern for various phone number formats
    phone_patterns = [
        r'\b\d{3}-\d{3}-\d{4}\b',  # 123-456-7890
        r'\(\d{3}\)\s*\d{3}-\d{4}',  # (123) 456-7890
        r'\b\d{3}\.\d{3}\.\d{4}\b',  # 123.456.7890
        r'\b\d{10}\b',  # 1234567890
        r'\+\d{1,3}[\s-]?\d{3,4}[\s-]?\d{3,4}[\s-]?\d{4}',  # +1 123 456 7890
        r'\b\d{3}\s+\d{3}\s+\d{4}\b',  # 123 456 7890
    ]
    
    phone_numbers = []
    for pattern in phone_patterns:
        matches = re.findall(pattern, text)
        phone_numbers.extend(matches)
    
    return list(set(phone_numbers))  # Remove duplicates

def extract_dates(text: str) -> list:
    """Extract dates from text."""
    date_patterns = [
        r'\b\d{1,2}/\d{1,2}/\d{4}\b',  # MM/DD/YYYY or M/D/YYYY
        r'\b\d{1,2}-\d{1,2}-\d{4}\b',  # MM-DD-YYYY or M-D-YYYY
        r'\b\d{4}-\d{1,2}-\d{1,2}\b',  # YYYY-MM-DD or YYYY-M-D
        r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b',  # Month DD, YYYY
    ]
    
    dates = []
    for pattern in date_patterns:
        dates.extend(re.findall(pattern, text, re.IGNORECASE))
    
    return list(set(dates))

def extract_numbers(text: str) -> list:
    """Extract numbers from text."""
    number_pattern = r'\b\d+(?:\.\d+)?\b'
    return re.findall(number_pattern, text)

def extract_urls(text: str) -> list:
    """Extract URLs from text."""
    url_pattern = r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?'
    return re.findall(url_pattern, text)

def perform_extraction(text: str, extraction_type: str) -> Dict[str, Any]:
    """Perform the specified type of data extraction."""
    extracted_data = {}
    
    if extraction_type == "email_phone":
        extracted_data["emails"] = extract_emails(text)
        extracted_data["phone_numbers"] = extract_phone_numbers(text)
    elif extraction_type == "dates":
        extracted_data["dates"] = extract_dates(text)
    elif extraction_type == "numbers":
        extracted_data["numbers"] = extract_numbers(text)
    elif extraction_type == "urls":
        extracted_data["urls"] = extract_urls(text)
    elif extraction_type == "all":
        extracted_data["emails"] = extract_emails(text)
        extracted_data["phone_numbers"] = extract_phone_numbers(text)
        extracted_data["dates"] = extract_dates(text)
        extracted_data["numbers"] = extract_numbers(text)
        extracted_data["urls"] = extract_urls(text)
    
    return extracted_data

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

@app.post("/extract", response_model=ExtractionResponse)
async def extract_data(
    request: ExtractionRequest,
    http_request: Request,
    token: str = Depends(verify_token)
):
    """
    Extract structured data from the provided text string.
    
    - **text**: The input text to extract data from
    - **extraction_type**: Type of extraction (email_phone, dates, numbers, urls, all)
    
    Returns structured JSON with extracted data organized by type.
    """
    try:
        # Rate limiting is handled in the security module via the SecureHTTPBearer
        
        extracted_data = perform_extraction(request.text, request.extraction_type)
        
        return ExtractionResponse(
            success=True,
            extracted_data=extracted_data,
            original_text=request.text,
            extraction_type=request.extraction_type,
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

