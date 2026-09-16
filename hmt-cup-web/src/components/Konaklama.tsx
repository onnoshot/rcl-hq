"use client";

import { motion } from "framer-motion";
import { Reveal, RevealStagger, staggerItem } from "./Reveal";
import { MediaFrame } from "./MediaFrame";

const points = [
  {
    title: "Güvenli Konaklama",
    body: "7/24 güvenlik ve gözetim altında, takımlara ve ailelere özel bloklar.",
    icon: (
      <path
        d="M12 2 4 6v6c0 5 3.4 8.7 8 10 4.6-1.3 8-5 8-10V6l-8-4Z"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    ),
  },
  {
    title: "Konforlu Alanlar",
    body: "Sahaya yakın, ulaşımı kolay, dinlenmeye elverişli kaliteli konaklama seçenekleri.",
    icon: (
      <path
        d="M3 20V9l9-6 9 6v11M7 20v-6h10v6"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    ),
  },
  {
    title: "Aile Dostu Hizmet",
    body: "Veliler için özel bilgilendirme ve destek hattı, tüm turnuva boyunca yanınızda.",
    icon: (
      <path
        d="M17 21v-2a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4v2M10 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8Zm8 10v-2a4 4 0 0 0-3-3.87M15 3.13A4 4 0 0 1 15 11"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    ),
  },
];

export function Konaklama() {
  return (
    <section id="konaklama" className="relative bg-ink-2 py-24 sm:py-32">
      <div className="mx-auto grid max-w-6xl items-center gap-14 px-6 lg:grid-cols-2 lg:gap-20">
        <Reveal>
          <div className="relative aspect-[4/5] w-full">
            <MediaFrame
              src="/images/konaklama.webp"
              alt="Konaklama tesisleri"
              className="h-full w-full"
            />
          </div>
        </Reveal>

        <div>
          <Reveal delay={0.1}>
            <span className="mb-4 inline-block rounded-full border border-white/12 bg-white/5 px-3.5 py-1 text-[11px] font-semibold tracking-wide text-red-bright">
              Konaklama & Aile Konforu
            </span>
            <h2 className="font-display mb-6 text-4xl font-extrabold leading-[1.05] tracking-tight text-white sm:text-5xl">
              Çocuğunuz sahada,
              <br />
              siz huzurlusunuz.
            </h2>
            <p className="mb-8 max-w-md text-[15px] leading-relaxed text-white/55">
              HMT CUP ekibi, takımların ve ailelerin turnuva boyunca güvenli
              ve konforlu bir deneyim yaşaması için konaklama sürecinin her
              adımını organize ediyor.
            </p>
          </Reveal>

          <RevealStagger className="space-y-2.5">
            {points.map((p) => (
              <motion.div
                key={p.title}
                variants={staggerItem}
                className="flex items-start gap-4 rounded-2xl border border-white/8 bg-ink-3 p-4 transition-all hover:-translate-y-0.5 hover:border-white/15"
              >
                <span className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-full bg-red/10 text-red-bright">
                  <svg width="17" height="17" viewBox="0 0 24 24" fill="none">
                    {p.icon}
                  </svg>
                </span>
                <div>
                  <h3 className="mb-0.5 text-[13px] font-bold tracking-tight text-white">
                    {p.title}
                  </h3>
                  <p className="text-[12.5px] leading-relaxed text-white/50">
                    {p.body}
                  </p>
                </div>
              </motion.div>
            ))}
          </RevealStagger>
        </div>
      </div>
    </section>
  );
}
