import Link from "next/link";
import { Reveal } from "./Reveal";
import { MediaFrame } from "./MediaFrame";

const teasers = [
  {
    href: "/turnuva",
    label: "Turnuva",
    title: "Neden HMT CUP?",
    body: "Tesis, konaklama, ödüller ve gelişim odaklı bir turnuva deneyimi.",
    src: "/images/tesis.webp",
  },
  {
    href: "/scout",
    label: "Scout & Transfer",
    title: "Her maçı biri izliyor",
    body: "Süper Lig altyapıları ve yurt dışı scoutlar sahada.",
    src: "/images/scout.webp",
  },
  {
    href: "/galeri",
    label: "Galeri",
    title: "Sahadan öne çıkanlar",
    body: "Maç anları, kupa törenleri, atmosfer.",
    src: "/images/galeri-kupa.webp",
  },
  {
    href: "/gelisim",
    label: "Gelişim",
    title: "Sahanın ötesinde gelişim",
    body: "Spor psikolojisi desteğiyle sporcu kimliği inşası.",
    src: "/images/roportaj-hoca.webp",
  },
  {
    href: "/lig",
    label: "Lig & İstatistik",
    title: "Canlı takip, çok yakında",
    body: "Fikstür, gol krallığı, asist ve maç tekrarları uygulamada.",
    src: "/images/galeri-atmosfer.webp",
  },
];

export function HomeTeasers() {
  return (
    <section className="relative bg-ink py-16 sm:py-24">
      <div className="mx-auto max-w-5xl px-4 sm:px-6">
        <Reveal className="mb-8 flex items-end justify-between">
          <h2 className="font-display text-2xl font-extrabold tracking-tight text-white sm:text-3xl">
            Turnuvayı keşfet
          </h2>
        </Reveal>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {teasers.map((t, i) => (
            <Reveal key={t.href} delay={i * 0.06}>
              <Link
                href={t.href}
                className="group block overflow-hidden rounded-[var(--radius-card)] border border-white/8 bg-ink-3 transition-all hover:-translate-y-1 hover:border-white/15"
              >
                <div className="relative aspect-[4/3]">
                  <MediaFrame src={t.src} alt={t.title} className="h-full w-full rounded-none" />
                  <div className="absolute inset-0 bg-gradient-to-t from-ink/70 to-transparent" />
                  <span className="absolute left-4 top-4 rounded-full bg-black/40 px-3 py-1 text-[10px] font-semibold text-white backdrop-blur-md">
                    {t.label}
                  </span>
                </div>
                <div className="p-5">
                  <h3 className="font-display mb-1.5 text-lg font-bold tracking-tight text-white">
                    {t.title}
                  </h3>
                  <p className="text-[13px] leading-relaxed text-white/50">
                    {t.body}
                  </p>
                  <span className="mt-3 inline-flex items-center gap-1 text-[12px] font-semibold text-red-bright">
                    Devamını gör
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" className="transition-transform group-hover:translate-x-0.5">
                      <path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  </span>
                </div>
              </Link>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}
