# Data Extraction API

A production-ready FastAPI application that extracts structured data from text strings and returns JSON responses. This API supports various types of data extraction including emails, phone numbers, dates, numbers, and URLs.

## Features

- **Multiple Extraction Types**: Extract emails, phone numbers, dates, numbers, URLs, or all data types
- **Authentication**: Secure API token-based authentication
- **Production Ready**: Comprehensive testing, CI/CD pipeline, and deployment configuration
- **CORS Support**: Cross-origin requests enabled for frontend integration
- **Comprehensive Documentation**: Auto-generated API docs with Swagger UI
- **Error Handling**: Robust error handling with meaningful error messages

## API Endpoints

### Health Check
- `GET /` - Root endpoint health check
- `GET /health` - Detailed health check

### Data Extraction
- `POST /extract` - Extract data from text (requires authentication)

## Authentication

The API uses Bearer token authentication. Include your API token in the Authorization header:

```
Authorization: Bearer your-api-token-here
```

## Request Format

```json
{
  "text": "Contact John at john@example.com or call (555) 123-4567",
  "extraction_type": "email_phone"
}
```

### Extraction Types

- `email_phone` - Extract email addresses and phone numbers
- `dates` - Extract date patterns
- `numbers` - Extract numeric values
- `urls` - Extract URLs
- `all` - Extract all supported data types

## Response Format

```json
{
  "success": true,
  "extracted_data": {
    "emails": ["john@example.com"],
    "phone_numbers": ["(555) 123-4567"]
  },
  "original_text": "Contact John at john@example.com or call (555) 123-4567",
  "extraction_type": "email_phone",
  "timestamp": "2025-09-17T10:30:00.000Z"
}
```

## Local Development

### Prerequisites

- Python 3.11+
- pip

### Setup

1. Clone the repository
2. Create and activate virtual environment:
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set environment variables:
   ```bash
   export API_TOKEN="your-secret-token-here"
   ```

5. Run the application:
   ```bash
   python main.py
   ```

The API will be available at `http://localhost:8000`

### API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Testing

Run the test suite:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=main --cov-report=html
```

## Deployment

This application is configured for deployment on Vercel with the included `vercel.json` configuration.

### Environment Variables for Production

Set the following environment variable in your deployment platform:

- `API_TOKEN` - Your secure API authentication token

## Project Structure

```
python-api-project/
├── main.py              # FastAPI application
├── requirements.txt     # Python dependencies
├── vercel.json         # Vercel deployment configuration
├── .gitignore          # Git ignore rules
├── README.md           # Project documentation
├── tests/              # Test suite
│   ├── __init__.py
│   ├── test_main.py    # Main application tests
│   └── conftest.py     # Test configuration
└── .github/
    └── workflows/
        └── ci.yml      # GitHub Actions CI/CD pipeline
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License.

