import Image from "next/image";
import { Reveal } from "./Reveal";

export function HomeQuote() {
  return (
    <section className="relative bg-ink-2 py-16 sm:py-24">
      <div className="mx-auto max-w-3xl px-4 text-center sm:px-6">
        <Reveal>
          <div className="mx-auto mb-6 h-16 w-16 overflow-hidden rounded-full border-2 border-red/40">
            <Image
              src="/images/roportaj-hoca.webp"
              alt="Hoca"
              width={64}
              height={64}
              className="h-full w-full object-cover"
            />
          </div>
          <p className="font-display text-xl font-semibold leading-snug tracking-tight text-white sm:text-3xl">
            &ldquo;Genç oyuncularımın gerçek bir turnuva atmosferinde,
            scoutların önünde oynama şansı bulması paha biçilemez.&rdquo;
          </p>
          <span className="mt-5 inline-block text-[12px] font-semibold uppercase tracking-wide text-white/40">
            — Hoca
          </span>
        </Reveal>
      </div>
    </section>
  );
}
