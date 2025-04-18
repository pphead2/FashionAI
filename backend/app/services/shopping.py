from googleapiclient.discovery import build
import logging
from typing import List, Dict, Any, Optional
import json
from app.core.config import settings
from app.core.cache import cache

logger = logging.getLogger(__name__)

class ShoppingAPI:
    """Google Shopping API service for product search"""
    
    _service = None
    
    # Cache expiration time in seconds (1 day)
    CACHE_EXPIRATION = 86400
    
    @classmethod
    def get_service(cls):
        """Get or create Shopping API service"""
        if cls._service is None:
            try:
                cls._service = build('customsearch', 'v1', developerKey=settings.GOOGLE_API_KEY)
                logger.info("Google Shopping API service initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Google Shopping API service: {str(e)}")
                raise
        return cls._service
    
    @classmethod
    async def search_products(
        cls, 
        query: str, 
        max_results: int = 10,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        brands: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for products using Google Shopping
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            min_price: Minimum price filter
            max_price: Maximum price filter
            brands: List of brand names to filter by
            
        Returns:
            List of product search results
        """
        # Create cache key
        cache_key = f"shopping_search:{query}:{max_results}:{min_price}:{max_price}:{brands}"
        
        # Check cache first
        cached_results = await cache.get(cache_key)
        if cached_results:
            logger.info(f"Retrieved cached shopping results for query: {query}")
            return cached_results
        
        # Build search query with filters
        search_query = query
        
        if min_price is not None and max_price is not None:
            search_query += f" price:{min_price}-{max_price}"
        elif min_price is not None:
            search_query += f" price>{min_price}"
        elif max_price is not None:
            search_query += f" price<{max_price}"
            
        if brands:
            brand_filter = " OR ".join([f"brand:{brand}" for brand in brands])
            search_query += f" ({brand_filter})"
        
        # Get service
        service = cls.get_service()
        
        try:
            # Execute search
            result = service.cse().list(
                q=search_query,
                cx=settings.GOOGLE_SEARCH_ENGINE_ID,
                searchType='shopping',
                num=max_results
            ).execute()
            
            # Parse results
            items = []
            if 'items' in result:
                for item in result['items']:
                    product = {
                        "id": item['cacheId'] if 'cacheId' in item else item['link'],
                        "title": item['title'],
                        "link": item['link'],
                        "image": item['pagemap']['cse_image'][0]['src'] if 'pagemap' in item and 'cse_image' in item['pagemap'] else None,
                        "price": cls._extract_price(item),
                        "currency": cls._extract_currency(item),
                        "brand": cls._extract_brand(item),
                        "description": item['snippet'] if 'snippet' in item else None,
                        "source": item['displayLink'] if 'displayLink' in item else None
                    }
                    items.append(product)
            
            logger.info(f"Found {len(items)} products for query: {query}")
            
            # Cache results
            await cache.set(cache_key, items, cls.CACHE_EXPIRATION)
            
            return items
        except Exception as e:
            logger.error(f"Failed to search products: {str(e)}")
            # Return empty list instead of raising error
            return []
    
    @classmethod
    async def get_product_details(cls, product_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific product
        
        Args:
            product_id: Product ID
            
        Returns:
            Product details or None if not found
        """
        # Check cache first
        cache_key = f"product_details:{product_id}"
        cached_product = await cache.get(cache_key)
        if cached_product:
            logger.info(f"Retrieved cached product details for ID: {product_id}")
            return cached_product
        
        # In a real implementation, this would use the Google Shopping API
        # to get detailed product information. Since there's no specific
        # endpoint for this in the free API, we'd typically use the search
        # API with a very specific query.
        
        # For demonstration purposes, we'll return a mock product
        logger.warning("Using mock product details - in production, this would call the Shopping API")
        
        # Mock product details
        product_details = {
            "id": product_id,
            "title": "Sample Product",
            "brand": "Brand Name",
            "description": "Detailed product description would go here",
            "price": 99.99,
            "currency": "USD",
            "images": ["https://example.com/product1.jpg", "https://example.com/product2.jpg"],
            "availability": "In stock",
            "rating": 4.5,
            "reviews_count": 123,
            "retailer": "Example Store",
            "product_url": f"https://example.com/products/{product_id}",
        }
        
        # Cache the results
        await cache.set(cache_key, product_details, cls.CACHE_EXPIRATION)
        
        return product_details
    
    @classmethod
    def _extract_price(cls, item: Dict[str, Any]) -> Optional[float]:
        """Extract price from item data"""
        try:
            if 'pagemap' in item and 'offer' in item['pagemap']:
                price_str = item['pagemap']['offer'][0]['price']
                return float(price_str.replace('$', '').replace(',', ''))
            if 'pagemap' in item and 'product' in item['pagemap'] and 'price' in item['pagemap']['product'][0]:
                price_str = item['pagemap']['product'][0]['price']
                return float(price_str.replace('$', '').replace(',', ''))
        except (KeyError, IndexError, ValueError):
            pass
        return None
    
    @classmethod
    def _extract_currency(cls, item: Dict[str, Any]) -> str:
        """Extract currency from item data"""
        try:
            if 'pagemap' in item and 'offer' in item['pagemap'] and 'pricecurrency' in item['pagemap']['offer'][0]:
                return item['pagemap']['offer'][0]['pricecurrency']
            if 'pagemap' in item and 'product' in item['pagemap'] and 'pricecurrency' in item['pagemap']['product'][0]:
                return item['pagemap']['product'][0]['pricecurrency']
        except (KeyError, IndexError):
            pass
        return "USD"  # Default to USD
    
    @classmethod
    def _extract_brand(cls, item: Dict[str, Any]) -> Optional[str]:
        """Extract brand from item data"""
        try:
            if 'pagemap' in item and 'product' in item['pagemap'] and 'brand' in item['pagemap']['product'][0]:
                return item['pagemap']['product'][0]['brand']
        except (KeyError, IndexError):
            pass
        
        # Try to extract from title or snippet
        if 'title' in item:
            # Implementation would check for known brands in title
            pass
            
        return None

# Create instance
shopping_api = ShoppingAPI() 