# Google Cloud Platform Setup Guide

This document provides a step-by-step guide for setting up all required Google Cloud Platform (GCP) services for the Fashion Finder AI application.

## Prerequisites

1. Google Cloud Platform account with billing enabled
2. Google Cloud SDK installed locally (optional, but recommended)
3. Basic familiarity with Google Cloud Console

## 1. Create a GCP Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top of the page
3. Click "NEW PROJECT"
4. Enter a project name (e.g., "fashion-finder-ai")
5. Select an organization if applicable
6. Click "CREATE"
7. Wait for the project to be created and then select it

## 2. Enable Required APIs

1. In the GCP Console, navigate to "APIs & Services" > "Library"
2. Search for and enable the following APIs:
   - Cloud Storage API
   - Cloud Vision API
   - Custom Search API
   - Cloud Run API
   - Cloud Monitoring API
   - Cloud Logging API

## 3. Set Up Service Account

1. Navigate to "IAM & Admin" > "Service Accounts"
2. Click "CREATE SERVICE ACCOUNT"
3. Enter a service account name (e.g., "fashion-finder-service")
4. Add a description and click "CREATE AND CONTINUE"
5. Assign the following roles:
   - Storage Admin
   - Cloud Vision AI User
   - Cloud Run Admin
   - Logs Writer
   - Monitoring Metric Writer
6. Click "CONTINUE" and then "DONE"
7. On the Service Accounts page, find your new service account
8. Click the three dots in the "Actions" column and select "Manage keys"
9. Click "ADD KEY" > "Create new key"
10. Choose "JSON" as the key type and click "CREATE"
11. Save the downloaded JSON key file securely

## 4. Configure Cloud Storage

1. Navigate to "Cloud Storage" > "Buckets"
2. Click "CREATE BUCKET"
3. Enter a globally unique bucket name (e.g., "fashion-finder-images-YOUR_PROJECT_ID")
4. Choose a region (prefer a region close to your users)
5. Leave the default settings for storage class (Standard)
6. Under "Access control", select "Fine-grained"
7. Under "Protection tools", leave the defaults
8. Click "CREATE"
9. Once created, go to the bucket details
10. Navigate to the "Permissions" tab
11. Click "GRANT ACCESS"
12. Add "allUsers" with the role "Storage Object Viewer" to make objects publicly accessible

## 5. Set Up Vision AI

The Vision AI API is already enabled from step 2. No additional configuration is required.

## 6. Configure Custom Search API for Shopping

1. Navigate to "APIs & Services" > "Credentials"
2. Click "CREATE CREDENTIALS" > "API Key"
3. Copy the generated API key
4. Click on the edit icon for the API key
5. Add API restrictions to only allow "Custom Search API"
6. Click "SAVE"

### Create a Custom Search Engine

1. Go to the [Google Programmable Search Engine](https://programmablesearchengine.google.com/create/new)
2. Enter a name for your search engine (e.g., "Fashion Finder Shopping")
3. Under "What to search", select "Search the entire web"
4. Enable "Search only for shopping sites" option if available
5. Click "CREATE"
6. In the resulting page, click "Control Panel"
7. Enable "Search the entire web" and "Image search" options
8. Copy your Search Engine ID for later use

## 7. Environment Variables Setup

Update your `.env` file with the following variables:

```
# Google Cloud
GCP_PROJECT_ID=your-project-id
GCP_STORAGE_BUCKET_NAME=your-bucket-name
GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/to/service-account-key.json
GOOGLE_API_KEY=your-api-key
GOOGLE_SEARCH_ENGINE_ID=your-search-engine-id
```

## 8. Local Testing

To test the GCP setup locally:

1. Make sure the service account key is properly referenced in GOOGLE_APPLICATION_CREDENTIALS
2. Run the application locally
3. Test the image upload endpoint to verify Cloud Storage
4. Test the image analysis endpoint to verify Vision AI
5. Test the product search endpoint to verify Custom Search API

## 9. Configuring MongoDB Atlas (Optional)

While not a GCP service, MongoDB Atlas is recommended for production:

1. Create a [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) account
2. Create a new cluster (the free tier is sufficient for development)
3. Configure network access to allow connections from your application
4. Create a database user with appropriate permissions
5. Get the connection string and update your `.env` file:

```
MONGODB_URI=mongodb+srv://<username>:<password>@<cluster-url>/<dbname>
MONGODB_DB_NAME=fashion_finder
```

## 10. Configuring Redis (Optional)

For Redis, you can either:

1. Use Memorystore for Redis in GCP (recommended for production)
2. Use a third-party Redis provider
3. Run Redis locally for development

For Memorystore (GCP):

1. Navigate to "Memorystore" > "Redis instances"
2. Click "CREATE INSTANCE"
3. Configure the instance and create it
4. Update your `.env` file with the connection details 