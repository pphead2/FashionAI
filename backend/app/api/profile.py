from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from .schemas import ProfileUpdate, UserResponse
from .deps import supabase, get_current_user
from typing import Dict
import uuid

router = APIRouter(prefix="/profile", tags=["profile"])

@router.get("/me", response_model=UserResponse)
async def get_profile(current_user: Dict = Depends(get_current_user)):
    try:
        # Get profile from profiles table
        profile = supabase.table("profiles").select("*").eq("id", current_user["id"]).single().execute()
        
        if not profile.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        return UserResponse(**profile.data)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/me", response_model=UserResponse)
async def update_profile(
    profile_data: ProfileUpdate,
    current_user: Dict = Depends(get_current_user)
):
    try:
        # Update profile in profiles table
        profile = supabase.table("profiles").update(
            profile_data.dict(exclude_unset=True)
        ).eq("id", current_user["id"]).execute()

        if not profile.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )

        return UserResponse(**profile.data[0])

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/me/image")
async def upload_profile_image(
    file: UploadFile = File(...),
    current_user: Dict = Depends(get_current_user)
):
    try:
        # Validate file type
        if not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image"
            )

        # Generate unique filename
        file_ext = file.filename.split(".")[-1]
        filename = f"{current_user['id']}/{uuid.uuid4()}.{file_ext}"

        # Upload to Supabase Storage
        file_data = await file.read()
        storage_response = supabase.storage.from_("profile-images").upload(
            filename,
            file_data
        )

        if not storage_response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload image"
            )

        # Get public URL
        image_url = supabase.storage.from_("profile-images").get_public_url(filename)

        # Update profile with new image URL
        profile = supabase.table("profiles").update({
            "image_url": image_url
        }).eq("id", current_user["id"]).execute()

        return {"image_url": image_url}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/me")
async def delete_account(current_user: Dict = Depends(get_current_user)):
    try:
        # Delete profile from profiles table
        supabase.table("profiles").delete().eq("id", current_user["id"]).execute()

        # Delete user from auth
        supabase.auth.admin.delete_user(current_user["id"])

        return {"message": "Account deleted successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) 