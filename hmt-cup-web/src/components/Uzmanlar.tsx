import { Reveal } from "./Reveal";
import { MediaFrame } from "./MediaFrame";

const experts: {
  role: string;
  body: string;
  src?: string;
  tags: string[];
}[] = [
  {
    role: "Spor Psikoloğu",
    body: "Maç öncesi ve sonrası zihinsel hazırlık, özgüven ve baskı yönetimi üzerine bire bir destek.",
    src: "/images/uzman-psikolog.webp",
    tags: ["Zihinsel Hazırlık", "Özgüven", "Baskı Yönetimi"],
  },
  {
    role: "Performans & Gelişim Uzmanı",
    body: "Sahadaki performansı, teknik gelişimi ve sporcu kimliğini bütünsel olarak değerlendirir.",
    src: "/images/uzman-performans.webp",
    tags: ["Performans Analizi", "Teknik Gelişim", "Sporcu Kimliği"],
  },
  {
    role: "Fizyoterapist",
    body: "Sakatlık önleme, esneklik çalışmaları ve maç sonrası toparlanma sürecinde sporcuya birebir eşlik eder.",
    tags: ["Sakatlık Önleme", "Toparlanma", "Esneklik"],
  },
  {
    role: "Saha Hekimi",
    body: "Turnuva boyunca sahada sağlık gözetimi yapar; acil müdahale ve sporcu sağlığı önceliklidir.",
    tags: ["Sağlık Gözetimi", "Acil Müdahale", "Sporcu Sağlığı"],
  },
];

export function Uzmanlar() {
  return (
    <section id="uzmanlar" className="relative bg-ink-2 py-16 sm:py-24">
      <div className="mx-auto max-w-5xl px-4 sm:px-6">
        <Reveal className="mb-10 text-center">
          <span className="mb-4 inline-block rounded-full border border-white/12 bg-white/5 px-3.5 py-1 text-[11px] font-semibold tracking-wide text-red-bright">
            Sahanın Ötesinde
          </span>
          <h2 className="font-display text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
            Gelişim, sadece skorla ölçülmez
          </h2>
          <p className="mx-auto mt-4 max-w-lg text-[14px] leading-relaxed text-white/55">
            HMT CUP boyunca sporcuların yanında, performansı ve zihinsel
            gelişimi birlikte değerlendiren bir uzman ekip yer alıyor —
            turnuva sonrası da sürecek bir bakış açısıyla.
          </p>
        </Reveal>

        <div className="grid gap-4 sm:grid-cols-2">
          {experts.map((e, i) => (
            <Reveal key={e.role} delay={i * 0.1}>
              <div className="overflow-hidden rounded-[var(--radius-card)] border border-white/8 bg-ink-3 transition-all hover:-translate-y-1 hover:border-white/15">
                <div className="relative aspect-[4/3]">
                  <MediaFrame src={e.src} alt={e.role} className="h-full w-full rounded-none" />
                </div>
                <div className="p-6">
                  <h3 className="font-display mb-2 text-lg font-bold tracking-tight text-white">
                    {e.role}
                  </h3>
                  <p className="mb-4 text-[13px] leading-relaxed text-white/50">
                    {e.body}
                  </p>
                  <div className="flex flex-wrap gap-1.5">
                    {e.tags.map((t) => (
                      <span
                        key={t}
                        className="rounded-full bg-white/5 px-2.5 py-1 text-[10px] font-semibold text-white/45"
                      >
                        {t}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}
