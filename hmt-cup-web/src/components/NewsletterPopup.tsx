"use client";

import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import Image from "next/image";
import { SubscribeForm } from "./SubscribeForm";

const DISMISS_KEY = "hmtcup_popup_dismissed_until";
const SUBSCRIBED_KEY = "hmtcup_subscribed";
const DISMISS_DAYS = 7;
const TRIGGER_SECONDS = 15;
const TRIGGER_SCROLL_RATIO = 0.5;

export function NewsletterPopup() {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const already = window.localStorage.getItem(SUBSCRIBED_KEY) === "1";
    const dismissedUntil = Number(
      window.localStorage.getItem(DISMISS_KEY) || 0
    );
    if (already || Date.now() < dismissedUntil) return;

    let shown = false;
    const trigger = () => {
      if (shown) return;
      shown = true;
      setOpen(true);
    };

    const timer = window.setTimeout(trigger, TRIGGER_SECONDS * 1000);

    const onScroll = () => {
      const ratio =
        window.scrollY / (document.body.scrollHeight - window.innerHeight);
      if (ratio >= TRIGGER_SCROLL_RATIO) trigger();
    };
    window.addEventListener("scroll", onScroll, { passive: true });

    return () => {
      window.clearTimeout(timer);
      window.removeEventListener("scroll", onScroll);
    };
  }, []);

  function dismiss() {
    setOpen(false);
    const until = Date.now() + DISMISS_DAYS * 24 * 60 * 60 * 1000;
    window.localStorage.setItem(DISMISS_KEY, String(until));
  }

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-[200] flex items-end justify-center bg-black/70 backdrop-blur-sm sm:items-center sm:p-6"
          onClick={dismiss}
        >
          <motion.div
            drag="y"
            dragConstraints={{ top: 0, bottom: 0 }}
            dragElastic={{ top: 0, bottom: 0.5 }}
            onDragEnd={(_, info) => {
              if (info.offset.y > 100) dismiss();
            }}
            initial={{ y: "100%" }}
            animate={{ y: 0 }}
            exit={{ y: "100%" }}
            transition={{ type: "spring", damping: 28, stiffness: 320 }}
            onClick={(e) => e.stopPropagation()}
            className="relative w-full max-w-md overflow-hidden rounded-t-[28px] border border-white/10 border-b-0 bg-ink-2 p-7 pb-9 sm:rounded-[28px] sm:border-b sm:p-10"
          >
            <div
              className="pointer-events-none absolute inset-0"
              style={{
                background:
                  "radial-gradient(ellipse 70% 60% at 50% 0%, rgba(204,0,0,0.18) 0%, transparent 60%)",
              }}
            />
            <div className="relative mb-5 flex justify-center sm:hidden">
              <span className="h-1.5 w-10 rounded-full bg-white/20" />
            </div>
            <button
              onClick={dismiss}
              aria-label="Kapat"
              className="absolute right-4 top-4 z-10 hidden h-8 w-8 items-center justify-center rounded-full text-white/50 transition-colors hover:bg-white/10 hover:text-white sm:flex"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                <path
                  d="M5 5l14 14M19 5L5 19"
                  stroke="currentColor"
                  strokeWidth="1.8"
                  strokeLinecap="round"
                />
              </svg>
            </button>

            <div className="relative flex flex-col items-center text-center">
              <Image
                src="/logo/hmt-cup-logo-white.svg"
                alt="HMT CUP"
                width={44}
                height={44}
                className="mb-5"
              />
              <h3 className="font-display mb-2 text-2xl font-extrabold leading-tight tracking-tight text-white sm:text-3xl">
                Turnuvayı kaçırma
              </h3>
              <p className="mb-7 text-[13px] leading-relaxed text-white/55">
                Tarih ve tesis detayları açıklanmadan önce e-postana haber
                verelim.
              </p>
              <SubscribeForm
                source="popup"
                variant="dark"
                layout="stack"
                onSuccess={dismiss}
              />
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
