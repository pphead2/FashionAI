#!/usr/bin/env python3
import os
import sys
import time
import requests
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_endpoint_health(url: str, max_retries: int = 5, delay: int = 10) -> bool:
    """Check if an endpoint is healthy by making HTTP requests with retries."""
    for attempt in range(max_retries):
        try:
            response = requests.get(f"{url}/health")
            if response.status_code == 200:
                logger.info(f"✅ Endpoint {url} is healthy")
                return True
            logger.warning(f"Attempt {attempt + 1}/{max_retries}: Endpoint {url} returned status {response.status_code}")
        except requests.RequestException as e:
            logger.warning(f"Attempt {attempt + 1}/{max_retries}: Failed to connect to {url}: {str(e)}")
        
        if attempt < max_retries - 1:
            logger.info(f"Waiting {delay} seconds before next attempt...")
            time.sleep(delay)
    
    logger.error(f"❌ Failed to verify health of {url} after {max_retries} attempts")
    return False

def verify_backend_functionality(url: str) -> bool:
    """Verify core backend functionality."""
    try:
        # Test search endpoint
        search_response = requests.post(
            f"{url}/api/v1/search",
            json={"query": "test dress", "price_min": 10, "price_max": 100}
        )
        if not search_response.ok:
            logger.error(f"❌ Search endpoint failed: {search_response.status_code}")
            return False
        
        # Test Redis caching
        cache_test = requests.get(f"{url}/api/v1/cache-test")
        if not cache_test.ok:
            logger.error(f"❌ Cache test failed: {cache_test.status_code}")
            return False

        logger.info("✅ Backend functionality tests passed")
        return True
    except requests.RequestException as e:
        logger.error(f"❌ Backend functionality test failed: {str(e)}")
        return False

def verify_frontend_assets(url: str) -> bool:
    """Verify that frontend static assets are accessible."""
    try:
        # Check main page
        main_page = requests.get(url)
        if not main_page.ok:
            logger.error(f"❌ Frontend main page not accessible: {main_page.status_code}")
            return False

        # Check for critical assets
        critical_paths = [
            "/static/js/main.js",
            "/static/css/main.css",
            "/manifest.json"
        ]
        
        for path in critical_paths:
            response = requests.get(f"{url}{path}")
            if not response.ok:
                logger.error(f"❌ Frontend asset {path} not accessible: {response.status_code}")
                return False

        logger.info("✅ Frontend assets verification passed")
        return True
    except requests.RequestException as e:
        logger.error(f"❌ Frontend assets verification failed: {str(e)}")
        return False

def main():
    # Get service URLs from environment variables
    backend_url = os.getenv("BACKEND_URL")
    frontend_url = os.getenv("FRONTEND_URL")

    if not backend_url or not frontend_url:
        logger.error("❌ BACKEND_URL and FRONTEND_URL environment variables must be set")
        sys.exit(1)

    success = True

    # Verify backend
    logger.info("🔍 Verifying backend deployment...")
    if not check_endpoint_health(backend_url):
        success = False
    elif not verify_backend_functionality(backend_url):
        success = False

    # Verify frontend
    logger.info("🔍 Verifying frontend deployment...")
    if not verify_frontend_assets(frontend_url):
        success = False

    if success:
        logger.info("✅ Deployment verification completed successfully")
        sys.exit(0)
    else:
        logger.error("❌ Deployment verification failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 