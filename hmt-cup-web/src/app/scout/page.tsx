import type { Metadata } from "next";
import { Scout } from "@/components/Scout";
import { Newsletter } from "@/components/Newsletter";
import { Footer } from "@/components/Footer";

export const metadata: Metadata = {
  title: "Scout & Transfer — HMT CUP 2027",
  description:
    "HMT CUP 2027'yi Süper Lig altyapı sorumluları ve yurt dışı scoutlar takip ediyor.",
};

export default function ScoutPage() {
  return (
    <>
      <main>
        <div className="pt-16 sm:pt-24">
          <Scout />
        </div>
        <Newsletter />
      </main>
      <Footer />
    </>
  );
}
