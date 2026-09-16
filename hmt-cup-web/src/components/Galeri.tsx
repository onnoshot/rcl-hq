import { Reveal } from "./Reveal";
import { MediaFrame } from "./MediaFrame";

const items = [
  { label: "Maç Anı", src: "/images/galeri-mac.webp", span: "sm:col-span-2 sm:row-span-2" },
  { label: "Kupa Kaldırma", src: "/images/galeri-kupa.webp" },
  { label: "Röportaj", src: "/images/galeri-roportaj.webp" },
  { label: "Atmosfer", src: "/images/galeri-atmosfer.webp" },
  { label: "Ödül Töreni", src: "/images/galeri-odul-toreni.webp", span: "sm:col-span-2" },
];

export function Galeri() {
  return (
    <section id="galeri" className="relative bg-ink-2 py-24 sm:py-32">
      <div className="mx-auto max-w-6xl px-6">
        <Reveal className="mb-14 text-center">
          <span className="mb-4 inline-block rounded-full border border-white/12 bg-white/5 px-3.5 py-1 text-[11px] font-semibold tracking-wide text-red-bright">
            Galeri
          </span>
          <h2 className="font-display text-4xl font-extrabold tracking-tight text-white sm:text-5xl">
            Sahadan öne çıkanlar
          </h2>
        </Reveal>

        <div className="grid auto-rows-[160px] grid-cols-2 gap-2.5 sm:grid-cols-4 sm:auto-rows-[210px]">
          {items.map((it, i) => (
            <Reveal key={it.label} delay={i * 0.06} className={it.span}>
              <div className="group relative h-full w-full">
                <MediaFrame src={it.src} alt={it.label} className="h-full w-full" />
                <div className="pointer-events-none absolute inset-0 flex items-end rounded-[var(--radius-media)] bg-gradient-to-t from-black/55 via-transparent to-transparent p-3.5 opacity-0 transition-opacity duration-300 group-hover:opacity-100">
                  <span className="text-[11px] font-bold tracking-tight text-white">
                    {it.label}
                  </span>
                </div>
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}
