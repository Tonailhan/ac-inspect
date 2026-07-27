import type React from "react"
import type { Metadata } from "next"
import { Manrope, Poppins } from "next/font/google"
import "./globals.css"

const manrope = Manrope({
  subsets: ["latin"],
  variable: "--font-manrope",
})

const poppins = Poppins({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700", "800", "900"],
  variable: "--font-poppins",
})

// Use Poppins for display/heading fonts as fallback
const calSans = poppins
const instrumentSans = poppins

export const metadata: Metadata = {
  title: "Anode Cover Inspector | Press Metal Bintulu",
  description: "AI-powered Anode Cover thickness and defect inspection tool for aluminum potline maintenance.",
  generator: 'anode-cover-inspector',
  icons: {
    icon: [
      { url: "/favicon.svg", type: "image/svg+xml" },
      { url: "/favicon.png", type: "image/png", sizes: "32x32" },
    ],
    apple: "/apple-icon.png",
  },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body className={`${manrope.variable} ${poppins.variable} font-sans antialiased`}>
        <div className="noise-overlay" aria-hidden="true" />
        {children}

      </body>
    </html>
  )
}
