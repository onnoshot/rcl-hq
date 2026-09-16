import { Reveal } from "./Reveal";
import { SubscribeForm } from "./SubscribeForm";
import { SITE } from "@/lib/constants";

export function Newsletter() {
  return (
    <section
      id="haberdar-ol"
      className="relative overflow-hidden bg-ink py-24 sm:py-32"
    >
      <div
        className="pointer-events-none absolute inset-0"
        style={{
          background:
            "radial-gradient(ellipse 60% 60% at 50% 50%, rgba(204,0,0,0.15) 0%, transparent 60%)",
        }}
      />
      <div className="relative mx-auto max-w-2xl px-6 text-center">
        <Reveal>
          <span className="mb-4 inline-block rounded-full border border-white/12 bg-white/5 px-3.5 py-1 text-[11px] font-semibold tracking-wide text-red-bright">
            Haberdar Ol
          </span>
          <h2 className="font-display mb-5 text-4xl font-extrabold leading-[1.05] tracking-tight text-white sm:text-5xl">
            Tarih ve tesis detayları
            <br />
            <span className="text-red">yakında açıklanacak.</span>
          </h2>
          <p className="mx-auto mb-9 max-w-md text-[14px] leading-relaxed text-white/55">
            E-posta adresini bırak, HMT CUP {SITE.year} ile ilgili tüm
            gelişmeleri ilk sen öğren.
          </p>
          <SubscribeForm source="form" variant="dark" />
        </Reveal>
      </div>
    </section>
  );
}
