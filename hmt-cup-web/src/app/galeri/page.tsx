import type { Metadata } from "next";
import { Galeri } from "@/components/Galeri";
import { Newsletter } from "@/components/Newsletter";
import { Footer } from "@/components/Footer";

export const metadata: Metadata = {
  title: "Galeri — HMT CUP 2027",
  description: "HMT CUP 2027'den maç anları, kupa törenleri ve saha atmosferi.",
};

export default function GaleriPage() {
  return (
    <>
      <main>
        <div className="pt-16 sm:pt-24">
          <Galeri />
        </div>
        <Newsletter />
      </main>
      <Footer />
    </>
  );
}
