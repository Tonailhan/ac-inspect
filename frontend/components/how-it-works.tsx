"use client"

import { motion, useInView } from "framer-motion"
import { useRef } from "react"
import { Upload, Brain, Shield, BarChart3 } from "lucide-react"

const steps = [
  {
    icon: Upload,
    title: "Upload Anode Image",
    description: "Capture and upload a clear vertical image of the anode cover. Supports JPEG and PNG industrial sensor outputs.",
    color: "text-blue-500",
  },
  {
    icon: Brain,
    title: "AI Analysis",
    description: "Our industrial model identifies anomalies including carbon residuals, sand, and iron contamination.",
    color: "text-purple-500",
  },
  {
    icon: BarChart3,
    title: "Standard Verification",
    description: "Automated verification of the 3cm powder level standard below the stub. Ensures optimal potline efficiency.",
    color: "text-emerald-500",
  },
  {
    icon: Shield,
    title: "Safety Logging",
    description: "Results are logged into the PMB safety dashboard for audit trails and maintenance scheduling.",
    color: "text-amber-500",
  },
]

export function HowItWorks() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: "-100px" })

  return (
    <section id="how-it-works" ref={ref} className="py-24 px-4">
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2
            className="text-3xl sm:text-4xl font-bold text-white mb-4"
            style={{ fontFamily: "var(--font-instrument-sans)" }}
          >
            How It Works
          </h2>
          <p className="text-zinc-400 max-w-2xl mx-auto">
            Uses AI to analyze anode covers in seconds. Here's how our industrial inspection process works.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {steps.map((step, index) => {
            const Icon = step.icon
            return (
              <motion.div
                key={step.title}
                initial={{ opacity: 0, y: 20 }}
                animate={isInView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className="relative"
              >
                <div className="relative p-6 rounded-2xl bg-zinc-900 border border-zinc-800 hover:border-zinc-600 transition-all duration-300 h-full">
                  <div className={`p-3 rounded-lg bg-zinc-800 w-fit mb-4 ${step.color}`}>
                    <Icon className="w-6 h-6" strokeWidth={1.5} />
                  </div>
                  <h3 className="text-lg font-semibold text-white mb-2">{step.title}</h3>
                  <p className="text-zinc-400 text-sm leading-relaxed">{step.description}</p>
                  <div className="absolute top-6 right-6 text-4xl font-bold text-zinc-800 opacity-50">
                    {index + 1}
                  </div>
                </div>
              </motion.div>
            )
          })}
        </div>

        {/* <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.5 }}
          className="mt-16 text-center"
        >
          <div className="inline-block p-8 rounded-2xl bg-zinc-900 border border-zinc-800 max-w-3xl">
            <h3 className="text-xl font-semibold text-white mb-4">Powered by Deep Learning</h3>
            <p className="text-zinc-400 mb-4">
              Our model uses VGG16 transfer learning architecture, trained on thousands of industrial inspection images from
              reputable manufacturing datasets including COCO, ImageNet, and proprietary PMB datasets.
            </p>
            <p className="text-sm text-zinc-500">
              The model has been optimized for accuracy and speed, providing results in under 3 seconds while
              maintaining industrial-grade reliability.
            </p>
          </div>
        </motion.div> */}
      </div>
    </section>
  )
}
