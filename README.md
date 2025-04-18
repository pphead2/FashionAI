# Fashion Finder AI

A web application that helps users identify and purchase clothing items and accessories from outfit images using AI-powered image recognition and product search.

## Overview

Fashion Finder AI serves both fashion-conscious individuals and those seeking style guidance by automatically detecting clothing items and finding similar products available for purchase. By leveraging AI for image recognition and integrating with Google's Shopping API, users can easily discover and shop for items that match their desired looks.

## Features

- **Image Upload and Analysis**: Upload images of outfits and automatically detect clothing items and accessories
- **Product Search**: Find similar items from various retailers through Google Shopping API integration
- **User Accounts**: Save favorite items, view search history, and manage a personal profile
- **Smart Caching**: Optimized performance with Redis-based caching system

## Tech Stack

- **Backend**: Python 3.9+, FastAPI, MongoDB, Redis
- **Frontend**: React.js, Material-UI, Redux
- **Cloud Services**: Google Cloud Platform (Cloud Run, Storage, Vision AI, Shopping API)
- **DevOps**: Docker, CI/CD pipeline

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 16+
- Docker and Docker Compose
- GCP account with enabled APIs
- MongoDB Atlas account
- Redis (local or Memorystore)

### Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/fashion-finder-ai.git
cd fashion-finder-ai
```

2. Set up the backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Set up the frontend
```bash
cd frontend
npm install
```

4. Configure environment variables
```bash
cp .env.example .env
# Edit .env with your configuration details
```

5. Start the development environment
```bash
docker-compose up
```

## Project Structure

```
fashion-finder-ai/
├── backend/              # Python FastAPI backend
│   ├── app/              # Application code
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Core functionality
│   │   ├── models/       # Data models
│   │   └── services/     # External services integration
│   ├── Dockerfile        # Backend Docker configuration
│   └── requirements.txt  # Python dependencies
├── frontend/             # React.js frontend
│   ├── public/           # Static files
│   ├── src/              # Source code
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   └── services/     # API service integrations
│   ├── Dockerfile        # Frontend Docker configuration
│   └── package.json      # Node.js dependencies
├── docs/                 # Documentation
├── docker-compose.yml    # Local development orchestration
└── README.md             # This file
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
