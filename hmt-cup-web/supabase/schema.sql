-- HMT CUP 2027 — subscribers table
-- Run this once in the Supabase SQL editor of the new project.

create table if not exists subscribers (
  id uuid primary key default gen_random_uuid(),
  email text not null unique,
  name text,
  source text not null default 'form' check (source in ('form', 'popup')),
  created_at timestamptz not null default now()
);

alter table subscribers enable row level security;

-- Public (anon) can only INSERT — no SELECT policy, so emails stay private.
-- The API route never uses `.select()` after insert, so this policy alone is enough.
create policy "public can subscribe"
  on subscribers
  for insert
  to anon
  with check (true);

-- The admin dashboard reads via the service role key, which bypasses RLS entirely.
