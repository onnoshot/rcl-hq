"use client";

import { motion } from "framer-motion";
import { Reveal } from "./Reveal";

const rows = [
  { name: "Oyuncu 1", w: 92 },
  { name: "Oyuncu 2", w: 70 },
  { name: "Oyuncu 3", w: 52 },
];

export function HomeLigPreview() {
  return (
    <section className="relative overflow-hidden bg-ink py-16 sm:py-24">
      <div
        className="pointer-events-none absolute inset-0"
        style={{
          background:
            "radial-gradient(ellipse 55% 45% at 80% 20%, rgba(204,0,0,0.12) 0%, transparent 55%)",
        }}
      />
      <div className="relative mx-auto grid max-w-5xl items-center gap-10 px-4 sm:px-6 lg:grid-cols-2 lg:gap-16">
        <Reveal>
          <span className="mb-4 inline-block rounded-full border border-white/12 bg-white/5 px-3.5 py-1 text-[11px] font-semibold tracking-wide text-red-bright">
            Lig & İstatistikler
          </span>
          <h2 className="font-display mb-4 text-3xl font-extrabold leading-[1.05] tracking-tight text-white sm:text-4xl">
            Turnuva canlı uygulamadan takip edilecek.
          </h2>
          <p className="mb-6 max-w-md text-[14px] leading-relaxed text-white/55">
            Fikstür, gol krallığı, asist liderliği ve maç tekrarları —
            turnuva başladığında hepsi tek bir yerde.
          </p>
          <a
            href="/lig"
            className="inline-block rounded-full border border-white/20 px-6 py-3 text-[13px] font-bold text-white transition-colors hover:border-white"
          >
            Lig Sayfasını Gör
          </a>
        </Reveal>

        <Reveal delay={0.1}>
          <div className="relative overflow-hidden rounded-[var(--radius-card)] border border-white/8 bg-ink-3 p-6">
            <span className="absolute right-4 top-4 rounded-full bg-black/40 px-2.5 py-1 text-[9px] font-bold uppercase tracking-wide text-white/70">
              Önizleme
            </span>
            <h3 className="font-display mb-4 text-base font-bold tracking-tight text-white">
              Gol Krallığı
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
                      transition={{
                        duration: 1,
                        delay: i * 0.15,
                        ease: [0.16, 1, 0.3, 1],
                      }}
                      className="h-full rounded-full bg-red"
                    />
                  </div>
                  <span className="w-16 text-[11px] font-medium text-white/40">
                    {row.name}
                  </span>
                </div>
              ))}
            </div>
            <div className="pointer-events-none absolute inset-0 flex items-center justify-center rounded-[var(--radius-card)] bg-ink/50 backdrop-blur-[2px]">
              <span className="rounded-full bg-red px-4 py-1.5 text-[11px] font-bold tracking-wide text-white shadow-lg">
                Çok Yakında
              </span>
            </div>
          </div>
        </Reveal>
      </div>
    </section>
  );
}
