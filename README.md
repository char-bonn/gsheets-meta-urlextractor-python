# Google Sheets ID Extraction API

A production-ready FastAPI service that extracts Google Sheets document IDs and sheet IDs from URLs. Built with comprehensive testing, security features, and CI/CD pipeline.

## Features

- **Google Sheets URL Parsing**: Extract document IDs and sheet IDs from various URL formats
- **Multiple Input Formats**: Support for full URLs, document IDs, and partial URLs
- **Production Ready**: Comprehensive testing, security, and deployment configuration
- **Authentication**: Bearer token authentication for secure access
- **Rate Limiting**: Built-in rate limiting to prevent abuse
- **Input Sanitization**: XSS protection and input validation
- **CI/CD Pipeline**: Automated testing and deployment with GitHub Actions
- **Vercel Deployment**: Ready for serverless deployment

## Quick Start

### Local Development

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd python-api-project
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Run the API**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **Test the API**
   ```bash
   curl -X POST "http://localhost:8000/extract" \
     -H "Authorization: Bearer your-secret-token-here" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://docs.google.com/spreadsheets/d/12itafHpvKAvPWUWl9XWtNJfG9T4kMw0sxqz9MFv0Xdk/edit?gid=1058109381"}'
   ```

## API Usage

### Extract Google Sheets IDs

**Endpoint**: `POST /extract`

**Request**:
```json
{
  "url": "https://docs.google.com/spreadsheets/d/12itafHpvKAvPWUWl9XWtNJfG9T4kMw0sxqz9MFv0Xdk/edit?gid=1058109381#gid=1058109381"
}
```

**Response**:
```json
{
  "success": true,
  "document_id": "12itafHpvKAvPWUWl9XWtNJfG9T4kMw0sxqz9MFv0Xdk",
  "sheet_ids": ["1058109381"],
  "original_url": "https://docs.google.com/spreadsheets/d/12itafHpvKAvPWUWl9XWtNJfG9T4kMw0sxqz9MFv0Xdk/edit?gid=1058109381#gid=1058109381",
  "url_type": "full_url_with_sheets",
  "timestamp": "2025-09-17T19:19:42.814449"
}
```

### Supported URL Formats

- **Full URL**: `https://docs.google.com/spreadsheets/d/12itafHpvKAvPWUWl9XWtNJfG9T4kMw0sxqz9MFv0Xdk/edit?gid=1058109381`
- **Document ID**: `12itafHpvKAvPWUWl9XWtNJfG9T4kMw0sxqz9MFv0Xdk`
- **Partial URL**: `docs.google.com/spreadsheets/d/12itafHpvKAvPWUWl9XWtNJfG9T4kMw0sxqz9MFv0Xdk/edit`

## Documentation

- **API Documentation**: See [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)
- **Deployment Guide**: See [deployment-guide.md](./deployment-guide.md)
- **Interactive Docs**: Visit `/docs` when running the API

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=main --cov=security --cov-report=term-missing

# Run specific test categories
pytest tests/test_main.py -v
pytest tests/test_security.py -v
```

**Test Coverage**: 94%+ with 51 comprehensive tests covering:
- Unit tests for extraction functions
- Integration tests for API endpoints
- Security and authentication tests
- Edge cases and error handling

## Security Features

- **Authentication**: Bearer token required for all extraction endpoints
- **Input Sanitization**: XSS protection and HTML entity escaping
- **Rate Limiting**: Configurable request limits per client
- **Security Headers**: OWASP recommended security headers
- **CORS**: Configurable cross-origin resource sharing

## Deployment

### Vercel (Recommended)

1. **Deploy to Vercel**
   ```bash
   npm install -g vercel
   vercel login
   vercel --prod
   ```

2. **Set Environment Variables**
   ```bash
   vercel env add API_TOKEN production
   ```

3. **Verify Deployment**
   ```bash
   curl https://your-app.vercel.app/health
   ```

### CI/CD Pipeline

The project includes GitHub Actions for:
- **Automated Testing**: Run on every push and PR
- **Security Scanning**: Bandit and Safety checks
- **Deployment**: Automatic deployment to staging and production
- **Coverage Reporting**: Test coverage tracking

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `API_TOKEN` | Authentication token for API access | Yes |

## Project Structure

```
python-api-project/
├── main.py                 # FastAPI application
├── security.py             # Security utilities
├── requirements.txt        # Python dependencies
├── vercel.json            # Vercel deployment config
├── api/
│   └── index.py           # Vercel entry point
├── tests/
│   ├── conftest.py        # Test configuration
│   ├── test_main.py       # Main API tests
│   └── test_security.py   # Security tests
├── .github/
│   └── workflows/
│       └── ci.yml         # CI/CD pipeline
└── docs/
    ├── API_DOCUMENTATION.md
    └── deployment-guide.md
```

## Development

### Prerequisites

- Python 3.11+
- pip or pipenv
- Git

### Setup Development Environment

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Tests**
   ```bash
   pytest
   ```

3. **Start Development Server**
   ```bash
   uvicorn main:app --reload
   ```

4. **Code Quality**
   ```bash
   flake8 .
   bandit -r .
   ```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

- **Documentation**: [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)
- **Issues**: GitHub Issues
- **Health Check**: `GET /health` endpoint

