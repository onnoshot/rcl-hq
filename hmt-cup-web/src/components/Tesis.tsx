"use client";

import { motion } from "framer-motion";
import { Reveal, RevealStagger, staggerItem } from "./Reveal";
import { MediaFrame } from "./MediaFrame";
import { CountUp } from "./CountUp";
import { SITE } from "@/lib/constants";

const features = [
  {
    title: "Profesyonel Sahalar",
    body: "Çim / suni çim, FIFA standartlarına uygun zemin.",
    icon: (
      <path
        d="M4 6h16v12H4V6Zm8 0v12M4 12h16"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    ),
  },
  {
    title: "Floodlight Aydınlatma",
    body: "Gece maçları için profesyonel saha ışıklandırması.",
    icon: (
      <path
        d="M12 2v2M4.2 4.2l1.4 1.4M2 12h2m16 0h2M18.4 5.6l1.4-1.4M9 17h6l-1 4h-4l-1-4Zm3-11a5 5 0 0 0-3 9v2h6v-2a5 5 0 0 0-3-9Z"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    ),
  },
  {
    title: "Sağlık Desteği",
    body: "Soyunma odaları ve sahada sağlık ekibi.",
    icon: (
      <path
        d="M12 21s-7-4.35-9.5-9A5.5 5.5 0 0 1 12 6a5.5 5.5 0 0 1 9.5 6c-2.5 4.65-9.5 9-9.5 9Z"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    ),
  },
  {
    title: "Aile Alanları",
    body: "Tribün ve gölgeli izleme alanları.",
    icon: (
      <path
        d="M3 20V10l9-6 9 6v10M9 20v-6h6v6"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    ),
  },
];

export function Tesis() {
  return (
    <section id="tesis" className="relative bg-ink py-24 sm:py-32">
      <div className="mx-auto grid max-w-6xl items-center gap-14 px-6 lg:grid-cols-2 lg:gap-20">
        <div>
          <Reveal>
            <span className="mb-4 inline-block rounded-full border border-white/12 bg-white/5 px-3.5 py-1 text-[11px] font-semibold tracking-wide text-red-bright">
              Tesis & Lokasyon
            </span>
            <h2 className="font-display mb-6 text-4xl font-extrabold leading-[1.05] tracking-tight text-white sm:text-5xl">
              {SITE.city}&apos;da {SITE.fieldCount} saha,
              <br />
              tek turnuva.
            </h2>
            <p className="mb-8 max-w-md text-[15px] leading-relaxed text-white/55">
              HMT CUP, {SITE.city}&apos;nın modern spor tesislerinde, aynı
              kampüs içinde {SITE.fieldCount} sahada eş zamanlı oynanacak.
              Takımlar, aileler ve scoutlar için ulaşımı kolay, konforlu tek
              bir merkez.
            </p>
          </Reveal>

          <RevealStagger className="grid grid-cols-2 gap-2.5">
            {features.map((f) => (
              <motion.div
                key={f.title}
                variants={staggerItem}
                className="rounded-2xl border border-white/8 bg-ink-3 p-4 transition-all hover:-translate-y-0.5 hover:border-white/15"
              >
                <span className="mb-2.5 flex h-8 w-8 items-center justify-center rounded-full bg-red/10 text-red-bright">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                    {f.icon}
                  </svg>
                </span>
                <h3 className="mb-1 text-[12.5px] font-bold tracking-tight text-white">
                  {f.title}
                </h3>
                <p className="text-[11.5px] leading-snug text-white/45">
                  {f.body}
                </p>
              </motion.div>
            ))}
          </RevealStagger>
        </div>

        <Reveal delay={0.15}>
          <div className="relative aspect-[4/5] w-full">
            <MediaFrame
              src="/images/tesis.webp"
              alt={`${SITE.city} HMT CUP tesisi`}
              className="h-full w-full"
            />
            <div className="absolute left-5 top-5 flex items-center gap-2 rounded-full border border-white/15 bg-ink/80 px-3.5 py-2 backdrop-blur-sm">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
                <path
                  d="M12 22s7-7.58 7-13A7 7 0 0 0 5 9c0 5.42 7 13 7 13Z"
                  stroke="#CC0000"
                  strokeWidth="1.8"
                />
                <circle cx="12" cy="9" r="2.4" stroke="#CC0000" strokeWidth="1.8" />
              </svg>
              <span className="text-[10px] font-bold uppercase tracking-[0.15em] text-white/80">
                {SITE.city}, Türkiye
              </span>
            </div>
            <div className="absolute bottom-5 right-5 flex items-center gap-1.5 rounded-full border border-white/15 bg-ink/80 px-3.5 py-2 backdrop-blur-sm">
              <CountUp
                to={6}
                className="font-display text-sm font-extrabold text-red-bright"
              />
              <span className="text-[10px] font-bold uppercase tracking-wide text-white/80">
                Saha
              </span>
            </div>
          </div>
        </Reveal>
      </div>
    </section>
  );
}
