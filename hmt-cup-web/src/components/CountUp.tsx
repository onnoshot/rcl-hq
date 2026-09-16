"use client";

import { useEffect, useRef } from "react";
import { useInView, useMotionValue, animate } from "framer-motion";

export function CountUp({
  to,
  suffix = "",
  prefix = "",
  duration = 1.8,
  className,
}: {
  to: number;
  suffix?: string;
  prefix?: string;
  duration?: number;
  className?: string;
}) {
  const ref = useRef<HTMLSpanElement>(null);
  const inView = useInView(ref, { once: true, margin: "-10% 0px -10% 0px" });
  const count = useMotionValue(0);

  useEffect(() => {
    if (!inView) return;
    const controls = animate(count, to, {
      duration,
      ease: [0.16, 0.6, 0.35, 1],
      onUpdate: (v) => {
        if (ref.current) {
          ref.current.textContent = `${prefix}${Math.round(v)}${suffix}`;
        }
      },
    });
    return () => controls.stop();
  }, [inView, to, duration, count, prefix, suffix]);

  return (
    <span ref={ref} className={className}>
      {prefix}0{suffix}
    </span>
  );
}
