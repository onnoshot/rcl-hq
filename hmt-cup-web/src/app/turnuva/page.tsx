import type { Metadata } from "next";
import { TurnuvaNedir } from "@/components/TurnuvaNedir";
import { NedenHMT } from "@/components/NedenHMT";
import { Tesis } from "@/components/Tesis";
import { Konaklama } from "@/components/Konaklama";
import { Odul } from "@/components/Odul";
import { Newsletter } from "@/components/Newsletter";
import { Footer } from "@/components/Footer";

export const metadata: Metadata = {
  title: "Turnuva — HMT CUP 2027",
  description:
    "HMT CUP 2027 turnuvası hakkında her şey: neden HMT CUP, tesis ve lokasyon, konaklama ve ödüller.",
};

export default function TurnuvaPage() {
  return (
    <>
      <main>
        <div className="pt-16 sm:pt-24">
          <TurnuvaNedir />
        </div>
        <NedenHMT />
        <Tesis />
        <Konaklama />
        <Odul />
        <Newsletter />
      </main>
      <Footer />
    </>
  );
}
