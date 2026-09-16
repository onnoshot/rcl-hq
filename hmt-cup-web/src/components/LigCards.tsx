"use client";

import { motion } from "framer-motion";
import { Reveal } from "./Reveal";

function PreviewChip() {
  return (
    <span className="absolute right-4 top-4 rounded-full bg-black/40 px-2.5 py-1 text-[9px] font-bold uppercase tracking-wide text-white/70 backdrop-blur-md">
      Önizleme
    </span>
  );
}

function ComingSoonRibbon() {
  return (
    <div className="pointer-events-none absolute inset-0 z-10 flex items-center justify-center rounded-[var(--radius-card)] bg-ink/55 backdrop-blur-[2px]">
      <span className="rounded-full bg-red px-4 py-1.5 text-[11px] font-bold tracking-wide text-white shadow-lg">
        Çok Yakında
      </span>
    </div>
  );
}

function FikstürCard() {
  const rows = [1, 2, 3];
  return (
    <div className="relative overflow-hidden rounded-[var(--radius-card)] border border-white/8 bg-ink-3 p-6">
      <PreviewChip />
      <h3 className="font-display mb-4 text-base font-bold tracking-tight text-white">
        Fikstür
      </h3>
      <div className="space-y-2.5">
        {rows.map((r) => (
          <div
            key={r}
            className="flex items-center justify-between rounded-xl bg-white/5 px-3.5 py-3"
          >
            <div className="flex items-center gap-2 text-[12px] font-medium text-white/70">
              <span className="h-6 w-6 rounded-full bg-white/10" /> Takım A
            </div>
            <span className="text-[10px] font-semibold text-white/30">vs</span>
            <div className="flex items-center gap-2 text-[12px] font-medium text-white/70">
              Takım B <span className="h-6 w-6 rounded-full bg-white/10" />
            </div>
          </div>
        ))}
      </div>
      <ComingSoonRibbon />
    </div>
  );
}

function LeaderboardCard({
  title,
  accent,
}: {
  title: string;
  accent: string;
}) {
  const rows = [
    { name: "Oyuncu 1", w: 92 },
    { name: "Oyuncu 2", w: 70 },
    { name: "Oyuncu 3", w: 52 },
  ];
  return (
    <div className="relative overflow-hidden rounded-[var(--radius-card)] border border-white/8 bg-ink-3 p-6">
      <PreviewChip />
      <h3 className="font-display mb-4 text-base font-bold tracking-tight text-white">
        {title}
      </h3>
      <div className="space-y-3">
        {rows.map((row, i) => (
          <div key={row.name} className="flex items-center gap-3">
            <span className="w-4 text-[11px] font-bold text-white/30">
              {i + 1}
            </span>
            <div className="h-2 flex-1 overflow-hidden rounded-full bg-white/8">
              <motion.div
                initial={{ width: 0 }}
                whileInView={{ width: `${row.w}%` }}
                viewport={{ once: true }}
                transition={{ duration: 1, delay: i * 0.15, ease: [0.16, 1, 0.3, 1] }}
                className="h-full rounded-full"
                style={{ background: accent }}
              />
            </div>
            <span className="w-14 text-[11px] font-medium text-white/40">
              {row.name}
            </span>
          </div>
        ))}
      </div>
      <ComingSoonRibbon />
    </div>
  );
}

function MacTekrariCard() {
  return (
    <div className="relative overflow-hidden rounded-[var(--radius-card)] border border-white/8 bg-ink-3 p-6">
      <PreviewChip />
      <h3 className="font-display mb-4 text-base font-bold tracking-tight text-white">
        Maç Tekrarları
      </h3>
      <div className="flex items-center justify-center rounded-xl bg-white/5 py-8">
        <span className="flex h-12 w-12 items-center justify-center rounded-full bg-red">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="white">
            <path d="M8 5v14l11-7Z" />
          </svg>
        </span>
      </div>
      <p className="mt-3 text-[11px] text-white/35">
        Turnuva sonrası maçların tam tekrarı uygulamadan izlenebilecek.
      </p>
      <ComingSoonRibbon />
    </div>
  );
}

export function LigCards() {
  return (
    <div className="mx-auto grid max-w-5xl gap-4 px-4 sm:grid-cols-2 sm:px-6">
      <Reveal delay={0}>
        <FikstürCard />
      </Reveal>
      <Reveal delay={0.08}>
        <MacTekrariCard />
      </Reveal>
      <Reveal delay={0.16}>
        <LeaderboardCard title="Gol Krallığı" accent="#CC0000" />
      </Reveal>
      <Reveal delay={0.24}>
        <LeaderboardCard title="Asist Liderliği" accent="#D4A843" />
      </Reveal>
    </div>
  );
}
