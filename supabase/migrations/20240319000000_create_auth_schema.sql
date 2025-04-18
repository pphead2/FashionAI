-- Create profiles table that extends auth.users
create table public.profiles (
  id uuid references auth.users on delete cascade primary key,
  updated_at timestamp with time zone default timezone('utc'::text, now()) not null,
  username text unique,
  full_name text,
  avatar_url text,
  preferences jsonb default '{}'::jsonb,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  constraint username_length check (char_length(username) >= 3)
);

-- Enable Row Level Security
alter table public.profiles enable row level security;

-- Create secure policies
create policy "Public profiles are viewable by everyone." on public.profiles
  for select using (true);

create policy "Users can insert their own profile." on public.profiles
  for insert with check (auth.uid() = id);

create policy "Users can update their own profile." on public.profiles
  for update using (auth.uid() = id);

-- Create favorites table
create table public.favorites (
  id uuid default uuid_generate_v4() primary key,
  user_id uuid references public.profiles on delete cascade not null,
  item_data jsonb not null, -- Stores product details
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Enable RLS on favorites
alter table public.favorites enable row level security;

-- Create favorites policies
create policy "Users can view their own favorites." on public.favorites
  for select using (auth.uid() = user_id);

create policy "Users can insert their own favorites." on public.favorites
  for insert with check (auth.uid() = user_id);

create policy "Users can delete their own favorites." on public.favorites
  for delete using (auth.uid() = user_id);

-- Create search_history table
create table public.search_history (
  id uuid default uuid_generate_v4() primary key,
  user_id uuid references public.profiles on delete cascade not null,
  search_type text not null, -- 'image' or 'text'
  search_data jsonb not null, -- Stores search parameters and results
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Enable RLS on search_history
alter table public.search_history enable row level security;

-- Create search_history policies
create policy "Users can view their own search history." on public.search_history
  for select using (auth.uid() = user_id);

create policy "Users can insert their own search history." on public.search_history
  for insert with check (auth.uid() = user_id);

-- Create analytics_events table
create table public.analytics_events (
  id uuid default uuid_generate_v4() primary key,
  user_id uuid references public.profiles on delete set null,
  event_type text not null, -- 'registration', 'login', 'search', 'item_click', etc.
  event_data jsonb not null,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Enable RLS on analytics_events
alter table public.analytics_events enable row level security;

-- Create analytics_events policies
create policy "Users can view their own analytics events." on public.analytics_events
  for select using (auth.uid() = user_id);

create policy "Users can insert their own analytics events." on public.analytics_events
  for insert with check (auth.uid() = user_id);

-- Create function to handle new user creation
create or replace function public.handle_new_user()
returns trigger as $$
begin
  insert into public.profiles (id, full_name, avatar_url)
  values (new.id, new.raw_user_meta_data->>'full_name', new.raw_user_meta_data->>'avatar_url');
  return new;
end;
$$ language plpgsql security definer;

-- Create trigger for new user creation
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();

-- Create indexes for better query performance
create index idx_profiles_username on public.profiles (username);
create index idx_favorites_user_id on public.favorites (user_id);
create index idx_search_history_user_id on public.search_history (user_id);
create index idx_analytics_events_user_id on public.analytics_events (user_id);
create index idx_analytics_events_type on public.analytics_events (event_type); 