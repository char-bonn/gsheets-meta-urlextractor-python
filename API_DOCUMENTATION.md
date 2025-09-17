# Google Sheets ID Extraction API Documentation

## Overview

The Google Sheets ID Extraction API is a production-ready FastAPI service that extracts Google Sheets document IDs and sheet IDs from URLs. It provides a clean, secure, and well-tested interface for parsing Google Sheets URLs and returning structured JSON data.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://your-app.vercel.app`

## Authentication

All API endpoints (except health checks) require Bearer token authentication.

```http
Authorization: Bearer your-secret-token-here
```

## Endpoints

### Health Check

#### GET `/` or `/health`

Returns the API health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-09-17T19:19:42.814449",
  "version": "1.0.0"
}
```

### Extract Google Sheets IDs

#### POST `/extract`

Extracts Google Sheets document ID and sheet IDs from a URL.

**Request Body:**
```json
{
  "url": "https://docs.google.com/spreadsheets/d/12itafHpvKAvPWUWl9XWtNJfG9T4kMw0sxqz9MFv0Xdk/edit?gid=1058109381#gid=1058109381"
}
```

**Response:**
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

## Supported URL Formats

The API supports various Google Sheets URL formats:

### 1. Full URL with Sheet IDs
```
https://docs.google.com/spreadsheets/d/12itafHpvKAvPWUWl9XWtNJfG9T4kMw0sxqz9MFv0Xdk/edit?gid=1058109381#gid=1058109381
```

### 2. Full URL without Sheet IDs
```
https://docs.google.com/spreadsheets/d/12itafHpvKAvPWUWl9XWtNJfG9T4kMw0sxqz9MFv0Xdk/edit
```

### 3. Document ID Only
```
12itafHpvKAvPWUWl9XWtNJfG9T4kMw0sxqz9MFv0Xdk
```

### 4. Partial URL
```
docs.google.com/spreadsheets/d/12itafHpvKAvPWUWl9XWtNJfG9T4kMw0sxqz9MFv0Xdk/edit
```

### 5. URL with Additional Parameters
```
https://docs.google.com/spreadsheets/d/12itafHpvKAvPWUWl9XWtNJfG9T4kMw0sxqz9MFv0Xdk/edit?usp=sharing&gid=123
```

## Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Whether the extraction was successful |
| `document_id` | string\|null | The Google Sheets document ID (44 characters) |
| `sheet_ids` | array | List of individual sheet IDs found in the URL |
| `original_url` | string | The original input URL |
| `url_type` | string | Type of URL processed |
| `timestamp` | string | ISO timestamp of when extraction was performed |

## URL Types

| Type | Description |
|------|-------------|
| `document_id` | Input was a clean 44-character document ID |
| `full_url` | Full Google Sheets URL without sheet IDs |
| `full_url_with_sheets` | Full Google Sheets URL with sheet IDs |
| `partial_url` | Partial URL containing the document ID |
| `invalid` | Invalid input that couldn't be processed |

## Error Responses

### 401 Unauthorized
```json
{
  "detail": "Invalid authentication token"
}
```

### 403 Forbidden
```json
{
  "detail": "Not authenticated"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "url"],
      "msg": "String should have at least 1 character",
      "input": ""
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Extraction failed: [error message]"
}
```

## Example Usage

### cURL Examples

#### Extract from Full URL
```bash
curl -X POST "https://your-app.vercel.app/extract" \
  -H "Authorization: Bearer your-secret-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://docs.google.com/spreadsheets/d/12itafHpvKAvPWUWl9XWtNJfG9T4kMw0sxqz9MFv0Xdk/edit?gid=1058109381#gid=1058109381"
  }'
```

#### Extract from Document ID
```bash
curl -X POST "https://your-app.vercel.app/extract" \
  -H "Authorization: Bearer your-secret-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "12itafHpvKAvPWUWl9XWtNJfG9T4kMw0sxqz9MFv0Xdk"
  }'
```

### JavaScript Examples

#### Using Fetch API
```javascript
const response = await fetch('https://your-app.vercel.app/extract', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer your-secret-token-here',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    url: 'https://docs.google.com/spreadsheets/d/12itafHpvKAvPWUWl9XWtNJfG9T4kMw0sxqz9MFv0Xdk/edit?gid=1058109381'
  })
});

const data = await response.json();
console.log(data);
```

#### Using Axios
```javascript
const axios = require('axios');

const response = await axios.post('https://your-app.vercel.app/extract', {
  url: 'https://docs.google.com/spreadsheets/d/12itafHpvKAvPWUWl9XWtNJfG9T4kMw0sxqz9MFv0Xdk/edit?gid=1058109381'
}, {
  headers: {
    'Authorization': 'Bearer your-secret-token-here',
    'Content-Type': 'application/json'
  }
});

console.log(response.data);
```

### Python Examples

#### Using Requests
```python
import requests

url = "https://your-app.vercel.app/extract"
headers = {
    "Authorization": "Bearer your-secret-token-here",
    "Content-Type": "application/json"
}
payload = {
    "url": "https://docs.google.com/spreadsheets/d/12itafHpvKAvPWUWl9XWtNJfG9T4kMw0sxqz9MFv0Xdk/edit?gid=1058109381"
}

response = requests.post(url, json=payload, headers=headers)
data = response.json()
print(data)
```

## Rate Limiting

The API includes rate limiting to prevent abuse:
- **Default**: 100 requests per minute per client
- **Rate limit headers** are included in responses
- **429 Too Many Requests** status code when limit exceeded

## Security Features

### Input Sanitization
- All input URLs are sanitized to prevent XSS attacks
- HTML entities are escaped
- Malicious JavaScript URLs are blocked

### Authentication
- Bearer token authentication required for all extraction endpoints
- Tokens are validated on every request
- Invalid tokens return 401 Unauthorized

### Security Headers
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- `Referrer-Policy: strict-origin-when-cross-origin`

### CORS
- Cross-Origin Resource Sharing enabled for web applications
- Configurable origins for production environments

## Validation Rules

### URL Field
- **Required**: Yes
- **Type**: String
- **Min Length**: 1 character
- **Max Length**: 2048 characters
- **Sanitization**: HTML entities escaped, malicious content removed

### Document ID Format
- **Length**: Exactly 44 characters
- **Characters**: Alphanumeric, underscores, and hyphens only
- **Pattern**: `^[a-zA-Z0-9_-]{44}$`

### Sheet ID Format
- **Type**: Numeric string
- **Pattern**: `\d+`
- **Examples**: `0`, `1058109381`, `123456789`

## Interactive Documentation

The API provides interactive documentation at:
- **Swagger UI**: `https://your-app.vercel.app/docs`
- **ReDoc**: `https://your-app.vercel.app/redoc`

## Testing

The API includes comprehensive test coverage:
- **Unit Tests**: Individual function testing
- **Integration Tests**: Full endpoint testing
- **Security Tests**: Authentication and input validation
- **Edge Cases**: Malformed URLs, Unicode characters, special cases
- **Coverage**: 94%+ code coverage

## Performance

### Response Times
- **Typical**: < 100ms for URL extraction
- **Maximum**: < 500ms including authentication and validation

### Scalability
- **Serverless**: Deployed on Vercel for automatic scaling
- **Stateless**: No session storage, fully stateless design
- **Caching**: Response headers include appropriate cache directives

## Monitoring

### Health Checks
- **Endpoint**: `/health`
- **Response Time**: < 50ms
- **Uptime Monitoring**: Available for external monitoring services

### Logging
- All requests are logged with timestamps
- Error tracking for debugging and monitoring
- Performance metrics collection

## Support

For API support and questions:
- **Documentation**: This document and interactive docs
- **Issues**: GitHub repository issues
- **Testing**: Use the `/health` endpoint to verify API availability

