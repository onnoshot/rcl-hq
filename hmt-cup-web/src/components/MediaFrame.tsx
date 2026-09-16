"use client";

import Image from "next/image";
import { motion } from "framer-motion";
import type { ReactNode } from "react";

/**
 * Reusable media slot. Pass `src` once real Higgsfield-generated photography
 * exists; until then it renders a branded placeholder so layout/spacing is final.
 * Images reveal with a settling zoom on scroll and nudge further on hover.
 */
export function MediaFrame({
  src,
  alt,
  icon,
  label,
  className = "",
  priority,
  hoverZoom = true,
}: {
  src?: string;
  alt: string;
  icon?: ReactNode;
  label?: string;
  className?: string;
  priority?: boolean;
  hoverZoom?: boolean;
}) {
  if (src) {
    return (
      <div
        className={`relative overflow-hidden rounded-[var(--radius-media)] bg-ink-2 ${className}`}
      >
        <motion.div
          initial={{ scale: 1.18, opacity: 0 }}
          whileInView={{ scale: 1, opacity: 1 }}
          viewport={{ once: true, margin: "-10%" }}
          whileHover={hoverZoom ? { scale: 1.07 } : undefined}
          transition={{ duration: 1.1, ease: [0.16, 1, 0.3, 1] }}
          className="relative h-full w-full"
        >
          <Image
            src={src}
            alt={alt}
            fill
            priority={priority}
            className="object-cover"
            sizes="(max-width: 768px) 100vw, 50vw"
          />
        </motion.div>
        <div className="pointer-events-none absolute inset-0 bg-gradient-to-t from-black/15 via-transparent to-transparent" />
      </div>
    );
  }

  return (
    <div
      className={`relative flex flex-col items-center justify-center gap-3 overflow-hidden rounded-[var(--radius-media)] bg-ink-2 ${className}`}
    >
      <div
        className="absolute inset-0 opacity-40"
        style={{
          background:
            "radial-gradient(ellipse 80% 60% at 50% 20%, rgba(204,0,0,0.18) 0%, transparent 60%)",
        }}
      />
      <div
        className="absolute inset-0 opacity-[0.06]"
        style={{
          backgroundImage:
            "linear-gradient(rgba(255,255,255,.6) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.6) 1px, transparent 1px)",
          backgroundSize: "36px 36px",
        }}
      />
      <div className="relative z-10 flex flex-col items-center gap-3 px-6 text-center">
        {icon ?? (
          <svg
            width="30"
            height="30"
            viewBox="0 0 24 24"
            fill="none"
            className="opacity-30"
          >
            <path
              d="M4 16l4.5-6 3.5 4 2.5-3L20 16"
              stroke="white"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <rect
              x="3"
              y="4"
              width="18"
              height="16"
              rx="1.5"
              stroke="white"
              strokeWidth="1.5"
              opacity="0.5"
            />
          </svg>
        )}
        {label && (
          <span className="text-[9px] font-bold uppercase tracking-[0.25em] text-white/25">
            {label}
          </span>
        )}
      </div>
    </div>
  );
}
