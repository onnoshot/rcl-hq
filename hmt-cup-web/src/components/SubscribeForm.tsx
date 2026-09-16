"use client";

import { useState, type FormEvent } from "react";

const SUBSCRIBED_KEY = "hmtcup_subscribed";

export function useAlreadySubscribed() {
  if (typeof window === "undefined") return false;
  return window.localStorage.getItem(SUBSCRIBED_KEY) === "1";
}

export function SubscribeForm({
  source,
  variant = "light",
  layout = "row",
  onSuccess,
}: {
  source: "form" | "popup";
  variant?: "light" | "dark";
  layout?: "row" | "stack";
  onSuccess?: () => void;
}) {
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [status, setStatus] = useState<"idle" | "loading" | "done" | "error">(
    "idle"
  );

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (status === "loading") return;
    setStatus("loading");
    try {
      const res = await fetch("/api/subscribe", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, name, source }),
      });
      if (!res.ok) throw new Error("failed");
      window.localStorage.setItem(SUBSCRIBED_KEY, "1");
      setStatus("done");
      onSuccess?.();
    } catch {
      setStatus("error");
    }
  }

  if (status === "done") {
    return (
      <div
        className={`flex items-center justify-center gap-2.5 rounded-[var(--radius-card)] border px-6 py-4 text-sm font-semibold ${
          variant === "dark"
            ? "border-red/40 bg-red/10 text-white"
            : "border-red/30 bg-red/5 text-ink"
        }`}
      >
        <span className="h-1.5 w-1.5 rotate-45 bg-red" />
        Teşekkürler! Gelişmelerden ilk sen haberdar olacaksın.
      </div>
    );
  }

  const inputClass =
    variant === "dark"
      ? "flex-1 rounded-[var(--radius-input)] border border-white/20 bg-white/5 px-4 py-3.5 text-sm text-white placeholder:text-white/35 outline-none transition-colors focus:border-red"
      : "flex-1 rounded-[var(--radius-input)] border border-black/15 bg-white px-4 py-3.5 text-sm text-ink placeholder:text-black/35 outline-none transition-colors focus:border-red";

  const isRow = layout === "row";

  return (
    <form
      onSubmit={handleSubmit}
      className={`flex w-full flex-col gap-2.5 ${isRow ? "sm:flex-row" : ""}`}
    >
      <input
        type="text"
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="İsim (opsiyonel)"
        className={`${inputClass} ${isRow ? "sm:max-w-[160px]" : ""}`}
      />
      <input
        type="email"
        required
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="E-posta adresin"
        className={inputClass}
      />
      <button
        type="submit"
        disabled={status === "loading"}
        className="flex-shrink-0 rounded-[var(--radius-pill)] bg-red px-7 py-3.5 text-[13px] font-semibold text-white transition-all active:scale-95 hover:bg-red-bright disabled:opacity-60"
      >
        {status === "loading" ? "Gönderiliyor..." : "Haberdar Ol"}
      </button>
      {status === "error" && (
        <p className="text-xs text-red-bright">
          Bir şeyler ters gitti, tekrar dener misin?
        </p>
      )}
    </form>
  );
}
