import type { Metadata, Viewport } from "next";
import { Space_Grotesk, Inter, Geist_Mono } from "next/font/google";
import "./globals.css";

const display = Space_Grotesk({
  variable: "--font-display",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  display: "swap",
});

const body = Inter({
  variable: "--font-body",
  subsets: ["latin"],
  display: "swap",
});

const mono = Geist_Mono({
  variable: "--font-mono",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "Adarsh Kumar Singh — AI Systems Engineer",
  description:
    "Adarsh Kumar Singh (ENTITY) builds production-grade autonomous AI — multi-agent systems, RAG pipelines, guardrails and model routing engineered for the real world.",
  keywords: [
    "Adarsh Kumar Singh",
    "AI Engineer",
    "Machine Learning",
    "RAG",
    "Multi-agent systems",
    "FastAPI",
    "LLM",
  ],
  authors: [{ name: "Adarsh Kumar Singh" }],
  openGraph: {
    title: "Adarsh Kumar Singh — AI Systems Engineer",
    description:
      "Production-grade autonomous AI: multi-agent systems, RAG pipelines, guardrails and model routing.",
    type: "website",
  },
};

export const viewport: Viewport = {
  themeColor: "#05060a",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className={`${display.variable} ${body.variable} ${mono.variable}`}>
        {children}
      </body>
    </html>
  );
}
