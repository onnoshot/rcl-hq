"use client";

import { motion } from "framer-motion";
import { Reveal, RevealStagger, staggerItem } from "./Reveal";
import { MediaFrame } from "./MediaFrame";

const chips = [
  "Süper Lig altyapı sorumluları",
  "Yurt dışı kulüp scoutları",
  "Performans & potansiyel değerlendirmesi",
];

const process = [
  { step: "01", title: "Sahada Gözlem", body: "Her maç canlı izleniyor." },
  { step: "02", title: "Değerlendirme", body: "Teknik + fiziksel analiz." },
  { step: "03", title: "Görünürlük", body: "Kulüplere doğrudan erişim." },
];

export function Scout() {
  return (
    <section id="scout" className="relative overflow-hidden bg-ink py-24 sm:py-32">
      <div
        className="pointer-events-none absolute inset-0"
        style={{
          background:
            "radial-gradient(ellipse 60% 50% at 85% 15%, rgba(204,0,0,0.14) 0%, transparent 55%)",
        }}
      />
      <div className="relative mx-auto grid max-w-6xl items-center gap-14 px-6 lg:grid-cols-2 lg:gap-20">
        <Reveal className="order-2 lg:order-1">
          <div className="relative aspect-square w-full">
            <MediaFrame
              src="/images/scout.webp"
              alt="Scout tribünde gözlem yapıyor"
              className="h-full w-full"
            />
          </div>
        </Reveal>

        <div className="order-1 lg:order-2">
          <Reveal>
            <span className="mb-4 inline-block rounded-full border border-white/12 bg-white/5 px-3.5 py-1 text-[11px] font-semibold tracking-wide text-red-bright">
              Scout & Transfer
            </span>
            <h2 className="font-display mb-6 text-4xl font-extrabold leading-[1.05] tracking-tight text-white sm:text-5xl">
              Her maçı, biri
              <br />
              <span className="text-red">izliyor.</span>
            </h2>
            <p className="mb-4 max-w-md text-[15px] leading-relaxed text-white/55">
              Türkiye&apos;nin büyük kulüplerinin altyapı gözlemcileri ve
              Avrupa&apos;dan scoutlar, genç yetenekleri gerçek maç
              temposunda görebilmek için bu tarz turnuvaları takip ediyor.
              HMT CUP, sahaya çıkan her futbolcu için bu görünürlüğü tek bir
              sahnede topluyor — kariyerinin dönüm noktası burada
              başlayabilir.
            </p>
            <p className="mb-6 max-w-md text-[13px] leading-relaxed text-white/40">
              Bugünün yıldızları da bir zamanlar küçük sahalarda, tam da
              böyle turnuvalarda fark edildi. Hikaye genelde orada başlar.
            </p>
          </Reveal>

          <RevealStagger className="mb-7 flex flex-wrap gap-2.5">
            {chips.map((chip) => (
              <motion.span
                key={chip}
                variants={staggerItem}
                className="rounded-full border border-white/15 bg-white/5 px-4 py-2 text-[11px] font-semibold text-white/65"
              >
                {chip}
              </motion.span>
            ))}
          </RevealStagger>

          <RevealStagger className="grid grid-cols-3 gap-2.5">
            {process.map((p) => (
              <motion.div
                key={p.step}
                variants={staggerItem}
                className="rounded-2xl border border-white/8 bg-ink-3 p-3.5"
              >
                <span className="font-display block text-lg font-extrabold text-red-bright">
                  {p.step}
                </span>
                <h4 className="mt-1 text-[11px] font-bold tracking-tight text-white">
                  {p.title}
                </h4>
                <p className="mt-0.5 text-[10.5px] leading-snug text-white/40">
                  {p.body}
                </p>
              </motion.div>
            ))}
          </RevealStagger>
        </div>
      </div>
    </section>
  );
}
