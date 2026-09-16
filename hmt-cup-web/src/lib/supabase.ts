import { createClient } from "@supabase/supabase-js";

const url = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const anonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;
const serviceKey = process.env.SUPABASE_SERVICE_ROLE_KEY!;

// Public client: anon key, RLS-restricted to INSERT-only on `subscribers`.
export function getPublicSupabase() {
  return createClient(url, anonKey, { auth: { persistSession: false } });
}

// Server-only client: service role key, full access. Never import from client components.
export function getAdminSupabase() {
  return createClient(url, serviceKey, { auth: { persistSession: false } });
}
