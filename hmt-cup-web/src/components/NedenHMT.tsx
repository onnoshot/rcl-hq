"use client";

import { Reveal, RevealStagger, staggerItem } from "./Reveal";
import { motion } from "framer-motion";

const pillars = [
  {
    n: "01",
    title: "Scout & Transfer Fırsatı",
    body: "Yurt içi ve yurt dışından kulüp gözlemcileri sahada. Her maç, bir sonraki adımın başlangıcı olabilir.",
  },
  {
    n: "02",
    title: "Sporcu Gelişimi",
    body: "Sadece rekabet değil; özgüven, takım ruhu ve sporcu kimliği kazandıran bir deneyim.",
  },
  {
    n: "03",
    title: "Unutulmaz Deneyim",
    body: "Profesyonel saha, tribün atmosferi ve ödül töreniyle çocuğunuzun hatırlayacağı bir turnuva.",
  },
];

export function NedenHMT() {
  return (
    <section id="neden" className="relative bg-ink-2 py-24 sm:py-32">
      <div className="mx-auto max-w-6xl px-6">
        <Reveal className="mb-16 text-center">
          <span className="mb-4 inline-block rounded-full border border-white/12 bg-white/5 px-3.5 py-1 text-[11px] font-semibold tracking-wide text-red-bright">
            Neden HMT CUP
          </span>
          <h2 className="font-display text-4xl font-extrabold tracking-tight text-white sm:text-5xl">
            Üç sebep, tek sahne
          </h2>
        </Reveal>

        <RevealStagger className="grid gap-4 sm:grid-cols-3">
          {pillars.map((p) => (
            <motion.div
              key={p.n}
              variants={staggerItem}
              className="group relative overflow-hidden rounded-[var(--radius-card)] border border-white/8 bg-ink-3 p-9 transition-all hover:-translate-y-1 hover:border-white/15"
            >
              <div className="absolute right-6 top-6 font-display text-6xl font-extrabold text-white/[0.04] transition-colors group-hover:text-red/10">
                {p.n}
              </div>
              <div className="relative">
                <div className="mb-6 h-px w-10 bg-red transition-all duration-300 group-hover:w-16" />
                <h3 className="font-display mb-3 text-2xl font-bold tracking-tight text-white">
                  {p.title}
                </h3>
                <p className="text-[14px] leading-relaxed text-white/50">
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
