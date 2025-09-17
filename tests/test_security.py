"""
Security-specific tests for the Data Extraction API.
Tests input sanitization, rate limiting, and security headers.
"""

import pytest
from fastapi.testclient import TestClient
from main import app
from security import sanitize_input_text, validate_extraction_type, SimpleRateLimiter
import time

class TestInputSanitization:
    """Test input sanitization functions."""
    
    def test_sanitize_normal_text(self):
        """Test sanitization of normal text."""
        text = "Contact john@example.com for more info"
        result = sanitize_input_text(text)
        assert result == text
    
    def test_sanitize_html_content(self):
        """Test sanitization of HTML content."""
        text = "Contact <script>alert('xss')</script> john@example.com"
        result = sanitize_input_text(text)
        # HTML should be escaped, not completely removed
        assert "&lt;script&gt;" in result  # HTML escaped
        assert "&lt;/script&gt;" in result  # HTML escaped
        assert "john@example.com" in result
    
    def test_sanitize_javascript_url(self):
        """Test sanitization of JavaScript URLs."""
        text = "Visit javascript:alert('xss') for more info"
        result = sanitize_input_text(text)
        assert "javascript:" not in result
    
    def test_sanitize_html_escape(self):
        """Test HTML escaping."""
        text = "Price: $100 < $200 & tax > 5%"
        result = sanitize_input_text(text)
        assert "&lt;" in result
        assert "&gt;" in result
        assert "&amp;" in result
    
    def test_sanitize_whitespace_normalization(self):
        """Test whitespace normalization."""
        text = "Contact   john@example.com\n\n\tfor   more    info"
        result = sanitize_input_text(text)
        assert "  " not in result  # No double spaces
        assert "\n" not in result
        assert "\t" not in result
    
    def test_sanitize_empty_text_error(self):
        """Test error handling for empty text."""
        with pytest.raises(Exception):  # Should raise HTTPException
            sanitize_input_text("")
    
    def test_sanitize_none_text_error(self):
        """Test error handling for None text."""
        with pytest.raises(Exception):  # Should raise HTTPException
            sanitize_input_text(None)

class TestExtractionTypeValidation:
    """Test extraction type validation."""
    
    def test_valid_extraction_types(self):
        """Test validation of valid extraction types."""
        valid_types = ["email_phone", "dates", "numbers", "urls", "all"]
        for extraction_type in valid_types:
            result = validate_extraction_type(extraction_type)
            assert result == extraction_type
    
    def test_case_insensitive_validation(self):
        """Test case-insensitive validation."""
        result = validate_extraction_type("EMAIL_PHONE")
        assert result == "email_phone"
    
    def test_whitespace_handling(self):
        """Test whitespace handling in extraction type."""
        result = validate_extraction_type("  dates  ")
        assert result == "dates"
    
    def test_invalid_extraction_type(self):
        """Test error handling for invalid extraction type."""
        with pytest.raises(Exception):  # Should raise HTTPException
            validate_extraction_type("invalid_type")
    
    def test_empty_extraction_type_default(self):
        """Test default value for empty extraction type."""
        result = validate_extraction_type("")
        assert result == "email_phone"
    
    def test_none_extraction_type_default(self):
        """Test default value for None extraction type."""
        result = validate_extraction_type(None)
        assert result == "email_phone"

class TestRateLimiting:
    """Test rate limiting functionality."""
    
    def test_rate_limiter_allows_requests_under_limit(self):
        """Test that rate limiter allows requests under the limit."""
        limiter = SimpleRateLimiter(max_requests=5, window_seconds=60)
        client_id = "test_client_1"
        
        # Should allow first 5 requests
        for i in range(5):
            assert limiter.is_allowed(client_id) is True
    
    def test_rate_limiter_blocks_requests_over_limit(self):
        """Test that rate limiter blocks requests over the limit."""
        limiter = SimpleRateLimiter(max_requests=3, window_seconds=60)
        client_id = "test_client_2"
        
        # Allow first 3 requests
        for i in range(3):
            assert limiter.is_allowed(client_id) is True
        
        # Block 4th request
        assert limiter.is_allowed(client_id) is False
    
    def test_rate_limiter_window_reset(self):
        """Test that rate limiter resets after window expires."""
        limiter = SimpleRateLimiter(max_requests=2, window_seconds=1)
        client_id = "test_client_3"
        
        # Use up the limit
        assert limiter.is_allowed(client_id) is True
        assert limiter.is_allowed(client_id) is True
        assert limiter.is_allowed(client_id) is False
        
        # Wait for window to expire
        time.sleep(1.1)
        
        # Should allow requests again
        assert limiter.is_allowed(client_id) is True
    
    def test_rate_limiter_different_clients(self):
        """Test that rate limiter tracks different clients separately."""
        limiter = SimpleRateLimiter(max_requests=2, window_seconds=60)
        
        # Client 1 uses up their limit
        assert limiter.is_allowed("client_1") is True
        assert limiter.is_allowed("client_1") is True
        assert limiter.is_allowed("client_1") is False
        
        # Client 2 should still be allowed
        assert limiter.is_allowed("client_2") is True
        assert limiter.is_allowed("client_2") is True

class TestSecurityHeaders:
    """Test security headers in API responses."""
    
    def test_security_headers_in_health_endpoint(self):
        """Test that security headers are present in health endpoint."""
        client = TestClient(app)
        response = client.get("/health")
        
        # Check for important security headers
        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        
        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Frame-Options"] == "DENY"
        
        assert "X-XSS-Protection" in response.headers
        assert "Strict-Transport-Security" in response.headers
        assert "Content-Security-Policy" in response.headers
    
    def test_security_headers_in_extract_endpoint(self):
        """Test that security headers are present in extract endpoint."""
        client = TestClient(app)
        headers = {"Authorization": "Bearer your-secret-token-here"}
        payload = {"text": "test@example.com", "extraction_type": "email_phone"}
        
        response = client.post("/extract", json=payload, headers=headers)
        
        # Check for security headers
        assert "X-Content-Type-Options" in response.headers
        assert "Cache-Control" in response.headers
        assert "no-cache" in response.headers["Cache-Control"]

class TestSecurityIntegration:
    """Test security features integration with the API."""
    
    def test_malicious_input_sanitization(self):
        """Test that malicious input is properly sanitized."""
        client = TestClient(app)
        headers = {"Authorization": "Bearer your-secret-token-here"}
        
        # Attempt XSS injection in URL
        malicious_url = "https://docs.google.com/spreadsheets/d/12itafHpvKAvPWUWl9XWtNJfG9T4kMw0sxqz9MFv0Xdk/edit?<script>alert('xss')</script>"
        payload = {"url": malicious_url}
        
        response = client.post("/extract", json=payload, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        # The original URL should be sanitized
        assert "<script>" not in data["original_url"]
        # Should still extract the document ID
        assert data["document_id"] == "12itafHpvKAvPWUWl9XWtNJfG9T4kMw0sxqz9MFv0Xdk"
    
    def test_oversized_input_rejection(self):
        """Test that oversized input is rejected."""
        client = TestClient(app)
        headers = {"Authorization": "Bearer your-secret-token-here"}
        
        # Create a very large URL input
        large_url = "https://docs.google.com/spreadsheets/d/12itafHpvKAvPWUWl9XWtNJfG9T4kMw0sxqz9MFv0Xdk/edit?" + "a" * (2048 + 1)  # Exceed max size
        payload = {"url": large_url}
        
        response = client.post("/extract", json=payload, headers=headers)
        assert response.status_code == 422  # Validation error
    
    def test_invalid_json_handling(self):
        """Test handling of invalid JSON input."""
        client = TestClient(app)
        headers = {
            "Authorization": "Bearer your-secret-token-here",
            "Content-Type": "application/json"
        }
        
        # Send invalid JSON
        response = client.post("/extract", data="invalid json", headers=headers)
        assert response.status_code == 422

