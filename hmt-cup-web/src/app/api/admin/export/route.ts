import { NextResponse } from "next/server";
import { getAdminSupabase } from "@/lib/supabase";

function csvEscape(value: string) {
  if (/[",\n]/.test(value)) return `"${value.replace(/"/g, '""')}"`;
  return value;
}

export async function GET() {
  const supabase = getAdminSupabase();
  const { data, error } = await supabase
    .from("subscribers")
    .select("email,name,source,created_at")
    .order("created_at", { ascending: false });

  if (error) {
    return NextResponse.json({ error: "server_error" }, { status: 500 });
  }

  const rows = [
    ["email", "name", "source", "created_at"],
    ...(data ?? []).map((r) => [
      r.email,
      r.name ?? "",
      r.source ?? "",
      r.created_at,
    ]),
  ];
  const csv = rows.map((r) => r.map((c) => csvEscape(String(c))).join(",")).join("\n");

  return new NextResponse(csv, {
    headers: {
      "Content-Type": "text/csv; charset=utf-8",
      "Content-Disposition": `attachment; filename="hmtcup-subscribers-${new Date()
        .toISOString()
        .slice(0, 10)}.csv"`,
    },
  });
}
