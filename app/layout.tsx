import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Mandi Mitra',
  description: 'Mandi Price Tracker',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="hi">
      <body className="bg-slate-50 antialiased min-h-screen">
        {children}
      </body>
    </html>
  );
}
