from fastapi import APIRouter, HTTPException, status, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm
from .schemas import UserRegister, UserLogin, TokenResponse, PasswordChange, EmailChange
from .deps import supabase, get_current_user
from .utils import verify_password, get_password_hash, create_tokens
from typing import Dict

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserRegister):
    try:
        # Check if user exists
        existing_user = supabase.auth.admin.list_users(
            filters={"email": user_data.email}
        )
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Create user in Supabase
        user = supabase.auth.admin.create_user({
            "email": user_data.email,
            "password": user_data.password,
            "email_confirm": True
        })

        # Create profile in profiles table
        profile_data = {
            "id": user.id,
            "email": user_data.email,
            "display_name": user_data.display_name or user_data.email.split("@")[0]
        }
        supabase.table("profiles").insert(profile_data).execute()

        # Generate tokens
        tokens = create_tokens(user.id, user.email)
        return TokenResponse(**tokens)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        # Authenticate with Supabase
        auth_response = supabase.auth.sign_in_with_password({
            "email": form_data.username,
            "password": form_data.password
        })
        
        user = auth_response.user
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        # Generate tokens
        tokens = create_tokens(user.id, user.email)
        return TokenResponse(**tokens)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(response: Response, current_user: Dict = Depends(get_current_user)):
    try:
        # Generate new tokens
        tokens = create_tokens(current_user["id"], current_user["email"])
        return TokenResponse(**tokens)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token refresh failed"
        )

@router.post("/logout")
async def logout(current_user: Dict = Depends(get_current_user)):
    try:
        # Sign out from Supabase
        supabase.auth.sign_out()
        return {"message": "Successfully logged out"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )

@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: Dict = Depends(get_current_user)
):
    try:
        # Verify old password
        user = supabase.auth.get_user(current_user["id"])
        if not verify_password(password_data.old_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect password"
            )

        # Update password
        supabase.auth.admin.update_user_by_id(
            current_user["id"],
            {"password": password_data.new_password}
        )
        return {"message": "Password updated successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/change-email")
async def change_email(
    email_data: EmailChange,
    current_user: Dict = Depends(get_current_user)
):
    try:
        # Verify password
        user = supabase.auth.get_user(current_user["id"])
        if not verify_password(email_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect password"
            )

        # Update email
        supabase.auth.admin.update_user_by_id(
            current_user["id"],
            {"email": email_data.new_email}
        )
        return {"message": "Email updated successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/request-password-reset")
async def request_password_reset(email: str):
    try:
        # Send password reset email through Supabase
        supabase.auth.reset_password_email(email)
        return {"message": "Password reset email sent"}
    except Exception as e:
        # Don't reveal if email exists
        return {"message": "If an account exists with this email, a password reset link will be sent"} 