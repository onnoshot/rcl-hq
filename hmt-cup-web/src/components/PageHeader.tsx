import { Reveal } from "./Reveal";

export function PageHeader({
  eyebrow,
  title,
  accent,
  description,
}: {
  eyebrow: string;
  title: string;
  accent?: string;
  description?: string;
}) {
  return (
    <div className="mx-auto max-w-2xl px-5 pt-28 pb-6 text-center sm:pt-36">
      <Reveal>
        <span className="mb-4 inline-block rounded-full border border-white/12 bg-white/5 px-3.5 py-1 text-[11px] font-semibold tracking-wide text-red-bright">
          {eyebrow}
        </span>
        <h1 className="font-display text-[2.2rem] font-extrabold leading-[1.08] tracking-tight text-white sm:text-5xl">
          {title} {accent && <span className="text-red">{accent}</span>}
        </h1>
        {description && (
          <p className="mx-auto mt-4 max-w-md text-[14px] leading-relaxed text-white/55">
            {description}
          </p>
        )}
      </Reveal>
    </div>
  );
}
