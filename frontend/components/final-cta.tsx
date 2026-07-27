"use client"

import { motion, useInView } from "framer-motion"
import { useRef } from "react"
import { ArrowRight } from "lucide-react"
import { Button } from "@/components/ui/button"

export function FinalCTA() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: "-100px" })

  return (
    <section className="py-24 px-4">
      <motion.div
        ref={ref}
        initial={{ opacity: 0, y: 40 }}
        animate={isInView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
        className="max-w-4xl mx-auto text-center"
      >
        <h2
          className="text-4xl sm:text-5xl lg:text-6xl font-bold text-white mb-6 tracking-tight"
          style={{ fontFamily: "var(--font-cal-sans)" }}
        >
          Found this useful?
        </h2>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <a href="https://github.com/Tonailhan/ac-inspect" target="_blank" rel="noopener noreferrer">
            <Button
              size="lg"
              className="shimmer-btn bg-white text-zinc-950 hover:bg-zinc-200 rounded-full px-8 h-14 text-base font-medium shadow-lg shadow-white/20"
            >
              Star on GitHub
              <ArrowRight className="ml-2 w-5 h-5" />
            </Button>
          </a>
          <a href="https://instagram.com/ilhantona" target="_blank" rel="noopener noreferrer">
            <Button
              variant="outline"
              size="lg"
              className="rounded-full px-8 h-14 text-base font-medium border-zinc-800 text-zinc-300 hover:bg-zinc-900 hover:text-white hover:border-zinc-700 bg-transparent"
            >
              Say hi on Instagram
            </Button>
          </a>
        </div>

        {/* <p className="mt-8 text-sm text-zinc-500">100% free for now. No credit card required. No hidden fees.</p> */}
      </motion.div>
    </section>
  )
}
