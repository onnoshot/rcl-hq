"use client";

import { useEffect, useRef, useState } from "react";
import { Reveal } from "./Reveal";

const posters = [
  { src: "/videos/HMTCUP_Reklam1.mp4", label: "Tanıtım" },
  { src: "/videos/Team_Duyuru1.mp4", label: "Takım Duyurusu" },
  { src: "/videos/Roportaj1.mp4", label: "Röportaj" },
  { src: "/videos/HMT_Rop3.mp4", label: "HMT CUP" },
  { src: "/videos/HMT_Rop5.mp4", label: "HMT CUP" },
  { src: "/videos/Bahar_Rop1.mp4", label: "Röportaj" },
  { src: "/videos/Ozgur_Rop1.mp4", label: "Röportaj" },
];

function PosterCard({ src, label }: { src: string; label: string }) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const wrapRef = useRef<HTMLDivElement>(null);
  const [active, setActive] = useState(false);
  const [hovered, setHovered] = useState(false);

  useEffect(() => {
    const el = wrapRef.current;
    if (!el) return;
    const io = new IntersectionObserver(
      ([entry]) => setActive(entry.isIntersecting),
      { threshold: 0.35 }
    );
    io.observe(el);
    return () => io.disconnect();
  }, []);

  useEffect(() => {
    const v = videoRef.current;
    if (!v) return;
    if (active) {
      v.play().catch(() => {});
    } else {
      v.pause();
    }
  }, [active]);

  useEffect(() => {
    const v = videoRef.current;
    if (!v) return;
    v.muted = !hovered;
  }, [hovered, active]);

  return (
    <div
      ref={wrapRef}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      className="group relative aspect-[9/16] w-[62vw] flex-shrink-0 snap-center overflow-hidden rounded-[var(--radius-card)] border border-white/10 bg-ink-3 sm:w-[240px]"
    >
      {active && (
        <video
          ref={videoRef}
          src={src}
          muted
          loop
          playsInline
          preload="none"
          className="h-full w-full object-cover"
        />
      )}
      <div className="pointer-events-none absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-black/10" />
      <span className="absolute bottom-3 left-3 rounded-full bg-black/40 px-2.5 py-1 text-[10px] font-semibold text-white backdrop-blur-md">
        {label}
      </span>
      <span
        className={`absolute right-3 top-3 flex h-7 w-7 items-center justify-center rounded-full bg-black/50 text-white backdrop-blur-md transition-opacity duration-200 ${
          hovered ? "opacity-100" : "opacity-0"
        }`}
        aria-hidden
      >
        <svg viewBox="0 0 24 24" fill="none" className="h-3.5 w-3.5">
          <path
            d="M3 9v6h4l5 5V4L7 9H3z"
            fill="currentColor"
          />
          <path
            d="M16.5 8.5a5 5 0 0 1 0 7"
            stroke="currentColor"
            strokeWidth="1.6"
            strokeLinecap="round"
          />
          <path
            d="M19 6a8.5 8.5 0 0 1 0 12"
            stroke="currentColor"
            strokeWidth="1.6"
            strokeLinecap="round"
          />
        </svg>
      </span>
    </div>
  );
}

export function FilmPosterWall() {
  return (
    <section className="relative bg-ink py-14 sm:py-20">
      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        <Reveal className="mb-6 flex items-end justify-between">
          <div>
            <span className="mb-3 inline-block rounded-full border border-white/12 bg-white/5 px-3.5 py-1 text-[11px] font-semibold tracking-wide text-red-bright">
              Sahadan Kareler
            </span>
            <h2 className="font-display text-2xl font-extrabold tracking-tight text-white sm:text-3xl">
              HMT CUP hareket halinde
            </h2>
          </div>
        </Reveal>
      </div>

      <Reveal>
        <div className="flex snap-x snap-mandatory gap-3 overflow-x-auto px-4 pb-2 sm:px-6 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
          {posters.map((p) => (
            <PosterCard key={p.src} src={p.src} label={p.label} />
          ))}
          <div className="w-1 flex-shrink-0 sm:w-2" aria-hidden />
        </div>
      </Reveal>
    </section>
  );
}
