import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Abaco Loans Analytics',
  description: 'Customer-centric lending intelligence with governed growth for Abaco clients.',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
