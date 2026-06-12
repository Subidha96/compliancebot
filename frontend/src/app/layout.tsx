import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'ComplianceBot+',
  description: 'GRC Awareness Chatbot for Women in Kathmandu\'s Tech Workforce',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="font-body antialiased">
        {children}
      </body>
    </html>
  );
}
