"use client";

import { useRouter } from "next/navigation";

export function LogoutButton() {
  const router = useRouter();
  return (
    <button
      onClick={async () => {
        await fetch("/api/admin/logout", { method: "POST" });
        router.push("/admin/login");
        router.refresh();
      }}
      className="bg-red px-5 py-2.5 text-[10px] font-bold uppercase tracking-[0.2em] text-white transition-colors hover:bg-red-bright"
    >
      Çıkış Yap
    </button>
  );
}
