# CI/CD Pipeline Documentation

This document describes the Continuous Integration and Continuous Deployment (CI/CD) pipeline for the Fashion Finder application.

## Overview

The CI/CD pipeline is implemented using GitHub Actions and consists of two main workflows:
1. Backend CI/CD (`backend-ci-cd.yml`)
2. Frontend CI/CD (`frontend-ci-cd.yml`)

Both pipelines are triggered automatically on pushes and pull requests to the `main` branch, but only for changes in their respective directories.

## Required Secrets

The following secrets must be configured in GitHub repository settings:

### GCP Related
- `GCP_PROJECT_ID`: Your Google Cloud Project ID
- `GCP_SA_KEY`: Service account key JSON for GCP authentication
- `GCP_BUCKET_NAME`: Cloud Storage bucket name for frontend deployment
- `GCP_LB_NAME`: Load balancer name for CDN cache invalidation

### Supabase Related
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Supabase service role key
- `SUPABASE_ANON_KEY`: Supabase anonymous key (for frontend)

### Other Services
- `REDIS_HOST`: Redis instance hostname
- `REDIS_PORT`: Redis instance port
- `SEARCHAPI_KEY`: SearchAPI API key
- `BACKEND_URL`: Deployed backend service URL
- `FRONTEND_URL`: Deployed frontend URL

## Backend Pipeline

The backend pipeline (`backend-ci-cd.yml`) performs the following steps:

1. **Test**
   - Sets up Python 3.9
   - Installs dependencies
   - Runs pytest with coverage
   - Uploads coverage reports to Codecov

2. **Build & Deploy** (only on main branch)
   - Sets up Google Cloud SDK
   - Builds Docker image
   - Pushes to Google Container Registry
   - Deploys to Cloud Run
   - Configures environment variables

## Frontend Pipeline

The frontend pipeline (`frontend-ci-cd.yml`) performs the following steps:

1. **Test**
   - Sets up Node.js 16
   - Installs dependencies
   - Runs tests with coverage
   - Uploads coverage reports to Codecov

2. **Build & Deploy** (only on main branch)
   - Builds React application
   - Sets up Google Cloud SDK
   - Deploys to Cloud Storage bucket
   - Configures caching headers
   - Invalidates CDN cache

## Deployment Verification

A deployment verification script (`scripts/verify_deployment.py`) runs after deployments to ensure:

1. **Backend Verification**
   - Health endpoint is responding
   - Search API is functional
   - Redis caching is working

2. **Frontend Verification**
   - Main page is accessible
   - Static assets are properly served
   - Critical resources are available

## Environment Configuration

### Development
- Backend: http://localhost:8000
- Frontend: http://localhost:3000

### Production
- Backend: https://api.fashionfinder.app
- Frontend: https://fashionfinder.app

## Monitoring

- Cloud Run metrics are available in Google Cloud Console
- Frontend performance is monitored through Cloud CDN
- Application logs are available in Cloud Logging

## Rollback Procedure

In case of deployment issues:

1. **Backend Rollback**
   ```bash
   gcloud run services update-traffic fashion-finder-backend --to-revision=REVISION_ID
   ```

2. **Frontend Rollback**
   ```bash
   gsutil -m cp -r gs://backup-bucket/frontend-TIMESTAMP/* gs://production-bucket/
   ```

## Adding New Secrets

To add new secrets to the pipeline:

1. Go to GitHub repository settings
2. Navigate to Secrets and Variables > Actions
3. Click "New repository secret"
4. Add the secret name and value

## Common Issues and Solutions

1. **Docker Build Failures**
   - Check Dockerfile syntax
   - Verify build context
   - Ensure dependencies are properly specified

2. **Deployment Failures**
   - Verify service account permissions
   - Check resource quotas
   - Review Cloud Run service configuration

3. **Frontend Asset Issues**
   - Clear browser cache
   - Check CDN cache invalidation
   - Verify asset paths in build output

## Best Practices

1. **Commits**
   - Use conventional commit messages
   - Include ticket numbers in commits
   - Keep changes focused and atomic

2. **Testing**
   - Write tests for new features
   - Maintain high coverage
   - Test deployment changes locally first

3. **Security**
   - Regularly rotate secrets
   - Review service account permissions
   - Keep dependencies updated

## Support

For CI/CD related issues:
1. Check Cloud Run logs
2. Review GitHub Actions workflow runs
3. Contact DevOps team for assistance 