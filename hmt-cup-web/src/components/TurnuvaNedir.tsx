import { Reveal } from "./Reveal";
import { CountUp } from "./CountUp";
import { SITE } from "@/lib/constants";

const stats = [
  { to: 32, suffix: "+", label: "Takım" },
  { to: 6, suffix: "", label: "Saha" },
  { to: 3, suffix: "", label: "Yaş Kategorisi" },
  { to: 1, suffix: "", label: "Şehir · " + SITE.city },
];

export function TurnuvaNedir() {
  return (
    <section id="turnuva" className="relative bg-ink py-24 sm:py-32">
      <div className="mx-auto max-w-5xl px-6 text-center">
        <Reveal>
          <span className="mb-4 inline-block rounded-full border border-white/12 bg-white/5 px-3.5 py-1 text-[11px] font-semibold tracking-wide text-red-bright">
            Turnuva Nedir
          </span>
          <h2 className="font-display text-4xl font-extrabold leading-[1.05] tracking-tight text-white sm:text-6xl">
            Sahaya çıkmak için bir sebep değil,
            <br />
            <span className="text-red">unutulmayacak bir sahne.</span>
          </h2>
          <p className="mx-auto mt-6 max-w-2xl text-[15px] leading-relaxed text-white/55">
            HMT CUP, genç futbolcuların yeteneklerini gerçek bir turnuva
            atmosferinde sergilediği, hocaların takımlarını öne çıkardığı ve
            ailelerin güvenle yanında olabildiği; {SITE.city}&apos;da
            düzenlenecek yeni nesil altyapı turnuvası.
          </p>
        </Reveal>

        <div className="mt-16 grid grid-cols-2 gap-3 sm:grid-cols-4">
          {stats.map((s, i) => (
            <Reveal key={s.label} delay={i * 0.08}>
              <div className="flex h-full flex-col items-center justify-center gap-1 rounded-[var(--radius-card)] border border-white/8 bg-ink-3 py-10 transition-all hover:-translate-y-1 hover:border-white/15">
                <CountUp
                  to={s.to}
                  suffix={s.suffix}
                  className="font-display text-5xl font-extrabold text-red sm:text-6xl"
                />
                <span className="text-[10px] font-bold uppercase tracking-[0.2em] text-white/45">
                  {s.label}
                </span>
              </div>
            </Reveal>
          ))}
        </div>
        <p className="mt-4 text-[10px] uppercase tracking-[0.2em] text-white/25">
          Kesin takım ve kategori sayıları yakında açıklanacak
        </p>
      </div>
    </section>
  );
}
