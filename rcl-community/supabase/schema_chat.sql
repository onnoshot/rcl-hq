-- RetroCameraLand - musteri mesajlasma (site sohbet penceresi <-> HQ dashboard "Mesajlar")
-- Supabase SQL Editor'de BIR KEZ calistir. Idempotent.
create extension if not exists pgcrypto;

create table if not exists chat_conversations (
  id uuid primary key default gen_random_uuid(),
  token text not null unique,            -- ziyaretcinin tarayicisinda saklanan gizli anahtar
  code text not null unique,             -- kisa referans (Telegram + panel): M-4F7A2C
  name text not null default '',
  contact text not null default '',      -- e-posta veya telefon (istege bagli)
  page text not null default '',
  device text not null default '',
  status text not null default 'open' check (status in ('open','closed')),
  unread_admin int not null default 0,
  unread_visitor int not null default 0,
  last_preview text not null default '',
  last_sender text not null default 'visitor',
  created_at timestamptz not null default now(),
  last_message_at timestamptz not null default now()
);

create table if not exists chat_messages (
  id bigserial primary key,
  conversation_id uuid not null references chat_conversations(id) on delete cascade,
  sender text not null check (sender in ('visitor','admin')),
  body text not null,
  via text not null default 'web',       -- web | panel | telegram
  created_at timestamptz not null default now()
);

create index if not exists chat_messages_conv_idx on chat_messages (conversation_id, id);
create index if not exists chat_conversations_last_idx on chat_conversations (last_message_at desc);

-- Tarayici Supabase'e dogrudan baglanmaz; tum erisim Vercel API uzerinden secret anahtarla yapilir.
alter table chat_conversations enable row level security;
alter table chat_messages enable row level security;
