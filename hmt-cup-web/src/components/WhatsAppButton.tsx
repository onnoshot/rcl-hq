"use client";

import { usePathname } from "next/navigation";
import { WHATSAPP_LINK } from "@/lib/constants";

export function WhatsAppButton() {
  const pathname = usePathname();
  if (pathname.startsWith("/admin")) return null;

  return (
    <a
      href={WHATSAPP_LINK}
      target="_blank"
      rel="noopener noreferrer"
      aria-label="WhatsApp'tan yaz"
      className="fixed bottom-24 right-5 z-[90] flex h-14 w-14 items-center justify-center rounded-full bg-[#25D366] shadow-[0_8px_24px_rgba(0,0,0,0.35)] transition-transform hover:scale-105 lg:bottom-6 lg:right-6"
    >
      <span className="absolute inset-0 rounded-full bg-[#25D366] animate-pulse-ring" />
      <svg
        width="26"
        height="26"
        viewBox="0 0 24 24"
        fill="none"
        className="relative"
      >
        <path
          d="M20.5 3.5A11 11 0 0 0 3.6 17.3L2 22l4.8-1.6a11 11 0 1 0 13.7-16.9Z"
          fill="white"
        />
        <path
          d="M8 8.4c.3-.7.6-.7 1-.7h.6c.2 0 .5 0 .7.5.3.6.9 2 .9 2.2.1.2.1.4 0 .6-.2.3-.3.4-.5.7-.2.2-.4.4-.2.8.3.5 1.1 1.6 2.2 2.4 1.4 1 2.1 1.3 2.4 1.5.3.1.4.1.6-.1.2-.3.8-1 1-1.3.2-.3.4-.2.7-.1.3.1 2 .9 2.3 1.1.3.1.5.2.6.3.1.2.1 1-.3 2-.3 1-2.2 1.9-3 1.9-.8 0-.8.6-4.9-1.1S6 13.4 6 12.6c0-.8.3-3.5.8-4.2Z"
          fill="#25D366"
        />
      </svg>
    </a>
  );
}
