-- RetroCameraLand - Retro Club v3 (ulke/sehir secimi, kamera, kisisel profil, rozetler, uye numarasi atama, kart satisi)
-- "rcl-mesajlar" Supabase projesinde SQL Editor'de calistir. Idempotent: tekrar calistirmak veri silmez.
-- Sira: once schema_club.sql (kuruluysa atla), sonra bu dosya, sonra seed_club_members.sql.

alter table club_members add column if not exists country text not null default 'TR';
alter table club_members add column if not exists camera_model text not null default '';
alter table club_members add column if not exists camera_image_url text not null default '';
alter table club_members add column if not exists cover_url text not null default '';
alter table club_members add column if not exists profile jsonb not null default '{}'::jsonb;  -- vurgu rengi, kart tasarimi, etiketler, koleksiyon...
alter table club_members add column if not exists is_seed boolean not null default false;      -- acilis icin eklenen hesaplar
alter table club_members add column if not exists intro_seen boolean not null default false;

alter table club_members drop constraint if exists club_members_via_check;
alter table club_members add constraint club_members_via_check check (via in ('card','application','purchase','seed'));

-- Panelden karta uye numarasi atanabilir; kart ilk kullanildiginda uyelik bu numarayla acilir.
alter table club_cards add column if not exists member_no int;
alter table club_cards add column if not exists email text not null default '';
alter table club_cards add column if not exists mailed_at timestamptz;
create unique index if not exists club_cards_member_no_key on club_cards (member_no) where member_no is not null;

-- Uyelerin onerdigi etkinlikler taslak olarak panele duser.
alter table club_events add column if not exists proposed_by uuid references club_members(id) on delete set null;

-- Rozetler: katalog kodda (lib/club.js). Burada yalnizca panelden verilen rozetler tutulur;
-- etkinlik/kurs katilimiyla kazanilanlar katilim kayitlarindan hesaplanir.
create table if not exists club_member_badges (
  id uuid primary key default gen_random_uuid(),
  member_id uuid not null references club_members(id) on delete cascade,
  badge text not null,
  city text not null default '',          -- sehir baskani rozeti icin
  note text not null default '',
  awarded_at timestamptz not null default now(),
  unique (member_id, badge, city)
);
create index if not exists club_member_badges_member_idx on club_member_badges (member_id);

-- Retro Club Card satin alanlar: siparis basina uretilen kart numaralari (ayni siparis iki kez kart alamaz).
create table if not exists club_card_orders (
  order_id text not null,
  idx int not null default 0,
  order_name text not null default '',
  email text not null default '',
  card_code text not null references club_cards(code),
  created_at timestamptz not null default now(),
  primary key (order_id, idx)
);

alter table club_member_badges enable row level security;
alter table club_card_orders enable row level security;

-- Yeni uye numarasi: sirayi ilerletir; bir uyeye ya da karta ayrilmis numaralari atlar.
create or replace function club_next_member_no() returns int language plpgsql as $$
declare n int;
begin
  loop
    n := nextval('club_member_no_seq');
    exit when not exists (select 1 from club_members where member_no = n)
          and not exists (select 1 from club_cards where member_no = n);
  end loop;
  return n;
end $$;
alter table club_members alter column member_no set default club_next_member_no();

-- Panelden uye numarasi degistirme (kart maili gonderirken). Cakisma varsa hata verir.
create unique index if not exists club_members_member_no_key on club_members (member_no);
