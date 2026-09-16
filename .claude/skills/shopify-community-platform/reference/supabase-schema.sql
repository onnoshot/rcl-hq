-- Shopify Gamified Community — Supabase schema (Postgres)
-- Fairness rules live HERE (constraints + RLS), not only in app code.
-- Identity: every row keyed to the Shopify customer id (text). The Vercel
-- bridge verifies identity and sets request.jwt.claims.sub = '<shopify_customer_id>'.

-- ---------- helper: current verified member id from the minted JWT ----------
create or replace function auth_member_id() returns text
  language sql stable as $$ select nullif(current_setting('request.jwt.claims', true)::json->>'sub','') $$;

-- ---------- profiles ----------
create table if not exists profiles (
  customer_id   text primary key,                 -- Shopify customer.id
  handle        text unique not null,             -- /community/profil/<handle>
  display_name  text not null,
  avatar_url    text,
  bio           text,
  city          text,
  member_since  timestamptz not null,             -- from Shopify customer.created_at (tenure badges)
  orders_count  int not null default 0,           -- from Shopify customer.orders_count (purchase badges)
  total_likes   int not null default 0,           -- denormalized, maintained by trigger
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now()
);

-- ---------- contests (monthly, with optional theme) ----------
create table if not exists contests (
  id          uuid primary key default gen_random_uuid(),
  slug        text unique not null,               -- 2026-haziran
  title       text not null,
  theme       text,                               -- "Şehir Işıkları"
  starts_at   timestamptz not null,
  ends_at     timestamptz not null,
  status      text not null default 'active' check (status in ('upcoming','active','closed')),
  hero_url    text,
  created_at  timestamptz not null default now()
);

-- ---------- photos (UGC entries) ----------
create table if not exists photos (
  id           uuid primary key default gen_random_uuid(),
  contest_id   uuid not null references contests(id) on delete cascade,
  customer_id  text not null references profiles(customer_id) on delete cascade,
  image_url    text not null,                     -- Supabase Storage / R2 (EXIF already stripped)
  camera_model text not null,                     -- REQUIRED (exifr-prefilled)
  location     text not null,                     -- REQUIRED (exifr GPS reverse-geocoded)
  caption      text,
  like_count   int not null default 0,            -- denormalized, maintained by trigger
  status       text not null default 'pending' check (status in ('pending','approved','rejected')),
  created_at   timestamptz not null default now()
);
create index if not exists photos_contest_idx on photos (contest_id, status, like_count desc);
create index if not exists photos_customer_idx on photos (customer_id);

-- ---------- votes (likes) ----------
create table if not exists votes (
  id          uuid primary key default gen_random_uuid(),
  photo_id    uuid not null references photos(id) on delete cascade,
  voter_id    text not null references profiles(customer_id) on delete cascade,
  created_at  timestamptz not null default now(),
  unique (photo_id, voter_id)                     -- one vote per member per photo
);
create index if not exists votes_photo_idx on votes (photo_id);
create index if not exists votes_velocity_idx on votes (photo_id, created_at);  -- velocity anomaly scans

-- block self-vote at the DB layer (defense in depth; also blocked in API)
create or replace function block_self_vote() returns trigger language plpgsql as $$
begin
  if exists (select 1 from photos p where p.id = new.photo_id and p.customer_id = new.voter_id) then
    raise exception 'self_vote_not_allowed';
  end if;
  return new;
end $$;
drop trigger if exists trg_block_self_vote on votes;
create trigger trg_block_self_vote before insert on votes
  for each row execute function block_self_vote();

-- keep like_count + profile.total_likes denormalized
create or replace function bump_like_counts() returns trigger language plpgsql as $$
declare owner text;
begin
  if (tg_op = 'INSERT') then
    update photos set like_count = like_count + 1 where id = new.photo_id returning customer_id into owner;
    update profiles set total_likes = total_likes + 1 where customer_id = owner;
  elsif (tg_op = 'DELETE') then
    update photos set like_count = greatest(0, like_count - 1) where id = old.photo_id returning customer_id into owner;
    update profiles set total_likes = greatest(0, total_likes - 1) where customer_id = owner;
  end if;
  return null;
end $$;
drop trigger if exists trg_bump_like on votes;
create trigger trg_bump_like after insert or delete on votes
  for each row execute function bump_like_counts();

-- ---------- badges ----------
create table if not exists badges (
  key         text primary key,                   -- 'tenure_archivist', 'orders_collector', 'week_winner'
  axis        text not null check (axis in ('tenure','purchase','achievement')),
  label       text not null,
  icon        text,
  threshold   int                                 -- days (tenure) or orders (purchase); null for achievement
);
create table if not exists user_badges (
  customer_id text not null references profiles(customer_id) on delete cascade,
  badge_key   text not null references badges(key) on delete cascade,
  awarded_at  timestamptz not null default now(),
  primary key (customer_id, badge_key)
);

-- ---------- leaderboards (current week / month) ----------
create or replace view leaderboard_week as
  select p.*, pr.handle, pr.display_name, pr.avatar_url
  from photos p join profiles pr on pr.customer_id = p.customer_id
  where p.status = 'approved' and p.created_at >= date_trunc('week', now())
  order by p.like_count desc, p.created_at asc;

create or replace view leaderboard_month as
  select p.*, pr.handle, pr.display_name, pr.avatar_url
  from photos p join profiles pr on pr.customer_id = p.customer_id
  where p.status = 'approved' and p.created_at >= date_trunc('month', now())
  order by p.like_count desc, p.created_at asc;

-- =====================  RLS  (the fairness layer)  =====================
alter table profiles    enable row level security;
alter table photos      enable row level security;
alter table votes       enable row level security;
alter table user_badges enable row level security;

-- public read of approved content
create policy photos_read   on photos      for select using (status = 'approved' or customer_id = auth_member_id());
create policy profiles_read on profiles    for select using (true);
create policy votes_read    on votes        for select using (true);
create policy badges_read   on user_badges  for select using (true);

-- writes: only as yourself
create policy profiles_self on profiles for all
  using (customer_id = auth_member_id()) with check (customer_id = auth_member_id());
create policy photos_self   on photos   for insert with check (customer_id = auth_member_id());
create policy votes_self    on votes    for insert with check (voter_id   = auth_member_id());
create policy votes_unvote  on votes    for delete using  (voter_id   = auth_member_id());

-- NOTE: service-role key (Vercel server) bypasses RLS for moderation status flips and gift-card awards.
-- Never expose the service-role key to the theme. The theme only ever talks to the App Proxy.
