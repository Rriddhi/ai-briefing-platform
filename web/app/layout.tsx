import './globals.css'

export const metadata = {
  title: 'AI Briefing Platform',
  description: 'AI news and research briefing platform',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}

