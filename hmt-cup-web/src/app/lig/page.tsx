import type { Metadata } from "next";
import { PageHeader } from "@/components/PageHeader";
import { LigCards } from "@/components/LigCards";
import { Newsletter } from "@/components/Newsletter";
import { Footer } from "@/components/Footer";

export const metadata: Metadata = {
  title: "Lig & İstatistikler — HMT CUP 2027",
  description:
    "HMT CUP 2027 fikstür, gol krallığı, asist liderliği ve maç tekrarları — turnuva başladığında uygulamadan canlı takip edilecek.",
};

export default function LigPage() {
  return (
    <>
      <main>
        <PageHeader
          eyebrow="Lig & İstatistikler"
          title="Turnuva canlı"
          accent="uygulamadan takip edilecek."
          description="Fikstür, gol krallığı, asist liderliği ve maç tekrarları — turnuva başladığında hepsi tek bir yerde. Aşağıdaki kartlar önizleme amaçlıdır."
        />
        <div className="py-10 sm:py-14">
          <LigCards />
        </div>
        <Newsletter />
      </main>
      <Footer />
    </>
  );
}
