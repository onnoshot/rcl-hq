"use client";

import { motion } from "framer-motion";
import { Reveal, RevealStagger, staggerItem } from "./Reveal";
import { MediaFrame } from "./MediaFrame";

const categories = [
  { title: "Şampiyonluk Kupası", body: "Turnuva birincisine." },
  { title: "Gol Kralı", body: "En golcü oyuncuya özel ödül." },
  { title: "Sürpriz Ödüller", body: "Detaylar yakında açıklanacak." },
];

export function Odul() {
  return (
    <section id="odul" className="relative overflow-hidden bg-ink py-24 sm:py-32">
      <div
        className="pointer-events-none absolute inset-0"
        style={{
          background:
            "radial-gradient(ellipse 60% 55% at 50% 100%, rgba(212,168,67,0.1) 0%, transparent 55%)",
        }}
      />
      <div className="relative mx-auto max-w-6xl px-6 text-center">
        <Reveal>
          <span className="mb-4 inline-block rounded-full border border-gold/30 bg-gold/5 px-3.5 py-1 text-[11px] font-semibold tracking-wide text-gold">
            Ödüller
          </span>
          <h2 className="font-display mb-6 text-4xl font-extrabold leading-[1.05] tracking-tight text-white sm:text-5xl">
            Kupanın ötesinde,
            <br />
            <span className="text-gold">sürpriz ödüller.</span>
          </h2>
          <p className="mx-auto mb-14 max-w-xl text-[15px] leading-relaxed text-white/55">
            Şampiyonluk kupasının yanı sıra, turnuva boyunca açıklanacak
            sürpriz ödüller de sizi bekliyor. Detaylar yakında paylaşılacak.
          </p>
        </Reveal>

        <Reveal delay={0.15}>
          <div className="relative mx-auto aspect-[16/9] max-w-3xl">
            <motion.div
              animate={{ opacity: [0.5, 0.9, 0.5] }}
              transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
              className="pointer-events-none absolute -inset-6 rounded-[36px] bg-gold/15 blur-2xl"
            />
            <MediaFrame
              src="/images/odul.webp"
              alt="Ödül töreni ve kupa"
              className="relative h-full w-full"
            />
            <div className="absolute inset-x-0 bottom-0 flex items-center justify-center gap-2 bg-gradient-to-t from-ink/90 to-transparent p-6">
              <span className="rounded-full border border-gold/50 px-4 py-1.5 text-[10px] font-bold uppercase tracking-[0.2em] text-gold">
                + Sürpriz Ödüller
              </span>
            </div>
          </div>
        </Reveal>

        <RevealStagger className="mx-auto mt-10 grid max-w-3xl gap-3 sm:grid-cols-3">
          {categories.map((c) => (
            <motion.div
              key={c.title}
              variants={staggerItem}
              className="rounded-2xl border border-gold/15 bg-ink-3 p-4 text-left transition-all hover:-translate-y-0.5 hover:border-gold/30"
            >
              <h3 className="mb-1 text-[13px] font-bold tracking-tight text-white">
                {c.title}
              </h3>
              <p className="text-[12px] leading-relaxed text-white/45">
                {c.body}
              </p>
            </motion.div>
          ))}
        </RevealStagger>
      </div>
    </section>
  );
}
