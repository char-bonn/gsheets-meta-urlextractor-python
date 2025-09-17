"""
Comprehensive test suite for the Data Extraction API.
Tests cover all endpoints, extraction functions, authentication, and edge cases.
"""

import pytest
from fastapi.testclient import TestClient
from main import (
    app, 
    extract_emails, 
    extract_phone_numbers, 
    extract_dates, 
    extract_numbers, 
    extract_urls,
    perform_extraction
)
import json

class TestHealthEndpoints:
    """Test health check endpoints."""
    
    def test_root_endpoint(self, client):
        """Test the root endpoint returns health status."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["version"] == "1.0.0"
    
    def test_health_endpoint(self, client):
        """Test the dedicated health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["version"] == "1.0.0"

class TestAuthentication:
    """Test API authentication mechanisms."""
    
    def test_extract_with_valid_token(self, client, auth_headers):
        """Test extraction endpoint with valid authentication."""
        payload = {
            "text": "Contact john@example.com",
            "extraction_type": "email_phone"
        }
        response = client.post("/extract", json=payload, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_extract_with_invalid_token(self, client, invalid_auth_headers):
        """Test extraction endpoint with invalid authentication."""
        payload = {
            "text": "Contact john@example.com",
            "extraction_type": "email_phone"
        }
        response = client.post("/extract", json=payload, headers=invalid_auth_headers)
        assert response.status_code == 401
        data = response.json()
        assert "Invalid authentication token" in data["detail"]
    
    def test_extract_without_token(self, client):
        """Test extraction endpoint without authentication."""
        payload = {
            "text": "Contact john@example.com",
            "extraction_type": "email_phone"
        }
        response = client.post("/extract", json=payload)
        assert response.status_code == 403

class TestExtractionFunctions:
    """Test individual extraction functions."""
    
    def test_extract_emails(self):
        """Test email extraction function."""
        text = "Contact john@example.com and jane.doe@company.org for more info"
        emails = extract_emails(text)
        assert "john@example.com" in emails
        assert "jane.doe@company.org" in emails
        assert len(emails) == 2
    
    def test_extract_emails_no_matches(self):
        """Test email extraction with no email addresses."""
        text = "No email addresses in this text"
        emails = extract_emails(text)
        assert emails == []
    
    def test_extract_phone_numbers(self):
        """Test phone number extraction function."""
        text = "Call (555) 123-4567 or 555-987-6543 or +1 800 555 0199"
        phones = extract_phone_numbers(text)
        assert "(555) 123-4567" in phones
        assert "555-987-6543" in phones
        assert "+1 800 555 0199" in phones
    
    def test_extract_phone_numbers_various_formats(self):
        """Test phone number extraction with various formats."""
        test_cases = [
            ("Call 555.123.4567", ["555.123.4567"]),
            ("Phone: 5551234567", ["5551234567"]),
            ("Contact (555) 123-4567", ["(555) 123-4567"]),
            ("Call 555 123 4567", ["555 123 4567"])
        ]
        
        for text, expected in test_cases:
            phones = extract_phone_numbers(text)
            for expected_phone in expected:
                assert expected_phone in phones
    
    def test_extract_dates(self):
        """Test date extraction function."""
        text = "Meeting on 12/25/2023, follow-up on 2024-01-15, and party on Jan 1, 2024"
        dates = extract_dates(text)
        assert "12/25/2023" in dates
        assert "2024-01-15" in dates
        assert "Jan 1, 2024" in dates
    
    def test_extract_numbers(self):
        """Test number extraction function."""
        text = "The price is $29.99 for 5 items, total 149.95"
        numbers = extract_numbers(text)
        assert "29.99" in numbers
        assert "5" in numbers
        assert "149.95" in numbers
    
    def test_extract_urls(self):
        """Test URL extraction function."""
        text = "Visit https://example.com or http://test.org for more info"
        urls = extract_urls(text)
        assert "https://example.com" in urls
        assert "http://test.org" in urls

class TestExtractionEndpoint:
    """Test the main extraction endpoint."""
    
    def test_email_phone_extraction(self, client, auth_headers):
        """Test email and phone extraction."""
        payload = {
            "text": "Contact john@example.com or call (555) 123-4567",
            "extraction_type": "email_phone"
        }
        response = client.post("/extract", json=payload, headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "john@example.com" in data["extracted_data"]["emails"]
        assert "(555) 123-4567" in data["extracted_data"]["phone_numbers"]
        assert data["extraction_type"] == "email_phone"
        assert data["original_text"] == payload["text"]
    
    def test_dates_extraction(self, client, auth_headers):
        """Test date extraction."""
        payload = {
            "text": "Meeting on 12/25/2023 and follow-up on Jan 15, 2024",
            "extraction_type": "dates"
        }
        response = client.post("/extract", json=payload, headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "dates" in data["extracted_data"]
        assert len(data["extracted_data"]["dates"]) >= 1
    
    def test_numbers_extraction(self, client, auth_headers):
        """Test number extraction."""
        payload = {
            "text": "The price is $29.99 and quantity is 5 items",
            "extraction_type": "numbers"
        }
        response = client.post("/extract", json=payload, headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "numbers" in data["extracted_data"]
        assert len(data["extracted_data"]["numbers"]) >= 2
    
    def test_urls_extraction(self, client, auth_headers):
        """Test URL extraction."""
        payload = {
            "text": "Visit https://example.com or http://test.org",
            "extraction_type": "urls"
        }
        response = client.post("/extract", json=payload, headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "urls" in data["extracted_data"]
        assert "https://example.com" in data["extracted_data"]["urls"]
        assert "http://test.org" in data["extracted_data"]["urls"]
    
    def test_all_extraction(self, client, auth_headers):
        """Test extraction of all data types."""
        payload = {
            "text": "Email support@company.com, call 555-123-4567, visit https://company.com on 01/01/2024",
            "extraction_type": "all"
        }
        response = client.post("/extract", json=payload, headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        extracted = data["extracted_data"]
        
        # Check that all extraction types are present
        assert "emails" in extracted
        assert "phone_numbers" in extracted
        assert "dates" in extracted
        assert "numbers" in extracted
        assert "urls" in extracted
        
        # Check specific extractions
        assert "support@company.com" in extracted["emails"]
        assert "https://company.com" in extracted["urls"]

class TestInputValidation:
    """Test input validation and error handling."""
    
    def test_empty_text(self, client, auth_headers):
        """Test extraction with empty text."""
        payload = {
            "text": "",
            "extraction_type": "email_phone"
        }
        response = client.post("/extract", json=payload, headers=auth_headers)
        assert response.status_code == 422  # Validation error
    
    def test_invalid_extraction_type(self, client, auth_headers):
        """Test extraction with invalid extraction type."""
        payload = {
            "text": "Some text",
            "extraction_type": "invalid_type"
        }
        response = client.post("/extract", json=payload, headers=auth_headers)
        assert response.status_code == 422  # Validation error
    
    def test_missing_text_field(self, client, auth_headers):
        """Test extraction with missing text field."""
        payload = {
            "extraction_type": "email_phone"
        }
        response = client.post("/extract", json=payload, headers=auth_headers)
        assert response.status_code == 422  # Validation error
    
    def test_missing_extraction_type(self, client, auth_headers):
        """Test extraction with missing extraction_type (should use default)."""
        payload = {
            "text": "Contact john@example.com"
        }
        response = client.post("/extract", json=payload, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["extraction_type"] == "email_phone"  # Default value

class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_very_long_text(self, client, auth_headers):
        """Test extraction with very long text."""
        long_text = "Contact john@example.com. " * 1000  # Very long text
        payload = {
            "text": long_text,
            "extraction_type": "email_phone"
        }
        response = client.post("/extract", json=payload, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_special_characters(self, client, auth_headers):
        """Test extraction with special characters."""
        payload = {
            "text": "Contact john+test@example.com or call (555) 123-4567! Visit https://example.com?param=value#section",
            "extraction_type": "all"
        }
        response = client.post("/extract", json=payload, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_unicode_text(self, client, auth_headers):
        """Test extraction with Unicode characters."""
        payload = {
            "text": "Contactez-nous à français@example.com ou téléphonez au (555) 123-4567",
            "extraction_type": "email_phone"
        }
        response = client.post("/extract", json=payload, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_no_matches_found(self, client, auth_headers):
        """Test extraction when no matches are found."""
        payload = {
            "text": "This text contains no extractable data",
            "extraction_type": "all"
        }
        response = client.post("/extract", json=payload, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # All extraction arrays should be empty
        extracted = data["extracted_data"]
        assert extracted["emails"] == []
        assert extracted["phone_numbers"] == []
        assert extracted["dates"] == []
        assert extracted["numbers"] == []
        assert extracted["urls"] == []

class TestResponseFormat:
    """Test response format and structure."""
    
    def test_response_structure(self, client, auth_headers):
        """Test that response has correct structure."""
        payload = {
            "text": "Contact john@example.com",
            "extraction_type": "email_phone"
        }
        response = client.post("/extract", json=payload, headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        
        # Check required fields
        required_fields = ["success", "extracted_data", "original_text", "extraction_type", "timestamp"]
        for field in required_fields:
            assert field in data
        
        # Check data types
        assert isinstance(data["success"], bool)
        assert isinstance(data["extracted_data"], dict)
        assert isinstance(data["original_text"], str)
        assert isinstance(data["extraction_type"], str)
        assert isinstance(data["timestamp"], str)
    
    def test_timestamp_format(self, client, auth_headers):
        """Test that timestamp is in ISO format."""
        payload = {
            "text": "Contact john@example.com",
            "extraction_type": "email_phone"
        }
        response = client.post("/extract", json=payload, headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        timestamp = data["timestamp"]
        
        # Basic ISO format check (should contain T and end with Z or timezone)
        assert "T" in timestamp
        assert len(timestamp) > 10  # Should be longer than just date

