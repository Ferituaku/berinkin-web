import type { Metadata } from "next";
import { Inter, Newsreader } from "next/font/google";
import "./globals.css";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import BottomNavBar from "@/components/BottomNavBar";
import SplashScreen from "@/components/SplashScreen";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const newsreader = Newsreader({ subsets: ["latin"], variable: "--font-newsreader" });

export const metadata: Metadata = {
  title: "Berinkin | Peringkasan Informasi",
  description: "Platform peringkasan berita harian multi-dokumen otomatis.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet" />
      </head>
      <body
        className={`${inter.variable} ${newsreader.variable} bg-background text-on-background min-h-screen flex flex-col overflow-x-hidden`}
      >
        <SplashScreen>
          <Header />
          <main className="flex-grow pt-24 md:pt-32 pb-24">
            {children}
          </main>
          <Footer />
          <BottomNavBar />
        </SplashScreen>
      </body>
    </html>
  );
}
