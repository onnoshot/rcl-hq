-- ============================================================================
-- RetroCameraLand Topluluk v2 - Kamera Sıralama + Oylama + Foto Kartları
-- Supabase > SQL Editor'e yapıştır > RUN. (profiles tablosu v1'den varsa korunur.)
-- Sonra seed_cameras.sql'i çalıştır (99 kamera kataloğu).
-- ============================================================================

-- ---------------- profiles (v1'den; yoksa oluştur) ----------------
create table if not exists profiles (
  customer_id   text primary key,
  handle        text unique not null,
  display_name  text not null,
  avatar_url    text,
  bio           text,
  city          text,
  member_since  timestamptz not null default now(),
  orders_count  int not null default 0,
  total_likes   int not null default 0,
  links         jsonb not null default '{}'::jsonb,   -- sosyal linkler {instagram,threads,x,facebook,pinterest,website}
  section_prefs jsonb not null default '{}'::jsonb,   -- ziyaretciye gizlenen bolumler {badges:false,...}
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now()
);
-- mevcut profiles tablosuna eksik kolonlari ekle
alter table profiles add column if not exists links         jsonb not null default '{}'::jsonb;
alter table profiles add column if not exists section_prefs jsonb not null default '{}'::jsonb;
-- anilarin gorunurlugu: herkese acik / gizli
alter table camera_photos add column if not exists visibility text not null default 'public' check (visibility in ('public','private'));

-- ---------------- cameras (katalog + kullanıcı eklemeleri) ----------------
create table if not exists cameras (
  id          uuid primary key default gen_random_uuid(),
  handle      text unique,
  brand       text not null,
  model       text not null,
  title       text not null,
  image_url   text,
  price       numeric,
  product_url text,
  base_score  int not null default 0,            -- seed beğeni (boş sayfa olmasın)
  votes_count int not null default 0,            -- gerçek kullanıcı beğenileri
  score       int generated always as (base_score + votes_count) stored,  -- = toplam beğeni
  photo_count int not null default 0,
  year        text,                              -- üretim/çıkış yılı
  highlight   text,                              -- kısa ikonik özellik
  source      text not null default 'catalog' check (source in ('catalog','user')),
  created_at  timestamptz not null default now()
);

-- ---------------- camera_waitlist (kullanıcı kendini bekleme listesine ekler) ----------------
create table if not exists camera_waitlist (
  camera_id   uuid not null references cameras(id) on delete cascade,
  customer_id text not null references profiles(customer_id) on delete cascade,
  created_at  timestamptz not null default now(),
  primary key (camera_id, customer_id)
);
create index if not exists camera_waitlist_idx on camera_waitlist (camera_id);
alter table camera_waitlist enable row level security;
-- mevcut tabloya eksik kolonlari ekle (daha once olusturulduysa)
alter table cameras add column if not exists year        text;
alter table cameras add column if not exists highlight   text;
alter table cameras add column if not exists photo_count int not null default 0;
alter table cameras add column if not exists description text;            -- magaza urun aciklamasindan (gercek bilgi)
create index if not exists cameras_score_idx on cameras (score desc);
create index if not exists cameras_brand_idx on cameras (brand, score desc);

-- ---------------- camera_votes (1 üye = 1 kameraya 1 oy) ----------------
create table if not exists camera_votes (
  camera_id  uuid not null references cameras(id) on delete cascade,
  voter_id   text not null references profiles(customer_id) on delete cascade,
  created_at timestamptz not null default now(),
  primary key (camera_id, voter_id)
);
create or replace function bump_camera_votes() returns trigger language plpgsql as $$
begin
  if (tg_op='INSERT') then update cameras set votes_count=votes_count+1 where id=new.camera_id;
  elsif (tg_op='DELETE') then update cameras set votes_count=greatest(0,votes_count-1) where id=old.camera_id; end if;
  return null;
end $$;
drop trigger if exists trg_camera_votes on camera_votes;
create trigger trg_camera_votes after insert or delete on camera_votes
  for each row execute function bump_camera_votes();

-- ---------------- camera_photos (kameranın kartına yüklenen foto) ----------------
create table if not exists camera_photos (
  id            uuid primary key default gen_random_uuid(),
  camera_id     uuid not null references cameras(id) on delete cascade,
  customer_id   text not null references profiles(customer_id) on delete cascade,
  image_url     text not null,
  taken_date    date,                            -- çekildiği tarih
  location      text,                            -- çekildiği yer
  note          text,                            -- o ana dair kısa düşünce
  like_count    int not null default 0,
  comment_count int not null default 0,
  status        text not null default 'approved' check (status in ('pending','approved','rejected')),
  created_at    timestamptz not null default now()
);
create index if not exists camera_photos_cam_idx  on camera_photos (camera_id, created_at desc);
create index if not exists camera_photos_feed_idx on camera_photos (status, created_at desc);
create index if not exists camera_photos_user_idx on camera_photos (customer_id);

create or replace function bump_photo_count() returns trigger language plpgsql as $$
begin
  if (tg_op='INSERT') then update cameras set photo_count=photo_count+1 where id=new.camera_id;
  elsif (tg_op='DELETE') then update cameras set photo_count=greatest(0,photo_count-1) where id=old.camera_id; end if;
  return null;
end $$;
drop trigger if exists trg_photo_count on camera_photos;
create trigger trg_photo_count after insert or delete on camera_photos
  for each row execute function bump_photo_count();

-- ---------------- photo_likes ----------------
create table if not exists photo_likes (
  photo_id    uuid not null references camera_photos(id) on delete cascade,
  customer_id text not null references profiles(customer_id) on delete cascade,
  created_at  timestamptz not null default now(),
  primary key (photo_id, customer_id)
);
create or replace function bump_photo_likes() returns trigger language plpgsql as $$
begin
  if (tg_op='INSERT') then update camera_photos set like_count=like_count+1 where id=new.photo_id;
  elsif (tg_op='DELETE') then update camera_photos set like_count=greatest(0,like_count-1) where id=old.photo_id; end if;
  return null;
end $$;
drop trigger if exists trg_photo_likes on photo_likes;
create trigger trg_photo_likes after insert or delete on photo_likes
  for each row execute function bump_photo_likes();

-- ---------------- photo_comments ----------------
create table if not exists photo_comments (
  id          uuid primary key default gen_random_uuid(),
  photo_id    uuid not null references camera_photos(id) on delete cascade,
  customer_id text not null references profiles(customer_id) on delete cascade,
  body        text not null,
  created_at  timestamptz not null default now()
);
create index if not exists photo_comments_idx on photo_comments (photo_id, created_at asc);
create or replace function bump_comment_count() returns trigger language plpgsql as $$
begin
  if (tg_op='INSERT') then update camera_photos set comment_count=comment_count+1 where id=new.photo_id;
  elsif (tg_op='DELETE') then update camera_photos set comment_count=greatest(0,comment_count-1) where id=old.photo_id; end if;
  return null;
end $$;
drop trigger if exists trg_comment_count on photo_comments;
create trigger trg_comment_count after insert or delete on photo_comments
  for each row execute function bump_comment_count();

-- ---------------- user_cameras (profile'a eklenen kendi kameraları) ----------------
create table if not exists user_cameras (
  id          uuid primary key default gen_random_uuid(),
  customer_id text not null references profiles(customer_id) on delete cascade,
  brand       text not null,
  model       text not null,
  created_at  timestamptz not null default now(),
  unique (customer_id, brand, model)
);
create index if not exists user_cameras_idx on user_cameras (customer_id);

-- ---------------- feedback (Time Capsule geri bildirimleri -> dashboard istatistik) ----------------
create table if not exists feedback (
  id          uuid primary key default gen_random_uuid(),
  customer_id text references profiles(customer_id) on delete set null,
  rating      int check (rating between 1 and 5),   -- 1-5 yildiz / emoji
  category    text,                                  -- genel / tasarim / fikir / hata / istek
  message     text,
  created_at  timestamptz not null default now()
);
create index if not exists feedback_idx on feedback (created_at desc);
alter table feedback enable row level security;

-- ---------------- RLS (tüm erişim Vercel service-key ile; anon kullanılmıyor) ----------------
alter table cameras        enable row level security;
alter table camera_votes   enable row level security;
alter table camera_photos  enable row level security;
alter table photo_likes    enable row level security;
alter table photo_comments enable row level security;
alter table user_cameras   enable row level security;
-- service_role RLS'i bypass eder; anon anahtar kullanılmadığı için public policy yok.
