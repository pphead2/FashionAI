# Supabase Setup for Fashion Finder AI

This directory contains the Supabase configuration and database migrations for the Fashion Finder AI project.

## Database Schema

The database schema includes the following tables:

1. `profiles` - Extended user profile information
   - Links to `auth.users`
   - Stores username, full name, avatar URL, and preferences
   - Protected by Row Level Security (RLS)

2. `favorites` - User's saved items
   - References user profiles
   - Stores product details in JSONB format
   - Protected by RLS

3. `search_history` - User's search activity
   - Tracks both image and text searches
   - Stores search parameters and results
   - Protected by RLS

4. `analytics_events` - System-wide analytics
   - Tracks user events, searches, and conversions
   - Stores event data in JSONB format
   - Protected by RLS

## Setup Instructions

1. Install Supabase CLI:
   ```bash
   npm install -g supabase-cli
   ```

2. Start Supabase locally:
   ```bash
   supabase start
   ```

3. Apply migrations:
   ```bash
   supabase db reset
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your Google OAuth credentials
   ```

5. Enable Google OAuth:
   - Add your Google OAuth credentials in Supabase dashboard
   - Configure allowed redirect URLs
   - Update `config.toml` if needed

## Security

- All tables have Row Level Security (RLS) enabled
- Users can only access their own data
- Public profiles are read-only
- Analytics events are protected

## Development Workflow

1. Create new migrations:
   ```bash
   supabase migration new <migration_name>
   ```

2. Apply migrations:
   ```bash
   supabase db reset
   ```

3. Push to production:
   ```bash
   supabase db push
   ```

## Environment Variables

Required environment variables:
- `GOOGLE_CLIENT_ID`: Your Google OAuth client ID
- `GOOGLE_CLIENT_SECRET`: Your Google OAuth client secret
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_ANON_KEY`: Your Supabase anonymous key
- `SUPABASE_SERVICE_ROLE_KEY`: Your Supabase service role key 