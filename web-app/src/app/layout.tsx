import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Infinix Music - Premium Telegram Music Bot",
  description: "Modern, premium Telegram Web App for music streaming and YouTube API Marketplace",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen">{children}</body>
    </html>
  );
}
