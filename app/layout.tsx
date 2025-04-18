import { Providers } from '@/providers/Providers'

export const metadata = {
  title: 'Fashion AI',
  description: 'Turn outfits into purchasable products',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  )
}
