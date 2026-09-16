import { Reveal } from "./Reveal";
import { MediaFrame } from "./MediaFrame";

const voices = [
  {
    role: "Hoca",
    src: "/images/roportaj-hoca.webp",
    quote:
      "Genç oyuncularımın gerçek bir turnuva atmosferinde, scoutların önünde oynama şansı bulması paha biçilemez.",
  },
  {
    role: "Futbolcu",
    src: "/images/roportaj-futbolcu.webp",
    quote:
      "Büyük bir sahnede oynamak, arkadaşlarımla birlikte kazanmak — bunun için sabırsızlanıyorum.",
  },
];

export function Roportajlar() {
  return (
    <section className="relative bg-ink-2 py-24 sm:py-32">
      <div className="mx-auto max-w-6xl px-6">
        <Reveal className="mb-14 text-center">
          <span className="mb-4 inline-block rounded-full border border-white/12 bg-white/5 px-3.5 py-1 text-[11px] font-semibold tracking-wide text-red-bright">
            Sesler
          </span>
          <h2 className="font-display text-4xl font-extrabold tracking-tight text-white sm:text-5xl">
            Hocalar ve futbolcular konuşuyor
          </h2>
        </Reveal>

        <div className="grid gap-6 sm:grid-cols-2">
          {voices.map((v, i) => (
            <Reveal key={v.role} delay={i * 0.1}>
              <div className="group overflow-hidden rounded-[var(--radius-card)] border border-white/10 bg-ink transition-all hover:-translate-y-1 hover:border-white/20">
                <div className="relative aspect-[16/10]">
                  <MediaFrame
                    src={v.src}
                    alt={`${v.role} röportajı`}
                    className="h-full w-full"
                    hoverZoom={false}
                  />
                </div>
                <div className="relative p-7">
                  <span className="font-display absolute right-5 top-3 text-6xl font-extrabold text-white/[0.04]">
                    &rdquo;
                  </span>
                  <span className="mb-3 inline-block text-[10px] font-bold uppercase tracking-[0.2em] text-red">
                    {v.role}
                  </span>
                  <p className="font-display relative text-xl font-semibold leading-snug tracking-tight text-white/85">
                    &ldquo;{v.quote}&rdquo;
                  </p>
                </div>
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}
