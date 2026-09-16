import type { Metadata } from "next";
import { PageHeader } from "@/components/PageHeader";
import { Uzmanlar } from "@/components/Uzmanlar";
import { Roportajlar } from "@/components/Roportajlar";
import { Newsletter } from "@/components/Newsletter";
import { Footer } from "@/components/Footer";

export const metadata: Metadata = {
  title: "Gelişim — HMT CUP 2027",
  description:
    "HMT CUP 2027'de sporcu gelişimi sadece sahayla sınırlı değil — spor psikolojisi ve performans desteğiyle bütünsel bir yaklaşım.",
};

export default function GelisimPage() {
  return (
    <>
      <main>
        <PageHeader
          eyebrow="Gelişim"
          title="Sahanın ötesinde"
          accent="bir gelişim yolculuğu."
          description="Rekabet kadar özgüven, sporcu kimliği ve zihinsel dayanıklılık da önemli — HMT CUP bunu uzman desteğiyle sahaya taşıyor."
        />
        <div className="pt-6">
          <Uzmanlar />
        </div>
        <Roportajlar />
        <Newsletter />
      </main>
      <Footer />
    </>
  );
}
