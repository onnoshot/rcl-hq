import Image from "next/image";
import { INSTAGRAM_LINK, INSTAGRAM_HANDLE, WHATSAPP_LINK, SITE } from "@/lib/constants";

export function Footer() {
  return (
    <footer className="border-t border-white/10 bg-ink py-12">
      <div className="mx-auto flex max-w-6xl flex-col items-center gap-6 px-6 text-center sm:flex-row sm:justify-between sm:text-left">
        <a href="/" className="flex items-center gap-2.5">
          <Image
            src="/logo/hmt-cup-logo-white.svg"
            alt="HMT CUP"
            width={28}
            height={28}
          />
          <span className="font-display text-lg font-bold tracking-tight text-white">
            HMT <span className="text-red">CUP</span>
          </span>
        </a>

        <p className="text-[11px] text-white/35">
          © {SITE.year} HMT CUP. Tüm hakları saklıdır.
        </p>

        <div className="flex items-center gap-5">
          <a
            href={INSTAGRAM_LINK}
            target="_blank"
            rel="noopener noreferrer"
            className="text-[11px] font-semibold uppercase tracking-[0.15em] text-white/50 transition-colors hover:text-white"
          >
            @{INSTAGRAM_HANDLE}
          </a>
          <a
            href={WHATSAPP_LINK}
            target="_blank"
            rel="noopener noreferrer"
            className="text-[11px] font-semibold uppercase tracking-[0.15em] text-white/50 transition-colors hover:text-white"
          >
            WhatsApp
          </a>
        </div>
      </div>
      <div className="mx-auto mt-8 flex max-w-6xl justify-center px-6">
        <a
          href="https://uniqbee.com/?utm_source=hmtcup&utm_medium=referral&utm_campaign=footer_credit"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 rounded-full border border-white/15 px-3.5 py-1.5 transition-colors hover:border-red"
        >
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="/uniqbee.svg" alt="UniqBee" width={18} height={18} className="h-[18px] w-[18px]" />
          <span className="text-[11px] font-medium text-white/70">UniqBee Dijital Medya Ajansı</span>
        </a>
      </div>
    </footer>
  );
}
