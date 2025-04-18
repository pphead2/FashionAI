from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Optional
import logging
import uuid

from ...core.config import get_settings
from ...services.storage import CloudStorage
from ...services.vision import VisionAI
from ...services.shopping import ShoppingAPI
from ...db.mongodb import get_database
from ...models.user import User
from ...core.auth import get_current_user

settings = get_settings()
router = APIRouter()
logger = logging.getLogger(__name__)

cloud_storage = CloudStorage()
vision_ai = VisionAI()
shopping_api = ShoppingAPI()


@router.post("/upload/")
async def upload_image(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    current_user: User = Depends(get_current_user),
    analyze: bool = True,
    db = Depends(get_database)
):
    """
    Upload an image to cloud storage and optionally analyze it with Vision AI.
    Returns the image URL and analysis results if requested.
    """
    try:
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Create a unique ID for this upload
        upload_id = str(uuid.uuid4())
        
        # Upload file to Google Cloud Storage
        file_content = await file.read()
        file_path = cloud_storage.generate_upload_path(
            user_id=str(current_user.id),
            filename=file.filename
        )
        
        public_url = cloud_storage.upload_file(
            file_content=file_content,
            file_path=file_path,
            content_type=file.content_type
        )
        
        # Prepare response
        response_data = {
            "id": upload_id,
            "file_name": file.filename,
            "file_path": file_path,
            "public_url": public_url,
            "analysis": None,
            "similar_products": None
        }
        
        # Save to database
        await db.images.insert_one({
            "id": upload_id,
            "user_id": str(current_user.id),
            "file_name": file.filename,
            "file_path": file_path,
            "public_url": public_url,
            "created_at": datetime.utcnow()
        })
        
        # Analyze image if requested
        if analyze:
            # Analyze with Vision AI
            clothing_items = vision_ai.analyze_clothing(file_content)
            response_data["analysis"] = clothing_items
            
            # Find similar products (if any clothing items were detected)
            if clothing_items and len(clothing_items) > 0:
                # Use the primary detected item for product search
                primary_item = clothing_items[0]
                query = f"{primary_item['category']} {primary_item['color']} {primary_item['pattern']} {primary_item['style']}"
                
                # Search for similar products
                products = await shopping_api.search_products(
                    query=query.strip(),
                    max_results=5
                )
                response_data["similar_products"] = products
                
                # Update database record with analysis
                await db.images.update_one(
                    {"id": upload_id},
                    {"$set": {
                        "analysis": clothing_items,
                        "similar_products": products
                    }}
                )
        
        return response_data
    
    except Exception as e:
        logger.error(f"Error processing image upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")


@router.get("/history/")
async def get_user_image_history(
    limit: int = 10,
    skip: int = 0,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get the image upload history for the current user"""
    try:
        # Query database for user's images
        cursor = db.images.find(
            {"user_id": str(current_user.id)}
        ).sort("created_at", -1).skip(skip).limit(limit)
        
        images = await cursor.to_list(length=limit)
        
        # Convert ObjectId to string for JSON serialization
        for image in images:
            image["_id"] = str(image["_id"])
        
        return {
            "count": await db.images.count_documents({"user_id": str(current_user.id)}),
            "images": images
        }
    
    except Exception as e:
        logger.error(f"Error retrieving image history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving image history: {str(e)}")


@router.delete("/{image_id}/")
async def delete_image(
    image_id: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Delete a user's uploaded image"""
    try:
        # Find the image
        image = await db.images.find_one({
            "id": image_id,
            "user_id": str(current_user.id)
        })
        
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")
        
        # Delete from cloud storage
        cloud_storage.delete_file(image["file_path"])
        
        # Delete from database
        await db.images.delete_one({"id": image_id})
        
        return {"message": "Image deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting image: {str(e)}")


@router.get("/{image_id}/analyze")
async def analyze_existing_image(
    image_id: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Analyze an existing image with Vision AI"""
    try:
        # Find the image
        image = await db.images.find_one({
            "id": image_id,
            "user_id": str(current_user.id)
        })
        
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")
        
        # Download the image content
        import requests
        response = requests.get(image["public_url"])
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to download image")
        
        file_content = response.content
        
        # Analyze with Vision AI
        clothing_items = vision_ai.analyze_clothing(file_content)
        
        # Find similar products if clothing items were detected
        similar_products = []
        if clothing_items and len(clothing_items) > 0:
            # Use the primary detected item for product search
            primary_item = clothing_items[0]
            query = f"{primary_item['category']} {primary_item['color']} {primary_item['pattern']} {primary_item['style']}"
            
            # Search for similar products
            similar_products = await shopping_api.search_products(
                query=query.strip(),
                max_results=5
            )
        
        # Update database with analysis results
        await db.images.update_one(
            {"id": image_id},
            {"$set": {
                "analysis": clothing_items,
                "similar_products": similar_products
            }}
        )
        
        return {
            "image_id": image_id,
            "analysis": clothing_items,
            "similar_products": similar_products
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing image: {str(e)}")


@router.post("/search/")
async def search_similar_products(
    query: str,
    max_results: int = 10,
    price_min: Optional[float] = None,
    price_max: Optional[float] = None,
    brands: Optional[List[str]] = None,
    current_user: User = Depends(get_current_user)
):
    """Search for products using the Shopping API"""
    try:
        products = await shopping_api.search_products(
            query=query,
            max_results=max_results,
            price_min=price_min,
            price_max=price_max,
            brands=brands
        )
        
        return {"products": products}
    
    except Exception as e:
        logger.error(f"Error searching products: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error searching products: {str(e)}")


@router.get("/product/{product_id}/")
async def get_product_details(
    product_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get detailed information about a specific product"""
    try:
        product = await shopping_api.get_product_details(product_id)
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        return product
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving product details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving product details: {str(e)}") 