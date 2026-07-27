import { SmoothScroll } from "@/components/smooth-scroll"
import { Navbar } from "@/components/navbar"
import { Hero } from "@/components/hero"
import { ImageAnalysis } from "@/components/image-analysis"
import { HowItWorks } from "@/components/how-it-works"
import { BentoGrid } from "@/components/bento-grid"
import { FinalCTA } from "@/components/final-cta"
import { Footer } from "@/components/footer"

export default function Home() {
  return (
    <SmoothScroll>
      <main className="min-h-screen bg-zinc-950">
        <Navbar />
        <Hero />
        <ImageAnalysis />
        <HowItWorks />
        <BentoGrid />
        <FinalCTA />
        <Footer />
      </main>
    </SmoothScroll>
  )
}
