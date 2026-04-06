import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ברנדיני | לוח בקרה",
  description: "לוח בקרה לניהול אתר brndini.co.il",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="he"
      dir="rtl"
      className="h-full antialiased"
    >
      <body className="min-h-full flex flex-col font-sans">{children}</body>
    </html>
  );
}
