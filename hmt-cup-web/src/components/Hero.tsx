"use client";

import { motion, useScroll, useTransform } from "framer-motion";
import Image from "next/image";
import { useRef } from "react";
import { SITE } from "@/lib/constants";
import { CountUp } from "./CountUp";

const stats = [
  { to: 32, suffix: "+", label: "Takım" },
  { to: 6, suffix: "", label: "Saha" },
  { to: 3, suffix: "", label: "Kategori" },
];

export function Hero() {
  const ref = useRef<HTMLElement>(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start start", "end start"],
  });
  const imageY = useTransform(scrollYProgress, [0, 1], ["0%", "22%"]);
  const imageScale = useTransform(scrollYProgress, [0, 1], [1.06, 1.2]);
  const contentOpacity = useTransform(scrollYProgress, [0, 0.6], [1, 0]);

  return (
    <section
      ref={ref}
      id="top"
      className="relative flex min-h-[100svh] flex-col overflow-hidden bg-ink"
    >
      <motion.div
        style={{ y: imageY, scale: imageScale }}
        className="absolute inset-0"
      >
        <Image
          src="/images/galeri-mac.webp"
          alt="HMT CUP maç anı"
          fill
          priority
          className="object-cover"
          sizes="100vw"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-ink via-ink/55 to-ink/20" />
        <div className="absolute inset-0 bg-gradient-to-b from-ink/70 via-transparent to-transparent" />
      </motion.div>

      <motion.div
        style={{ opacity: contentOpacity }}
        className="relative z-10 mx-auto flex w-full max-w-5xl flex-1 flex-col justify-end px-5 pb-8 pt-32 sm:px-6 sm:pb-12">
        <motion.div
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-5 flex items-center gap-2.5"
        >
          <Image src="/logo/hmt-cup-logo-white.svg" alt="" width={26} height={26} />
          <span className="rounded-full border border-white/15 bg-white/5 px-3.5 py-1 text-[11px] font-semibold tracking-wide text-white/80 backdrop-blur-md">
            {SITE.year} · {SITE.city}
          </span>
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
          className="font-display max-w-2xl text-[3rem] font-extrabold leading-[1.02] tracking-tight text-white sm:text-7xl lg:text-[5.5rem]"
        >
          Genç yeteneğin <span className="text-red">büyük sahnesi.</span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.22 }}
          className="mt-5 max-w-md text-[15px] leading-relaxed text-white/65 sm:text-lg"
        >
          {SITE.tagline_soft}
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.34 }}
          className="mt-8 flex flex-wrap items-center gap-3"
        >
          <a
            href="/turnuva"
            className="rounded-full bg-white px-7 py-3.5 text-[13px] font-bold text-ink transition-transform active:scale-95"
          >
            Turnuvayı Keşfet
          </a>
          <a
            href="#haberdar-ol"
            className="rounded-full bg-red px-7 py-3.5 text-[13px] font-bold text-white transition-transform active:scale-95"
          >
            Haberdar Ol
          </a>
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.5 }}
          className="mt-10 flex flex-wrap items-center gap-2.5 sm:gap-3"
        >
          {stats.map((s) => (
            <div
              key={s.label}
              className="flex items-center gap-1.5 rounded-full border border-white/12 bg-white/5 px-4 py-2 backdrop-blur-md"
            >
              <CountUp
                to={s.to}
                suffix={s.suffix}
                className="font-display text-base font-extrabold text-red-bright"
              />
              <span className="text-[11px] font-semibold uppercase tracking-wide text-white/55">
                {s.label}
              </span>
            </div>
          ))}
        </motion.div>
      </motion.div>

      <motion.a
        href="#neden-ozet"
        aria-label="Aşağı kaydır"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1, delay: 1 }}
        className="relative z-10 mx-auto mb-6 hidden sm:block"
      >
        <motion.div
          animate={{ y: [0, 8, 0] }}
          transition={{ duration: 1.8, repeat: Infinity, ease: "easeInOut" }}
          className="flex h-10 w-6 items-start justify-center rounded-full border-2 border-white/30 p-1.5"
        >
          <span className="h-1.5 w-1.5 rounded-full bg-red" />
        </motion.div>
      </motion.a>
    </section>
  );
}
