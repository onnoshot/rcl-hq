"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { Reveal, RevealStagger, staggerItem } from "./Reveal";

const pillars = [
  {
    icon: (
      <path
        d="M12 3 3 7l9 4 9-4-9-4Zm-9 6v6c0 3.9 4.03 7 9 7s9-3.1 9-7V9"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    ),
    title: "Scout & Transfer",
    body: "Süper Lig altyapıları ve yurt dışı scoutlar sahada.",
  },
  {
    icon: (
      <path
        d="M12 2a5 5 0 0 1 5 5c0 2.5-2 4-2 6h-6c0-2-2-3.5-2-6a5 5 0 0 1 5-5ZM9 17h6M10 20h4"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    ),
    title: "Sporcu Gelişimi",
    body: "Özgüven, takım ruhu ve sporcu kimliği kazandıran deneyim.",
  },
  {
    icon: (
      <path
        d="M8 21h8M12 17v4M6 4h12v3a6 6 0 0 1-12 0V4Z"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    ),
    title: "Unutulmaz Deneyim",
    body: "Profesyonel saha, tribün atmosferi, ödül töreni.",
  },
];

export function HomeWhy() {
  return (
    <section id="neden-ozet" className="relative bg-ink-2 py-16 sm:py-24">
      <div className="mx-auto max-w-5xl px-4 sm:px-6">
        <Reveal className="mb-8 flex items-end justify-between gap-4">
          <div>
            <span className="mb-3 inline-block rounded-full border border-white/12 bg-white/5 px-3.5 py-1 text-[11px] font-semibold tracking-wide text-red-bright">
              Neden HMT CUP
            </span>
            <h2 className="font-display text-2xl font-extrabold tracking-tight text-white sm:text-3xl">
              Üç sebep, tek sahne
            </h2>
          </div>
          <Link
            href="/turnuva"
            className="hidden shrink-0 text-[13px] font-semibold text-red-bright sm:block"
          >
            Tümünü gör →
          </Link>
        </Reveal>

        <RevealStagger className="grid gap-3 sm:grid-cols-3">
          {pillars.map((p) => (
            <motion.div
              key={p.title}
              variants={staggerItem}
              className="flex items-start gap-4 rounded-[var(--radius-card)] border border-white/8 bg-ink-3 p-5"
            >
              <span className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full bg-red/10 text-red-bright">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                  {p.icon}
                </svg>
              </span>
              <div>
                <h3 className="mb-1 text-[15px] font-bold tracking-tight text-white">
                  {p.title}
                </h3>
                <p className="text-[13px] leading-relaxed text-white/50">
                  {p.body}
                </p>
              </div>
            </motion.div>
          ))}
        </RevealStagger>
      </div>
    </section>
  );
}
