"use client"

import { motion } from "framer-motion"
import { Info, Github, ExternalLink } from "lucide-react"

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-zinc-950 pt-24">
      <div className="max-w-4xl mx-auto px-4 py-16">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-zinc-900 border border-zinc-800 mb-6">
            <Info className="w-8 h-8 text-white" />
          </div>
          <h1
            className="text-4xl sm:text-5xl font-bold text-white mb-4"
            style={{ fontFamily: "var(--font-instrument-sans)" }}
          >
            About Project
          </h1>
          <p className="text-zinc-400">Open source licensing and project information</p>
        </motion.div>

        {/* Content */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="prose prose-invert max-w-none"
        >
          <div className="p-8 rounded-2xl bg-zinc-900 border border-zinc-800">
            <div className="space-y-8 text-zinc-300">
              <div className="space-y-4">
                <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
                  Anode Cover Inspector Tool
                </h2>
                
                <div className="p-6 rounded-xl bg-zinc-950 border border-zinc-800 font-mono text-sm leading-relaxed">
                  <p className="text-zinc-300">
                    <span className="text-white font-semibold">Press Metal Bintulu - Anode Cover Inspection Tool.</span>
                  </p>
                  <p className="mt-4">
                    Powered by open-source software under the <span className="text-emerald-500">GPLv3 License</span>.
                  </p>
                  <p className="mt-4">
                    Based on the <span className="text-white">Anode Cover Inspector</span> project.
                  </p>
                </div>
              </div>

              <div className="pt-6 border-t border-zinc-800">
                <h3 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                  <Github className="w-5 h-5" />
                  Source Code
                </h3>
                <p className="mb-6">
                  This project is built upon the open-source Anode Cover Inspector framework. You can find the original source code and contribute to the core project on GitHub.
                </p>
                
                <a 
                  href="https://github.com/Tonailhan/ac-inspect" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-white text-zinc-950 font-medium hover:bg-zinc-200 transition-colors"
                >
                  View on GitHub
                  <ExternalLink className="w-4 h-4" />
                </a>
              </div>

              <div className="pt-6 border-t border-zinc-800">
                <p className="text-sm text-zinc-500 italic">
                  Developed for industrial excellence and operational safety at Press Metal Bintulu.
                </p>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
