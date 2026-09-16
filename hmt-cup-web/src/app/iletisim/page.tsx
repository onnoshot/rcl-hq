import type { Metadata } from "next";
import { Iletisim } from "@/components/Iletisim";
import { Footer } from "@/components/Footer";

export const metadata: Metadata = {
  title: "İletişim — HMT CUP 2027",
  description: "HMT CUP 2027 hakkında sorularınız için WhatsApp veya Instagram üzerinden ulaşın.",
};

export default function IletisimPage() {
  return (
    <>
      <main>
        <div className="pt-16 sm:pt-24">
          <Iletisim />
        </div>
      </main>
      <Footer />
    </>
  );
}
