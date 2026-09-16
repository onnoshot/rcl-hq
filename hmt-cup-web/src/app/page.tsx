import { Hero } from "@/components/Hero";
import { FilmPosterWall } from "@/components/FilmPosterWall";
import { HomeWhy } from "@/components/HomeWhy";
import { HomeTeasers } from "@/components/HomeTeasers";
import { HomeLigPreview } from "@/components/HomeLigPreview";
import { HomeQuote } from "@/components/HomeQuote";
import { Newsletter } from "@/components/Newsletter";
import { Footer } from "@/components/Footer";
import { NewsletterPopup } from "@/components/NewsletterPopup";

export default function Home() {
  return (
    <>
      <main>
        <Hero />
        <FilmPosterWall />
        <HomeWhy />
        <HomeTeasers />
        <HomeLigPreview />
        <HomeQuote />
        <Newsletter />
      </main>
      <Footer />
      <NewsletterPopup />
    </>
  );
}
