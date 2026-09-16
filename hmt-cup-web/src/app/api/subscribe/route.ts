import { NextResponse } from "next/server";
import { getPublicSupabase } from "@/lib/supabase";

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export async function POST(request: Request) {
  const body = await request.json().catch(() => null);
  const email = typeof body?.email === "string" ? body.email.trim().toLowerCase() : "";
  const name = typeof body?.name === "string" ? body.name.trim().slice(0, 120) : null;
  const source = body?.source === "popup" ? "popup" : "form";

  if (!EMAIL_RE.test(email)) {
    return NextResponse.json({ error: "invalid_email" }, { status: 400 });
  }

  const supabase = getPublicSupabase();
  const { error } = await supabase
    .from("subscribers")
    .insert({ email, name, source });

  if (error) {
    // Unique violation -> treat as success (already subscribed)
    if (error.code === "23505") {
      return NextResponse.json({ ok: true, already: true });
    }
    return NextResponse.json({ error: "server_error" }, { status: 500 });
  }

  return NextResponse.json({ ok: true });
}
