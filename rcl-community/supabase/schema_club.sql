-- RetroCameraLand - Retro Club (kart ile giris, basvurular, etkinlikler, kareler, panel ayarlari)
-- "rcl-mesajlar" Supabase projesinde SQL Editor'de BIR KEZ calistir. Idempotent.
create extension if not exists pgcrypto;
create sequence if not exists club_member_no_seq start 1;

-- Lisans kartlari. Kartin numarasi uyeligin anahtaridir: ilk giriste uyelik olusur, sonraki girislerde ayni uyelik acilir.
create table if not exists club_cards (
  code text primary key,                 -- RC-7K4M-2QXP
  batch text not null default '',
  note text not null default '',         -- siparis no / kime verildi
  status text not null default 'unused' check (status in ('unused','used','void')),
  used_at timestamptz,
  created_at timestamptz not null default now()
);

create table if not exists club_members (
  id uuid primary key default gen_random_uuid(),
  card_code text not null unique references club_cards(code),
  username text unique,                  -- kucuk harf; ilk giriste secilir
  name text not null default '',
  email text not null default '',
  city text not null default '',
  instagram text not null default '',
  bio text not null default '',
  avatar_url text not null default '',
  member_no int not null default nextval('club_member_no_seq'),
  via text not null default 'card' check (via in ('card','application')),
  status text not null default 'active' check (status in ('active','suspended')),
  joined_at timestamptz not null default now(),
  last_seen_at timestamptz not null default now()
);

-- Cihazda acik kalan oturumlar (tarayicida saklanan anahtar).
create table if not exists club_sessions (
  token text primary key,
  member_id uuid not null references club_members(id) on delete cascade,
  created_at timestamptz not null default now()
);
create index if not exists club_sessions_member_idx on club_sessions (member_id);

-- Kendi retro kamerasiyla selfie gonderip basvuranlar (panelden onaylanir; onayda kart numarasi e-postayla gider).
create table if not exists club_applications (
  id uuid primary key default gen_random_uuid(),
  name text not null default '',
  email text not null default '',
  city text not null default '',
  camera_model text not null default '',
  instagram text not null default '',
  note text not null default '',
  selfie_path text not null default '',  -- ozel bucket yolu (herkese acik degil)
  consent_at timestamptz,
  status text not null default 'pending' check (status in ('pending','approved','rejected')),
  review_note text not null default '',
  card_code text,
  reviewed_at timestamptz,
  created_at timestamptz not null default now()
);
create index if not exists club_applications_status_idx on club_applications (status, created_at desc);

create table if not exists club_photos (
  id uuid primary key default gen_random_uuid(),
  member_id uuid not null references club_members(id) on delete cascade,
  image_url text not null,
  camera_title text not null default '',
  caption text not null default '',
  location text not null default '',
  status text not null default 'visible' check (status in ('visible','hidden')),
  like_count int not null default 0,
  created_at timestamptz not null default now()
);
create index if not exists club_photos_feed_idx on club_photos (status, created_at desc);
create table if not exists club_photo_likes (
  photo_id uuid not null references club_photos(id) on delete cascade,
  member_id uuid not null references club_members(id) on delete cascade,
  created_at timestamptz not null default now(),
  primary key (photo_id, member_id)
);

create table if not exists club_events (
  id uuid primary key default gen_random_uuid(),
  kind text not null default 'bulusma' check (kind in ('bulusma','kurs','workshop','gezi')),
  title text not null,
  description text not null default '',
  starts_at timestamptz not null,
  ends_at timestamptz,
  place text not null default '',
  city text not null default '',
  capacity int not null default 0,        -- 0 = sinirsiz
  cover_url text not null default '',
  status text not null default 'published' check (status in ('draft','published','cancelled')),
  created_at timestamptz not null default now()
);
create index if not exists club_events_time_idx on club_events (status, starts_at);
create table if not exists club_event_rsvps (
  event_id uuid not null references club_events(id) on delete cascade,
  member_id uuid not null references club_members(id) on delete cascade,
  created_at timestamptz not null default now(),
  primary key (event_id, member_id)
);

-- Panelden duzenlenen uye alani ayarlari (karsilama metni, duyuru, bolum gorunurlugu...).
create table if not exists club_settings (
  key text primary key,
  value jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);

-- Tarayici Supabase'e dogrudan baglanmaz; tum erisim Vercel API uzerinden secret anahtarla yapilir.
alter table club_cards enable row level security;
alter table club_members enable row level security;
alter table club_sessions enable row level security;
alter table club_applications enable row level security;
alter table club_photos enable row level security;
alter table club_photo_likes enable row level security;
alter table club_events enable row level security;
alter table club_event_rsvps enable row level security;
alter table club_settings enable row level security;
