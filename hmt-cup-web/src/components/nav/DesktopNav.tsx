"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import Image from "next/image";
import { NAV_LINKS } from "./nav-items";
import { WHATSAPP_LINK } from "@/lib/constants";

export function DesktopNav() {
  const pathname = usePathname();
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 16);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  if (pathname.startsWith("/admin")) return null;

  return (
    <header className="fixed inset-x-0 top-0 z-[100] hidden justify-center px-6 pt-5 lg:flex">
      <div
        className={`flex w-full max-w-4xl items-center justify-between rounded-full border border-white/10 bg-ink-2/70 px-5 py-2.5 backdrop-blur-2xl transition-shadow duration-300 ${
          scrolled ? "shadow-[0_12px_40px_rgba(0,0,0,0.35)]" : ""
        }`}
      >
        <Link href="/" className="flex items-center gap-2 pr-3">
          <Image
            src="/logo/hmt-cup-logo-white.svg"
            alt="HMT CUP"
            width={28}
            height={28}
          />
          <span className="font-display text-[15px] font-bold tracking-tight text-white">
            HMT <span className="text-red">CUP</span>
          </span>
        </Link>

        <nav className="flex items-center gap-1">
          {NAV_LINKS.map((l) => {
            const active = pathname.startsWith(l.href);
            return (
              <Link
                key={l.href}
                href={l.href}
                className={`rounded-full px-3.5 py-2 text-[13px] font-medium transition-colors ${
                  active
                    ? "bg-white/10 text-white"
                    : "text-white/55 hover:text-white"
                }`}
              >
                {l.label}
              </Link>
            );
          })}
        </nav>

        <a
          href={WHATSAPP_LINK}
          target="_blank"
          rel="noopener noreferrer"
          className="ml-2 rounded-full bg-red px-4 py-2 text-[13px] font-semibold text-white transition-colors hover:bg-red-bright"
        >
          Bilgi Al
        </a>
      </div>
    </header>
  );
}
