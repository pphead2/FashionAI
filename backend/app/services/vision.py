from google.cloud import vision
from google.oauth2 import service_account
import logging
import io
from typing import List, Dict, Any, Optional, Tuple
import os

from ..core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

class VisionAI:
    """Google Cloud Vision AI service for image analysis"""
    
    _client = None
    
    # Clothing item categories
    CLOTHING_CATEGORIES = [
        "shirt", "t-shirt", "dress", "pants", "jeans", "shorts", "skirt",
        "jacket", "coat", "sweater", "hoodie", "blazer", "suit", "tie",
        "shoes", "sneakers", "heels", "boots", "sandals", "hat", "cap",
        "sunglasses", "glasses", "watch", "bracelet", "necklace", "earrings",
        "ring", "bag", "handbag", "backpack", "wallet", "belt", "scarf"
    ]
    
    # Pattern types
    PATTERN_TYPES = [
        "solid", "striped", "plaid", "checkered", "dotted", "floral",
        "geometric", "animal_print", "camouflage", "logo", "graphic"
    ]
    
    # Style categories
    STYLE_CATEGORIES = [
        "casual", "formal", "business", "sporty", "athletic", "streetwear",
        "vintage", "bohemian", "preppy", "punk", "minimalist", "luxury"
    ]
    
    def __init__(self):
        """Initialize Google Vision AI client"""
        try:
            # Check if we have service account credentials
            if hasattr(settings, "GCP_SERVICE_ACCOUNT_KEY_PATH") and settings.GCP_SERVICE_ACCOUNT_KEY_PATH:
                # Create service account credentials
                credentials = service_account.Credentials.from_service_account_file(
                    settings.GCP_SERVICE_ACCOUNT_KEY_PATH
                )
                # Initialize client with credentials
                VisionAI._client = vision.ImageAnnotatorClient(credentials=credentials)
            else:
                # Use default credentials if no service account provided
                VisionAI._client = vision.ImageAnnotatorClient()
                
            logger.info("Vision AI client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Vision AI client: {str(e)}")
            raise Exception(f"Vision AI initialization error: {str(e)}")
    
    @classmethod
    def get_client(cls):
        """Get or create Vision AI client"""
        if cls._client is None:
            try:
                cls._client = vision.ImageAnnotatorClient()
                logger.info("Vision AI client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Vision AI client: {str(e)}")
                raise
        return cls._client
    
    @classmethod
    async def detect_labels(cls, image_content: bytes) -> List[Dict[str, Any]]:
        """
        Detect labels in an image
        
        Args:
            image_content: Image content as bytes
            
        Returns:
            List of detected labels with scores
        """
        client = cls.get_client()
        image = vision.Image(content=image_content)
        
        try:
            response = client.label_detection(image=image)
            labels = []
            
            for label in response.label_annotations:
                labels.append({
                    "description": label.description,
                    "score": label.score,
                    "topicality": label.topicality
                })
            
            logger.info(f"Detected {len(labels)} labels in image")
            return labels
        except Exception as e:
            logger.error(f"Failed to detect labels: {str(e)}")
            raise
    
    @classmethod
    async def detect_objects(cls, image_content: bytes) -> List[Dict[str, Any]]:
        """
        Detect objects in an image
        
        Args:
            image_content: Image content as bytes
            
        Returns:
            List of detected objects with bounding boxes
        """
        client = cls.get_client()
        image = vision.Image(content=image_content)
        
        try:
            response = client.object_localization(image=image)
            objects = []
            
            for obj in response.localized_object_annotations:
                # Convert normalized vertices to pixel coordinates
                # Note: In a real app, you'd use the actual image dimensions
                vertices = []
                for vertex in obj.bounding_poly.normalized_vertices:
                    vertices.append({
                        "x": vertex.x,
                        "y": vertex.y
                    })
                
                objects.append({
                    "name": obj.name,
                    "score": obj.score,
                    "vertices": vertices
                })
            
            logger.info(f"Detected {len(objects)} objects in image")
            return objects
        except Exception as e:
            logger.error(f"Failed to detect objects: {str(e)}")
            raise
    
    @classmethod
    async def analyze_clothing(cls, image_content: bytes) -> List[Dict[str, Any]]:
        """
        Analyze clothing items in an image
        
        Args:
            image_content: Image content as bytes
            
        Returns:
            List of detected clothing items with attributes
        """
        # Get general labels
        labels = await cls.detect_labels(image_content)
        
        # Get object locations
        objects = await cls.detect_objects(image_content)
        
        # Filter objects and labels related to clothing
        clothing_items = []
        
        # Process detected objects
        for obj in objects:
            # Check if object is a clothing item
            if any(category.lower() in obj["name"].lower() for category in cls.CLOTHING_CATEGORIES):
                # Find potential matching labels for additional info
                matching_labels = [
                    label for label in labels 
                    if label["description"].lower() in obj["name"].lower() 
                    or obj["name"].lower() in label["description"].lower()
                ]
                
                # Extract color from labels (in a real app, this would be more sophisticated)
                colors = cls._extract_colors(labels)
                
                # Extract patterns from labels
                pattern = cls._extract_pattern(labels)
                
                # Extract style from labels
                style = cls._extract_style(labels)
                
                # Create clothing item entry
                item = {
                    "type": obj["name"],
                    "confidence": obj["score"],
                    "bounding_box": obj["vertices"],
                    "attributes": {
                        "colors": colors,
                        "pattern": pattern,
                        "style": style
                    },
                    "related_labels": [label["description"] for label in matching_labels]
                }
                
                clothing_items.append(item)
        
        logger.info(f"Detected {len(clothing_items)} clothing items in image")
        return clothing_items
    
    @classmethod
    def _extract_colors(cls, labels: List[Dict[str, Any]]) -> List[str]:
        """Extract color information from labels"""
        # Common colors - in a real app, this would be more comprehensive
        common_colors = [
            "red", "blue", "green", "yellow", "black", "white", "pink",
            "purple", "orange", "brown", "gray", "navy", "teal", "gold", "silver"
        ]
        
        colors = []
        for label in labels:
            description = label["description"].lower()
            for color in common_colors:
                if color in description:
                    colors.append(color)
        
        return list(set(colors))  # Remove duplicates
    
    @classmethod
    def _extract_pattern(cls, labels: List[Dict[str, Any]]) -> Optional[str]:
        """Extract pattern information from labels"""
        for label in labels:
            description = label["description"].lower()
            for pattern in cls.PATTERN_TYPES:
                if pattern.lower().replace("_", " ") in description:
                    return pattern
        
        # Default to solid if no pattern detected
        return "solid"
    
    @classmethod
    def _extract_style(cls, labels: List[Dict[str, Any]]) -> Optional[str]:
        """Extract style information from labels"""
        for label in labels:
            description = label["description"].lower()
            for style in cls.STYLE_CATEGORIES:
                if style.lower() in description:
                    return style
        
        # Default to casual if no specific style detected
        return "casual"
    
    @classmethod
    async def analyze_image(cls, image_content: bytes) -> Dict[str, Any]:
        """
        Perform comprehensive image analysis using multiple Vision AI features
        
        Args:
            image_content: Image content as bytes
            
        Returns:
            Dictionary with analysis results from multiple vision features
        """
        client = cls.get_client()
        image = vision.Image(content=image_content)
        
        try:
            # Request features
            features = [
                vision.Feature(type_=vision.Feature.Type.LABEL_DETECTION, max_results=10),
                vision.Feature(type_=vision.Feature.Type.WEB_DETECTION, max_results=10),
                vision.Feature(type_=vision.Feature.Type.OBJECT_LOCALIZATION, max_results=10),
                vision.Feature(type_=vision.Feature.Type.IMAGE_PROPERTIES),
                vision.Feature(type_=vision.Feature.Type.PRODUCT_SEARCH, max_results=10),
            ]
            
            # Perform batch annotation
            response = client.annotate_image({
                'image': image,
                'features': features,
            })
            
            # Process and structure results
            results = cls._process_vision_response(response)
            
            logger.info(f"Completed comprehensive image analysis")
            return results
            
        except Exception as e:
            logger.error(f"Failed to analyze image: {str(e)}")
            return {"error": str(e)}
    
    @classmethod
    async def analyze_image_from_url(cls, image_url: str) -> Dict[str, Any]:
        """
        Analyze an image using its URL
        
        Args:
            image_url: URL of the image to analyze
            
        Returns:
            Dictionary with analysis results
        """
        client = cls.get_client()
        
        try:
            # Create image object from URL
            image = vision.Image()
            image.source.image_uri = image_url
            
            # Request features
            features = [
                vision.Feature(type_=vision.Feature.Type.LABEL_DETECTION, max_results=10),
                vision.Feature(type_=vision.Feature.Type.WEB_DETECTION, max_results=10),
                vision.Feature(type_=vision.Feature.Type.OBJECT_LOCALIZATION, max_results=10),
                vision.Feature(type_=vision.Feature.Type.IMAGE_PROPERTIES),
                vision.Feature(type_=vision.Feature.Type.PRODUCT_SEARCH, max_results=10),
            ]
            
            # Perform batch annotation
            response = client.annotate_image({
                'image': image,
                'features': features,
            })
            
            # Process and structure results
            results = cls._process_vision_response(response)
            
            logger.info(f"Completed image analysis from URL")
            return results
            
        except Exception as e:
            logger.error(f"Failed to analyze image from URL: {str(e)}")
            return {"error": str(e)}
    
    @classmethod
    def _process_vision_response(cls, response) -> Dict[str, Any]:
        """Process and structure the Vision AI batch annotation response"""
        result = {
            "labels": [],
            "web_entities": [],
            "web_labels": [],
            "colors": [],
            "objects": [],
            "fashion_items": [],
        }
        
        # Process label annotations
        if response.label_annotations:
            result["labels"] = [
                {
                    "description": label.description, 
                    "score": round(label.score * 100, 2),
                    "topicality": round(label.topicality * 100, 2)
                } 
                for label in response.label_annotations
            ]
        
        # Process web detection
        if response.web_detection:
            # Web entities
            if response.web_detection.web_entities:
                result["web_entities"] = [
                    {
                        "description": entity.description,
                        "score": round(entity.score * 100, 2) if entity.score else None
                    }
                    for entity in response.web_detection.web_entities
                ]
            
            # Web labels
            if response.web_detection.best_guess_labels:
                result["web_labels"] = [
                    {"label": label.label} 
                    for label in response.web_detection.best_guess_labels
                ]
        
        # Process color information
        if response.image_properties:
            colors = response.image_properties.dominant_colors.colors
            result["colors"] = [
                {
                    "color": {
                        "red": color.color.red,
                        "green": color.color.green,
                        "blue": color.color.blue
                    },
                    "score": round(color.score * 100, 2),
                    "pixel_fraction": round(color.pixel_fraction * 100, 2),
                    "hex": "#{:02x}{:02x}{:02x}".format(
                        color.color.red, color.color.green, color.color.blue
                    )
                }
                for color in colors
            ]
        
        # Process object localization
        if response.localized_object_annotations:
            result["objects"] = [
                {
                    "name": obj.name,
                    "score": round(obj.score * 100, 2),
                    "bounding_poly": [
                        {"x": vertex.x, "y": vertex.y}
                        for vertex in obj.bounding_poly.normalized_vertices
                    ]
                }
                for obj in response.localized_object_annotations
            ]
        
        # Extract fashion-specific information
        fashion_keywords = set(cls.CLOTHING_CATEGORIES) | {
            "APPAREL", "CLOTHING", "DRESS", "SHIRT", "PANTS", "JEANS", "JACKET", 
            "COAT", "FOOTWEAR", "SHOE", "SNEAKER", "BAG", "HANDBAG", "ACCESSORY",
            "WATCH", "JEWELRY", "GLASSES", "SUNGLASSES", "HAT"
        }
        
        # Extract fashion items from labels and objects
        for label in result["labels"]:
            if any(keyword.upper() in label["description"].upper() for keyword in fashion_keywords):
                result["fashion_items"].append({
                    "type": "label",
                    "name": label["description"],
                    "confidence": label["score"]
                })
        
        for obj in result["objects"]:
            if any(keyword.upper() in obj["name"].upper() for keyword in fashion_keywords):
                result["fashion_items"].append({
                    "type": "object",
                    "name": obj["name"],
                    "confidence": obj["score"],
                    "location": obj["bounding_poly"]
                })
        
        # Get dominant colors in more readable format
        result["dominant_colors"] = cls._extract_dominant_colors(result["colors"])
        
        # Generate suggested search terms
        result["suggested_search_terms"] = cls._generate_search_terms(result)
        
        return result
    
    @classmethod
    def _extract_dominant_colors(cls, colors: List[Dict]) -> List[Dict]:
        """Extract dominant colors in a more user-friendly format"""
        if not colors:
            return []
        
        # Get the most prominent colors (top 5)
        top_colors = sorted(colors, key=lambda x: x["score"], reverse=True)[:5]
        
        # Map colors to common color names
        color_names = []
        for color in top_colors:
            r, g, b = color["color"]["red"], color["color"]["green"], color["color"]["blue"]
            
            # Simple color name mapping (this could be improved with a more sophisticated algorithm)
            if max(r, g, b) < 50:
                name = "black"
            elif min(r, g, b) > 200:
                name = "white"
            elif r > max(g, b) + 50:
                name = "red"
            elif g > max(r, b) + 50:
                name = "green"
            elif b > max(r, g) + 50:
                name = "blue"
            elif r > 200 and g > 150 and b < 50:
                name = "yellow"
            elif r > 200 and g < 100 and b > 150:
                name = "pink"
            elif r > 150 and g > 100 and b < 50:
                name = "orange"
            elif r > 100 and g < 100 and b > 100:
                name = "purple"
            elif r < 50 and g > 100 and b > 100:
                name = "teal"
            elif r > 100 and g > 100 and b < 50:
                name = "brown"
            else:
                name = "gray"
            
            color_names.append({
                "name": name,
                "hex": color["hex"],
                "score": color["score"]
            })
        
        return color_names
    
    @classmethod
    def _generate_search_terms(cls, analysis_results: Dict) -> List[str]:
        """Generate suggested search terms based on the analysis results"""
        search_terms = []
        
        # Add all fashion items
        for item in analysis_results["fashion_items"]:
            search_terms.append(item["name"])
        
        # Add top 3 labels
        top_labels = sorted(analysis_results["labels"], key=lambda x: x["score"], reverse=True)[:3]
        for label in top_labels:
            if label["description"] not in search_terms:
                search_terms.append(label["description"])
        
        # Add top web entity
        if analysis_results["web_entities"] and len(analysis_results["web_entities"]) > 0:
            top_entity = analysis_results["web_entities"][0]["description"]
            if top_entity not in search_terms:
                search_terms.append(top_entity)
        
        # Add top color
        if analysis_results["dominant_colors"] and len(analysis_results["dominant_colors"]) > 0:
            top_color = analysis_results["dominant_colors"][0]["name"]
            # Combine top color with top fashion item
            if analysis_results["fashion_items"] and len(analysis_results["fashion_items"]) > 0:
                color_term = f"{top_color} {analysis_results['fashion_items'][0]['name']}"
                search_terms.append(color_term)
        
        return search_terms[:5]  # Limit to 5 search terms

# Create instance
vision_client = VisionAI() 