"""
Comprehensive test suite for the Google Sheets ID Extraction API.
Tests cover all endpoints, extraction functions, authentication, and edge cases.
"""

import pytest
from fastapi.testclient import TestClient
from main import (
    app, 
    extract_document_id, 
    extract_sheet_ids, 
    determine_url_type,
    extract_sheets_info
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
            "url": "https://docs.google.com/spreadsheets/d/12itafHpvKAvPWUWl9XWtNJfG9T4kMw0sxqz9MFv0Xdk/edit"
        }
        response = client.post("/extract", json=payload, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_extract_with_invalid_token(self, client, invalid_auth_headers):
        """Test extraction endpoint with invalid authentication."""
        payload = {
            "url": "https://docs.google.com/spreadsheets/d/12itafHpvKAvPWUWl9XWtNJfG9T4kMw0sxqz9MFv0Xdk/edit"
        }
        response = client.post("/extract", json=payload, headers=invalid_auth_headers)
        assert response.status_code == 401
        data = response.json()
        assert "Invalid authentication token" in data["detail"]
    
    def test_extract_without_token(self, client):
        """Test extraction endpoint without authentication."""
        payload = {
            "url": "https://docs.google.com/spreadsheets/d/12itafHpvKAvPWUWl9XWtNJfG9T4kMw0sxqz9MFv0Xdk/edit"
        }
        response = client.post("/extract", json=payload)
        assert response.status_code == 403


class TestExtractionFunctions:
    """Test the core extraction functions."""
    
    def test_extract_document_id_from_full_url(self):
        """Test extracting document ID from full Google Sheets URL."""
        url = "https://docs.google.com/spreadsheets/d/12itafHpvKAvPWUWl9XWtNJfG9T4kMw0sxqz9MFv0Xdk/edit"
        result = extract_document_id(url)
        assert result == "12itafHpvKAvPWUWl9XWtNJfG9T4kMw0sxqz9MFv0Xdk"
    
    def test_extract_document_id_from_clean_id(self):
        """Test that clean document IDs are returned as-is."""
        doc_id = "12itafHpvKAvPWUWl9XWtNJfG9T4kMw0sxqz9MFv0Xdk"
        result = extract_document_id(doc_id)
        assert result == doc_id
    
    def test_extract_document_id_from_shorter_id(self):
        """Test that shorter document IDs (42 chars) are handled correctly."""
        doc_id = "1234567890abcdefghijklmnopqrstuvwxyzABCDEF"  # 42 chars
        result = extract_document_id(doc_id)
        assert result == doc_id
    
    def test_extract_document_id_from_partial_url(self):
        """Test extracting document ID from partial URL."""
        url = "docs.google.com/spreadsheets/d/12itafHpvKAvPWUWl9XWtNJfG9T4kMw0sxqz9MFv0Xdk/edit"
        result = extract_document_id(url)
        assert result == "12itafHpvKAvPWUWl9XWtNJfG9T4kMw0sxqz9MFv0Xdk"
    
    def test_extract_document_id_invalid_url(self):
        """Test that invalid URLs return None."""
        invalid_urls = [
            "https://example.com/not-a-sheets-url",
            "invalid-id-too-short",
            "this-is-way-too-long-to-be-a-valid-google-sheets-document-id-and-should-be-rejected",
            "",
            None
        ]
        for url in invalid_urls:
            result = extract_document_id(url)
            assert result is None

    def test_extract_sheet_ids_single_gid(self):
        """Test sheet ID extraction with single gid parameter."""
        url = "https://docs.google.com/spreadsheets/d/12itafHpvKAvPWUWl9XWtNJfG9T4kMw0sxqz9MFv0Xdk/edit?gid=1058109381"
        sheet_ids = extract_sheet_ids(url)
        assert sheet_ids == ["1058109381"]
    
    def test_extract_sheet_ids_multiple_gids(self):
        """Test sheet ID extraction with multiple gid parameters."""
        url = "https://docs.google.com/spreadsheets/d/12itafHpvKAvPWUWl9XWtNJfG9T4kMw0sxqz9MFv0Xdk/edit?gid=1058109381#gid=1058109381"
        sheet_ids = extract_sheet_ids(url)
        assert "1058109381" in sheet_ids
        # Should deduplicate
        assert len(sheet_ids) == 1
    
    def test_extract_sheet_ids_no_gids(self):
        """Test sheet ID extraction with no gid parameters."""
        url = "https://docs.google.com/spreadsheets/d/12itafHpvKAvPWUWl9XWtNJfG9T4kMw0sxqz9MFv0Xdk/edit"
        sheet_ids = extract_sheet_ids(url)
        assert sheet_ids == []
    
    def test_determine_url_type_full_url_with_sheets(self):
        """Test URL type determination for full URL with sheet IDs."""
        url = "https://docs.google.com/spreadsheets/d/12itafHpvKAvPWUWl9XWtNJfG9T4kMw0sxqz9MFv0Xdk/edit?gid=123"
        doc_id = "12itafHpvKAvPWUWl9XWtNJfG9T4kMw0sxqz9MFv0Xdk"
        sheet_ids = ["123"]
        url_type = determine_url_type(url, doc_id, sheet_ids)
        assert url_type == "full_url_with_sheets"
    
    def test_determine_url_type_document_id(self):
        """Test URL type determination for clean document ID."""
        url = "12itafHpvKAvPWUWl9XWtNJfG9T4kMw0sxqz9MFv0Xdk"
        doc_id = "12itafHpvKAvPWUWl9XWtNJfG9T4kMw0sxqz9MFv0Xdk"
        sheet_ids = []
        url_type = determine_url_type(url, doc_id, sheet_ids)
        assert url_type == "document_id"
    
    def test_determine_url_type_invalid(self):
        """Test URL type determination for invalid input."""
        url = "invalid-url"
        doc_id = None
        sheet_ids = []
        url_type = determine_url_type(url, doc_id, sheet_ids)
        assert url_type == "invalid"

class TestExtractionEndpoint:
    """Test the main extraction endpoint."""
    
    def test_extract_full_url_with_sheets(self, client, auth_headers):
        """Test extraction from full URL with sheet IDs."""
        payload = {
            "url": "https://docs.google.com/spreadsheets/d/12itafHpvKAvPWUWl9XWtNJfG9T4kMw0sxqz9MFv0Xdk/edit?gid=1058109381#gid=1058109381"
        }
        response = client.post("/extract", json=payload, headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["document_id"] == "12itafHpvKAvPWUWl9XWtNJfG9T4kMw0sxqz9MFv0Xdk"
        assert "1058109381" in data["sheet_ids"]
        assert data["url_type"] == "full_url_with_sheets"
        assert data["original_url"] == payload["url"]
    
    def test_extract_document_id_only(self, client, auth_headers):
        """Test extraction from document ID only."""
        payload = {
            "url": "12itafHpvKAvPWUWl9XWtNJfG9T4kMw0sxqz9MFv0Xdk"
        }
        response = client.post("/extract", json=payload, headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["document_id"] == "12itafHpvKAvPWUWl9XWtNJfG9T4kMw0sxqz9MFv0Xdk"
        assert data["sheet_ids"] == []
        assert data["url_type"] == "document_id"
    
    def test_extract_full_url_without_sheets(self, client, auth_headers):
        """Test extraction from full URL without sheet IDs."""
        payload = {
            "url": "https://docs.google.com/spreadsheets/d/12itafHpvKAvPWUWl9XWtNJfG9T4kMw0sxqz9MFv0Xdk/edit"
        }
        response = client.post("/extract", json=payload, headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["document_id"] == "12itafHpvKAvPWUWl9XWtNJfG9T4kMw0sxqz9MFv0Xdk"
        assert data["sheet_ids"] == []
        assert data["url_type"] == "full_url"
    
    def test_extract_invalid_url(self, client, auth_headers):
        """Test extraction from invalid URL."""
        payload = {
            "url": "https://example.com/not-a-sheets-url"
        }
        response = client.post("/extract", json=payload, headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is False
        assert data["document_id"] is None
        assert data["sheet_ids"] == []
        assert data["url_type"] == "invalid"

class TestInputValidation:
    """Test input validation and error handling."""
    
    def test_empty_url(self, client, auth_headers):
        """Test extraction with empty URL."""
        payload = {
            "url": ""
        }
        response = client.post("/extract", json=payload, headers=auth_headers)
        assert response.status_code == 422  # Validation error
    
    def test_missing_url_field(self, client, auth_headers):
        """Test extraction with missing URL field."""
        payload = {}
        response = client.post("/extract", json=payload, headers=auth_headers)
        assert response.status_code == 422  # Validation error
    
    def test_very_long_url(self, client, auth_headers):
        """Test extraction with very long URL."""
        long_url = "https://docs.google.com/spreadsheets/d/12itafHpvKAvPWUWl9XWtNJfG9T4kMw0sxqz9MFv0Xdk/edit" + "a" * 3000
        payload = {
            "url": long_url
        }
        response = client.post("/extract", json=payload, headers=auth_headers)
        assert response.status_code == 422  # Validation error

class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_url_with_special_characters(self, client, auth_headers):
        """Test extraction with special characters in URL."""
        payload = {
            "url": "https://docs.google.com/spreadsheets/d/12itafHpvKAvPWUWl9XWtNJfG9T4kMw0sxqz9MFv0Xdk/edit?usp=sharing&gid=123"
        }
        response = client.post("/extract", json=payload, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["document_id"] == "12itafHpvKAvPWUWl9XWtNJfG9T4kMw0sxqz9MFv0Xdk"
    
    def test_url_with_multiple_different_gids(self, client, auth_headers):
        """Test extraction with multiple different gid parameters."""
        payload = {
            "url": "https://docs.google.com/spreadsheets/d/12itafHpvKAvPWUWl9XWtNJfG9T4kMw0sxqz9MFv0Xdk/edit?gid=123&otherparam=value#gid=456"
        }
        response = client.post("/extract", json=payload, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "123" in data["sheet_ids"]
        assert "456" in data["sheet_ids"]
        assert len(data["sheet_ids"]) == 2
    
    def test_malformed_document_id(self, client, auth_headers):
        """Test extraction with malformed document ID."""
        payload = {
            "url": "12itafHpvKAvPWUWl9XWtNJ"  # 23 chars - too short for new validation (min 25)
        }
        response = client.post("/extract", json=payload, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False  # Should fail because it's less than 25 chars minimum
        assert data["document_id"] is None
    
    def test_unicode_in_url(self, client, auth_headers):
        """Test extraction with Unicode characters in URL."""
        payload = {
            "url": "https://docs.google.com/spreadsheets/d/12itafHpvKAvPWUWl9XWtNJfG9T4kMw0sxqz9MFv0Xdk/edit?title=测试"
        }
        response = client.post("/extract", json=payload, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

class TestResponseFormat:
    """Test response format and structure."""
    
    def test_response_structure(self, client, auth_headers):
        """Test that response has correct structure."""
        payload = {
            "url": "12itafHpvKAvPWUWl9XWtNJfG9T4kMw0sxqz9MFv0Xdk"
        }
        response = client.post("/extract", json=payload, headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        
        # Check required fields
        required_fields = ["success", "document_id", "sheet_ids", "original_url", "url_type", "timestamp"]
        for field in required_fields:
            assert field in data
        
        # Check data types
        assert isinstance(data["success"], bool)
        assert isinstance(data["sheet_ids"], list)
        assert isinstance(data["original_url"], str)
        assert isinstance(data["url_type"], str)
        assert isinstance(data["timestamp"], str)
    
    def test_timestamp_format(self, client, auth_headers):
        """Test that timestamp is in ISO format."""
        payload = {
            "url": "12itafHpvKAvPWUWl9XWtNJfG9T4kMw0sxqz9MFv0Xdk"
        }
        response = client.post("/extract", json=payload, headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        timestamp = data["timestamp"]
        
        # Basic ISO format check (should contain T and end with Z or timezone)
        assert "T" in timestamp
        assert len(timestamp) > 10  # Should be longer than just date

class TestIntegrationScenarios:
    """Test real-world integration scenarios."""
    
    def test_google_sheets_url_variations(self, client, auth_headers):
        """Test various Google Sheets URL formats."""
        test_cases = [
            {
                "url": "https://docs.google.com/spreadsheets/d/12itafHpvKAvPWUWl9XWtNJfG9T4kMw0sxqz9MFv0Xdk/edit#gid=0",
                "expected_doc_id": "12itafHpvKAvPWUWl9XWtNJfG9T4kMw0sxqz9MFv0Xdk",
                "expected_sheet_ids": ["0"]
            },
            {
                "url": "https://docs.google.com/spreadsheets/d/12itafHpvKAvPWUWl9XWtNJfG9T4kMw0sxqz9MFv0Xdk/edit?usp=sharing",
                "expected_doc_id": "12itafHpvKAvPWUWl9XWtNJfG9T4kMw0sxqz9MFv0Xdk",
                "expected_sheet_ids": []
            },
            {
                "url": "docs.google.com/spreadsheets/d/12itafHpvKAvPWUWl9XWtNJfG9T4kMw0sxqz9MFv0Xdk/edit",
                "expected_doc_id": "12itafHpvKAvPWUWl9XWtNJfG9T4kMw0sxqz9MFv0Xdk",
                "expected_sheet_ids": []
            }
        ]
        
        for test_case in test_cases:
            payload = {"url": test_case["url"]}
            response = client.post("/extract", json=payload, headers=auth_headers)
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] is True
            assert data["document_id"] == test_case["expected_doc_id"]
            assert data["sheet_ids"] == test_case["expected_sheet_ids"]

