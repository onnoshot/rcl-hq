import Image from "next/image";
import { getAdminSupabase } from "@/lib/supabase";
import { LogoutButton } from "./LogoutButton";

export const dynamic = "force-dynamic";

type Subscriber = {
  id: string;
  email: string;
  name: string | null;
  source: string;
  created_at: string;
};

export default async function AdminPage() {
  const supabase = getAdminSupabase();
  const { data, error } = await supabase
    .from("subscribers")
    .select("id,email,name,source,created_at")
    .order("created_at", { ascending: false })
    .limit(500);

  const subscribers = (data ?? []) as Subscriber[];
  const total = subscribers.length;
  const fromPopup = subscribers.filter((s) => s.source === "popup").length;
  const weekAgo = Date.now() - 7 * 24 * 60 * 60 * 1000;
  const thisWeek = subscribers.filter(
    (s) => new Date(s.created_at).getTime() > weekAgo
  ).length;

  return (
    <div className="min-h-screen bg-ink px-6 py-10 text-white sm:px-10">
      <div className="mx-auto max-w-5xl">
        <div className="mb-10 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Image
              src="/logo/hmt-cup-logo-white.svg"
              alt="HMT CUP"
              width={32}
              height={32}
            />
            <h1 className="font-display text-2xl tracking-wide">
              Abone Paneli
            </h1>
          </div>
          <div className="flex items-center gap-3">
            <a
              href="/api/admin/export"
              className="border border-white/20 px-5 py-2.5 text-[10px] font-bold uppercase tracking-[0.2em] text-white transition-colors hover:border-white"
            >
              CSV İndir
            </a>
            <LogoutButton />
          </div>
        </div>

        {error && (
          <p className="mb-6 border border-red/40 bg-red/10 p-4 text-sm text-white">
            Supabase bağlantı hatası: {error.message}. `.env.local` içindeki
            SUPABASE değişkenlerini kontrol edin.
          </p>
        )}

        <div className="mb-10 grid grid-cols-3 gap-px overflow-hidden bg-white/10">
          {[
            { label: "Toplam Abone", value: total },
            { label: "Bu Hafta", value: thisWeek },
            { label: "Popup'tan", value: fromPopup },
          ].map((s) => (
            <div key={s.label} className="bg-ink-2 p-6 text-center">
              <div className="font-display text-4xl text-red">{s.value}</div>
              <div className="mt-1 text-[10px] font-bold uppercase tracking-[0.15em] text-white/45">
                {s.label}
              </div>
            </div>
          ))}
        </div>

        <div className="overflow-x-auto border border-white/10">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-white/10 bg-white/5 text-[10px] font-bold uppercase tracking-[0.15em] text-white/45">
                <th className="px-5 py-3">E-posta</th>
                <th className="px-5 py-3">İsim</th>
                <th className="px-5 py-3">Kaynak</th>
                <th className="px-5 py-3">Tarih</th>
              </tr>
            </thead>
            <tbody>
              {subscribers.map((s) => (
                <tr key={s.id} className="border-b border-white/5">
                  <td className="px-5 py-3 text-white/85">{s.email}</td>
                  <td className="px-5 py-3 text-white/55">{s.name || "—"}</td>
                  <td className="px-5 py-3 text-white/55">
                    <span className="border border-white/15 px-2 py-0.5 text-[10px] uppercase tracking-[0.1em]">
                      {s.source}
                    </span>
                  </td>
                  <td className="px-5 py-3 text-white/45">
                    {new Date(s.created_at).toLocaleString("tr-TR")}
                  </td>
                </tr>
              ))}
              {subscribers.length === 0 && !error && (
                <tr>
                  <td colSpan={4} className="px-5 py-10 text-center text-white/35">
                    Henüz abone yok.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
