# Deployment Guide - Data Extraction API

This guide explains how to deploy the Data Extraction API to Vercel for production use.

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **GitHub Repository**: Push your code to a GitHub repository
3. **API Token**: Generate a secure API token for authentication

## Deployment Steps

### 1. Prepare Environment Variables

In your Vercel project settings, add the following environment variable:

- `API_TOKEN`: Your secure API authentication token (e.g., `your-production-secret-token-here`)

### 2. Deploy via Vercel Dashboard

1. Go to [vercel.com/dashboard](https://vercel.com/dashboard)
2. Click "New Project"
3. Import your GitHub repository
4. Vercel will automatically detect the `vercel.json` configuration
5. Add your environment variables in the project settings
6. Deploy!

### 3. Deploy via Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy from project directory
vercel

# For production deployment
vercel --prod
```

### 4. Configure Environment Variables via CLI

```bash
# Add production API token
vercel env add API_TOKEN production

# List environment variables
vercel env ls
```

## Post-Deployment Verification

### 1. Test Health Endpoint

```bash
curl https://your-app.vercel.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-09-17T19:00:00.000000",
  "version": "1.0.0"
}
```

### 2. Test Extract Endpoint

```bash
curl -X POST "https://your-app.vercel.app/extract" \
  -H "Authorization: Bearer your-production-token" \
  -H "Content-Type: application/json" \
  -d '{"text": "Contact john@example.com or call (555) 123-4567", "extraction_type": "all"}'
```

### 3. Test API Documentation

Visit: `https://your-app.vercel.app/docs`

## Security Considerations

### 1. API Token Security

- Use a strong, randomly generated API token
- Store the token securely in Vercel's environment variables
- Never commit the token to your repository
- Rotate the token regularly

### 2. CORS Configuration

The API is configured to allow cross-origin requests. For production, consider restricting CORS origins:

```python
# In main.py, update CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Restrict to your domain
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)
```

### 3. Rate Limiting

The API includes basic rate limiting. For production, consider:

- Using Redis for distributed rate limiting
- Implementing IP-based rate limiting
- Adding API key-based rate limiting

## Monitoring and Maintenance

### 1. Vercel Analytics

Enable Vercel Analytics in your project settings to monitor:
- Request volume
- Response times
- Error rates
- Geographic distribution

### 2. Error Monitoring

Consider integrating with error monitoring services:
- Sentry
- Rollbar
- Bugsnag

### 3. Logging

Vercel automatically captures function logs. Access them via:
- Vercel Dashboard → Project → Functions tab
- Vercel CLI: `vercel logs`

## Scaling Considerations

### 1. Function Limits

Vercel serverless functions have limits:
- Maximum execution time: 30 seconds (configured in vercel.json)
- Maximum payload size: 5MB
- Memory limit: 1024MB

### 2. Cold Starts

To minimize cold starts:
- Keep dependencies minimal
- Use connection pooling for databases
- Consider Vercel's Edge Functions for faster response times

### 3. Database Integration

For persistent data storage, consider:
- Vercel Postgres
- PlanetScale
- Supabase
- MongoDB Atlas

## Custom Domain Setup

1. In Vercel Dashboard → Project Settings → Domains
2. Add your custom domain
3. Configure DNS records as instructed
4. SSL certificate will be automatically provisioned

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are in `requirements.txt`
2. **Environment Variables**: Verify variables are set in Vercel project settings
3. **Function Timeout**: Check function execution time and optimize if needed
4. **CORS Issues**: Verify CORS configuration for your frontend domain

### Debug Deployment

```bash
# Check deployment logs
vercel logs

# Run local development server
vercel dev

# Check function output
vercel inspect [deployment-url]
```

## CI/CD Integration

The project includes GitHub Actions for automated deployment:

1. Push to `main` branch triggers production deployment
2. Push to `develop` branch triggers staging deployment
3. Pull requests trigger preview deployments

Required GitHub Secrets:
- `VERCEL_TOKEN`: Vercel authentication token
- `VERCEL_ORG_ID`: Your Vercel organization ID
- `VERCEL_PROJECT_ID`: Your Vercel project ID
- `API_TOKEN`: Your API authentication token

## Support

For deployment issues:
1. Check Vercel documentation: [vercel.com/docs](https://vercel.com/docs)
2. Review function logs in Vercel dashboard
3. Test locally with `vercel dev`
4. Check GitHub Actions logs for CI/CD issues

