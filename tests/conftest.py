"""
Pytest configuration and fixtures for the Data Extraction API tests.
"""

import pytest
from fastapi.testclient import TestClient
from main import app
import os

@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)

@pytest.fixture
def auth_headers():
    """Provide authentication headers for testing."""
    return {"Authorization": "Bearer your-secret-token-here"}

@pytest.fixture
def invalid_auth_headers():
    """Provide invalid authentication headers for testing."""
    return {"Authorization": "Bearer invalid-token"}

@pytest.fixture
def sample_text_data():
    """Provide sample text data for testing extraction functions."""
    return {
        "email_phone": "Contact John at john@example.com or call (555) 123-4567",
        "dates": "Meeting scheduled for 12/25/2023 and follow-up on Jan 15, 2024",
        "numbers": "The price is $29.99 and quantity is 5 items",
        "urls": "Visit our website at https://example.com or https://test.org",
        "mixed": "Email us at support@company.com, call 555-123-4567, visit https://company.com on 01/01/2024"
    }

@pytest.fixture
def expected_extractions():
    """Provide expected extraction results for test data."""
    return {
        "email_phone": {
            "emails": ["john@example.com"],
            "phone_numbers": ["(555) 123-4567"]
        },
        "dates": {
            "dates": ["12/25/2023", "Jan 15, 2024"]
        },
        "numbers": {
            "numbers": ["29", "99", "5"]
        },
        "urls": {
            "urls": ["https://example.com", "https://test.org"]
        }
    }

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Set up test environment variables."""
    # Ensure we're using the test token
    os.environ["API_TOKEN"] = "your-secret-token-here"
    yield
    # Cleanup if needed

