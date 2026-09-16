"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";
import Image from "next/image";

export default function AdminLoginPage() {
  const router = useRouter();
  const [password, setPassword] = useState("");
  const [error, setError] = useState(false);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(false);
    const res = await fetch("/api/admin/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password }),
    });
    setLoading(false);
    if (res.ok) {
      router.push("/admin");
      router.refresh();
    } else {
      setError(true);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-ink px-6">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-sm border border-white/10 bg-ink-2 p-8"
      >
        <div className="mb-8 flex flex-col items-center text-center">
          <Image
            src="/logo/hmt-cup-logo-white.svg"
            alt="HMT CUP"
            width={40}
            height={40}
            className="mb-4"
          />
          <h1 className="font-display text-2xl tracking-wide text-white">
            Admin Girişi
          </h1>
        </div>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Şifre"
          autoFocus
          className="mb-4 w-full border border-white/20 bg-white/5 px-4 py-3.5 text-sm text-white outline-none transition-colors focus:border-red"
        />
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-red py-3.5 text-xs font-bold uppercase tracking-[0.2em] text-white transition-colors hover:bg-red-bright disabled:opacity-60"
        >
          {loading ? "Kontrol ediliyor..." : "Giriş Yap"}
        </button>
        {error && (
          <p className="mt-3 text-center text-xs text-red-bright">
            Şifre hatalı.
          </p>
        )}
      </form>
    </div>
  );
}
