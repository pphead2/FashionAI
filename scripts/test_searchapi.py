import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_product_search(query, price_min=None, price_max=None):
    """
    Test product search using SearchAPI
    
    Args:
        query (str): Search query
        price_min (float, optional): Minimum price filter
        price_max (float, optional): Maximum price filter
    """
    try:
        # Get API key from environment
        api_key = os.getenv('SEARCHAPI_KEY')
        if not api_key:
            raise ValueError("SearchAPI key not found in environment variables")

        # Base parameters
        params = {
            'api_key': api_key,
            'engine': 'google_shopping',
            'q': query,
            'google_domain': 'google.com',
            'gl': 'us',  # Country
            'hl': 'en',  # Language
            'num': 10,   # Increased number of results
            'device': 'desktop',
            'output': 'json'
        }

        # Add price filters if provided
        if price_min is not None:
            params['min_price'] = price_min
        if price_max is not None:
            params['max_price'] = price_max

        print(f"Making request to SearchAPI with parameters: {params}")
        
        # Make the request
        response = requests.get(
            'https://www.searchapi.io/api/v1/search',
            params=params
        )
        response.raise_for_status()
        
        # Parse response
        data = response.json()
        
        # Print results
        print(f"\nSearch Results for: {query}")
        print("-" * 50)
        
        if 'shopping_results' in data:
            for idx, product in enumerate(data['shopping_results'], 1):
                print(f"\nProduct {idx}:")
                print(f"Title: {product.get('title', 'N/A')}")
                print(f"Price: ${product.get('price', 'N/A')}")
                
                # Extract and format rating information
                rating = product.get('rating')
                reviews = product.get('reviews')
                if rating and reviews:
                    print(f"Rating: {rating}/5 ({reviews} reviews)")
                elif rating:
                    print(f"Rating: {rating}/5")
                else:
                    print("Rating: N/A")
                
                # Store and merchant information
                print(f"Store: {product.get('source', 'N/A')}")
                
                # Shipping and delivery info
                shipping = product.get('shipping', 'N/A')
                delivery = product.get('delivery_date', 'N/A')
                if shipping != 'N/A' or delivery != 'N/A':
                    print(f"Shipping: {shipping}")
                    if delivery != 'N/A':
                        print(f"Estimated Delivery: {delivery}")
                
                # Product images
                thumbnail = product.get('thumbnail', 'N/A')
                if thumbnail != 'N/A':
                    print(f"Thumbnail: {thumbnail}")
                
                # Additional product details
                extensions = product.get('extensions', [])
                if extensions:
                    # Look for color, size, material info in extensions
                    for ext in extensions:
                        if any(keyword in ext.lower() for keyword in ['color', 'size', 'material']):
                            print(f"Details: {ext}")
                
                # Product link
                link = product.get('link', 'N/A')
                if link != 'N/A':
                    print(f"Product URL: {link}")
                
                print("-" * 30)
        else:
            print("No shopping results found")
            if 'error' in data:
                print(f"Error: {data['error']}")
            print(f"Full response: {json.dumps(data, indent=2)}")
            
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
    except json.JSONDecodeError as e:
        print(f"Error parsing response: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    # Test fashion-specific searches
    print("\nTesting women's dress search...")
    test_product_search("designer midi dress")
    
    # Test with specific brand
    print("\nTesting brand-specific search...")
    test_product_search("Zara summer collection 2024")
    
    # Test with style and material
    print("\nTesting style and material search...")
    test_product_search("silk wrap dress", price_min=50, price_max=300) 