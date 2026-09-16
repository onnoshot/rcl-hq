import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import Script from "next/script";
import "./globals.css";
import { DesktopNav } from "@/components/nav/DesktopNav";
import { BottomTabBar } from "@/components/nav/BottomTabBar";
import { WhatsAppButton } from "@/components/WhatsAppButton";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700", "800"],
  display: "swap",
});

export const metadata: Metadata = {
  metadataBase: new URL("https://hmtcup.com"),
  title: "HMT CUP 2027",
  description:
    "HMT CUP 2027 — Antalya'da düzenlenecek genç futbol takımları turnuvası. Scout fırsatı, unutulmaz bir sahne, gelişim odaklı bir deneyim.",
  icons: {
    icon: [
      { url: "/icons/favicon-32.png", sizes: "32x32", type: "image/png" },
      { url: "/icons/favicon-16.png", sizes: "16x16", type: "image/png" },
    ],
    apple: "/icons/apple-touch-icon.png",
  },
  openGraph: {
    title: "HMT CUP 2027",
    description:
      "Türkiye'nin yeni nesil genç futbol turnuvası. Antalya'da, Ağustos 2027.",
    type: "website",
    locale: "tr_TR",
  },
};

export const viewport: Viewport = {
  themeColor: "#0a0a0a",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="tr" className={`${inter.variable} h-full`}>
      <body className="min-h-full bg-ink text-white antialiased">
        <Script
          src="https://www.googletagmanager.com/gtag/js?id=G-S71N2XW0S4"
          strategy="afterInteractive"
        />
        <Script id="gtag-init" strategy="afterInteractive">
          {`
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());
            gtag('config', 'G-S71N2XW0S4');
          `}
        </Script>
        <DesktopNav />
        <div className="pb-[84px] lg:pb-0">{children}</div>
        <BottomTabBar />
        <WhatsAppButton />
      </body>
    </html>
  );
}
