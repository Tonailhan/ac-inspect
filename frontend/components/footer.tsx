"use client"

import { motion, useInView } from "framer-motion"
import { useRef } from "react"
import { Github, Instagram } from "lucide-react"

export function Footer() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: "-50px" })

  return (
    <footer ref={ref} className="border-t border-zinc-800 bg-zinc-950">
      <div className="max-w-6xl mx-auto px-4 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="flex flex-col md:flex-row items-start gap-8"
        >
          {/* Brand */}
          <div>
            <a href="#" className="flex items-center gap-3 mb-4">
              <img src="/pmb-logo.png" alt="PMB Logo" className="w-8 h-8 object-contain" />
              <span className="font-semibold text-white uppercase tracking-wider">Inspector</span>
            </a>
            <p className="text-sm text-zinc-500 mb-4">Press Metal Bintulu Sdn. Bhd. Anode Cover Quality Inspection Tool. Automated detection and standard verification.</p>

          </div>
        </motion.div>

        {/* Bottom */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={isInView ? { opacity: 1 } : {}}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="mt-4 pt-6 border-t border-zinc-800 flex flex-col sm:flex-row items-center justify-between gap-4"
        >
          <div className="flex flex-col items-center sm:items-start gap-2">
            <p className="text-sm text-zinc-500">
              &copy; {new Date().getFullYear()}{" "}
              <a
                href="https://github.com/tonailhan"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-white transition-colors"
              >
                <span> tona1lhan </span>
              </a>  •
              <a
                href="/legal"
                className="text-sm text-zinc-500 hover:text-white transition-colors"
              >
                Legal
              </a>
              <span className="text-zinc-800 mx-2">•</span>
              <a
                href="/about"
                className="text-sm text-zinc-500 hover:text-white transition-colors"
              >
                About
              </a>
            </p>
          </div>
          <div className="flex items-center gap-4">
            <a
              href="https://instagram.com/ilhantona"
              target="_blank"
              rel="noopener noreferrer"
              className="text-zinc-500 hover:text-white transition-colors"
              aria-label="Instagram"
            >
              <Instagram className="w-5 h-5" />
            </a>
            <a
              href="https://github.com/tonailhan"
              target="_blank"
              rel="noopener noreferrer"
              className="text-zinc-500 hover:text-white transition-colors"
              aria-label="GitHub"
            >
              <Github className="w-5 h-5" />
            </a>
          </div>
        </motion.div>
      </div>
    </footer>
  )
}
