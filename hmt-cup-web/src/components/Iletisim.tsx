"use client";

import { Reveal, RevealStagger, staggerItem } from "./Reveal";
import { motion } from "framer-motion";
import { WHATSAPP_LINK, INSTAGRAM_LINK, INSTAGRAM_HANDLE } from "@/lib/constants";

const info = [
  { label: "Hızlı Dönüş", value: "Genelde birkaç saat içinde" },
  { label: "Dil Desteği", value: "Türkçe · İngilizce" },
  { label: "Kanal", value: "WhatsApp · Instagram" },
];

export function Iletisim() {
  return (
    <section id="iletisim" className="relative bg-ink-2 py-24 sm:py-32">
      <div className="mx-auto max-w-4xl px-6 text-center">
        <Reveal>
          <span className="mb-4 inline-block rounded-full border border-white/12 bg-white/5 px-3.5 py-1 text-[11px] font-semibold tracking-wide text-red-bright">
            İletişim
          </span>
          <h2 className="font-display mb-10 text-4xl font-extrabold tracking-tight text-white sm:text-5xl">
            Sorularınız mı var?
          </h2>
        </Reveal>

        <Reveal delay={0.1}>
          <div className="grid gap-4 sm:grid-cols-2">
            <motion.a
              whileHover={{ y: -4 }}
              href={WHATSAPP_LINK}
              target="_blank"
              rel="noopener noreferrer"
              className="group flex items-center justify-center gap-3 rounded-[var(--radius-card)] border border-white/10 bg-ink-3 px-8 py-6 transition-colors hover:border-red/50 hover:bg-red/5"
            >
              <motion.svg
                whileHover={{ rotate: -8, scale: 1.1 }}
                width="22"
                height="22"
                viewBox="0 0 24 24"
                fill="none"
              >
                <path
                  d="M20.5 3.5A11 11 0 0 0 3.6 17.3L2 22l4.8-1.6a11 11 0 1 0 13.7-16.9Z"
                  stroke="#25D366"
                  strokeWidth="1.6"
                />
                <path
                  d="M8 8.4c.3-.7.6-.7 1-.7h.6c.2 0 .5 0 .7.5.3.6.9 2 .9 2.2.1.2.1.4 0 .6-.2.3-.3.4-.5.7-.2.2-.4.4-.2.8.3.5 1.1 1.6 2.2 2.4 1.4 1 2.1 1.3 2.4 1.5.3.1.4.1.6-.1.2-.3.8-1 1-1.3.2-.3.4-.2.7-.1.3.1 2 .9 2.3 1.1.3.1.5.2.6.3.1.2.1 1-.3 2-.3 1-2.2 1.9-3 1.9-.8 0-.8.6-4.9-1.1S6 13.4 6 12.6c0-.8.3-3.5.8-4.2Z"
                  fill="#25D366"
                />
              </motion.svg>
              <span className="text-sm font-bold uppercase tracking-[0.15em] text-white group-hover:text-white">
                WhatsApp&apos;tan Yaz
              </span>
            </motion.a>

            <motion.a
              whileHover={{ y: -4 }}
              href={INSTAGRAM_LINK}
              target="_blank"
              rel="noopener noreferrer"
              className="group flex items-center justify-center gap-3 rounded-[var(--radius-card)] border border-white/10 bg-ink-3 px-8 py-6 transition-colors hover:border-red/50 hover:bg-red/5"
            >
              <motion.svg
                whileHover={{ rotate: -8, scale: 1.1 }}
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
              >
                <rect
                  x="3"
                  y="3"
                  width="18"
                  height="18"
                  rx="5"
                  stroke="white"
                  strokeWidth="1.6"
                />
                <circle cx="12" cy="12" r="4" stroke="white" strokeWidth="1.6" />
                <circle cx="17.2" cy="6.8" r="1.1" fill="white" />
              </motion.svg>
              <span className="text-sm font-bold uppercase tracking-[0.15em] text-white">
                @{INSTAGRAM_HANDLE}
              </span>
            </motion.a>
          </div>
        </Reveal>

        <RevealStagger className="mx-auto mt-10 grid max-w-2xl gap-2.5 sm:grid-cols-3">
          {info.map((i) => (
            <motion.div
              key={i.label}
              variants={staggerItem}
              className="rounded-2xl border border-white/8 bg-ink-3 px-4 py-3.5"
            >
              <span className="block text-[9.5px] font-bold uppercase tracking-[0.15em] text-red-bright">
                {i.label}
              </span>
              <span className="mt-1 block text-[12.5px] font-medium text-white/60">
                {i.value}
              </span>
            </motion.div>
          ))}
        </RevealStagger>
      </div>
    </section>
  );
}
