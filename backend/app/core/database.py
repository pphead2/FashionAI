from supabase import create_client, Client
from .config import settings

# Initialize Supabase client
supabase: Client = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_SERVICE_KEY
)

# Export the client for use in other modules
db = supabase

# Helper functions for common database operations
async def get_user_by_id(user_id: str):
    """Get user by ID from Supabase auth.users table"""
    try:
        response = db.auth.admin.get_user_by_id(user_id)
        return response.user if response else None
    except Exception as e:
        print(f"Error getting user by ID: {e}")
        return None

async def get_user_favorites(user_id: str):
    """Get user's favorite items"""
    try:
        response = db.table('favorites').select('*').eq('user_id', user_id).execute()
        return response.data if response else []
    except Exception as e:
        print(f"Error getting user favorites: {e}")
        return []

async def add_to_favorites(user_id: str, item_data: dict):
    """Add an item to user's favorites"""
    try:
        response = db.table('favorites').insert({
            'user_id': user_id,
            **item_data
        }).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error adding to favorites: {e}")
        return None

async def remove_from_favorites(user_id: str, item_id: str):
    """Remove an item from user's favorites"""
    try:
        response = db.table('favorites').delete().match({
            'user_id': user_id,
            'id': item_id
        }).execute()
        return True
    except Exception as e:
        print(f"Error removing from favorites: {e}")
        return False

async def add_search_history(user_id: str, search_data: dict):
    """Add a search query to user's history"""
    try:
        response = db.table('search_history').insert({
            'user_id': user_id,
            **search_data
        }).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error adding search history: {e}")
        return None

async def get_search_history(user_id: str, limit: int = 10):
    """Get user's recent search history"""
    try:
        response = db.table('search_history')\
            .select('*')\
            .eq('user_id', user_id)\
            .order('created_at', desc=True)\
            .limit(limit)\
            .execute()
        return response.data if response else []
    except Exception as e:
        print(f"Error getting search history: {e}")
        return []

async def log_analytics_event(event_data: dict):
    """Log an analytics event"""
    try:
        response = db.table('analytics_events').insert(event_data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error logging analytics event: {e}")
        return None 