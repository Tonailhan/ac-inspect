"use client"

import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { FileText, Shield, Scale, AlertTriangle } from "lucide-react"

const sections = [
  {
    id: "disclaimer",
    title: "Operational Disclaimer",
    icon: AlertTriangle,
    color: "text-amber-500",
  },
  {
    id: "privacy",
    title: "Privacy Policy",
    icon: Shield,
    color: "text-blue-500",
  },
  {
    id: "terms",
    title: "Terms of Use",
    icon: Scale,
    color: "text-purple-500",
  },
]

export default function LegalPage() {
  const [activeSection, setActiveSection] = useState("disclaimer")
  const [lastUpdated, setLastUpdated] = useState<string>("")

  useEffect(() => {
    setLastUpdated(new Date().toLocaleDateString())
  }, [])

  return (
    <div className="min-h-screen bg-zinc-950 pt-24">
      <div className="max-w-4xl mx-auto px-4 py-16">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h1
            className="text-4xl sm:text-5xl font-bold text-white mb-4"
            style={{ fontFamily: "var(--font-instrument-sans)" }}
          >
            Legal Information
          </h1>
          <p className="text-zinc-400">Important information about using the PMB Inspector Tool</p>
        </motion.div>

        {/* Navigation */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="flex flex-wrap justify-center gap-4 mb-12"
        >
          {sections.map((section) => {
            const Icon = section.icon
            return (
              <button
                key={section.id}
                onClick={() => setActiveSection(section.id)}
                className={`flex items-center gap-2 px-6 py-3 rounded-full border transition-all duration-200 ${activeSection === section.id
                    ? "bg-zinc-800 border-zinc-600 text-white"
                    : "bg-zinc-900 border-zinc-800 text-zinc-400 hover:border-zinc-700 hover:text-white"
                  }`}
              >
                <Icon className={`w-4 h-4 ${section.color}`} />
                <span className="font-medium">{section.title}</span>
              </button>
            )
          })}
        </motion.div>

        {/* Content */}
        <motion.div
          key={activeSection}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="prose prose-invert max-w-none"
        >
          <div className="p-8 rounded-2xl bg-zinc-900 border border-zinc-800">
            {activeSection === "disclaimer" && (
              <div className="space-y-6 text-zinc-300">
                <h2 className="text-2xl font-bold text-white mb-4">Operational Disclaimer</h2>

                <div className="space-y-4">
                  <p>
                    <strong className="text-white">Important:</strong> This is an AI-powered tool designed for
                    industrial inspection and operational monitoring purposes only. It is not a substitute for
                    certified on-site safety audits.
                  </p>

                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">Not a Replacement for Physical Inspection</h3>
                    <p>
                      This tool should never be used as the sole basis for maintenance decisions. Always follow the
                      Press Metal Bintulu Standard Operating Procedures (SOP) and obtain physical verification from a
                      qualified potline supervisor or technician.
                    </p>
                  </div>

                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">Limitations</h3>
                    <ul className="list-disc list-inside space-y-2 ml-4">
                      <li>
                        AI detections may contain false positives/negatives and should not be the sole basis for safety critical decisions.
                      </li>
                      <li>
                        Analysis accuracy depends on the quality of the image capture provided by industrial sensors.
                      </li>
                      <li>
                        The tool may not detect all structural defects or internal carbon contaminations.
                      </li>
                    </ul>
                  </div>

                  <div className="p-4 rounded-lg bg-amber-950/30 border border-amber-800/50">
                    <p className="text-amber-200 font-medium">
                      By using this tool, you acknowledge that you understand these industrial limitations and will
                      comply with all institutional safety regulations at Press Metal Bintulu.
                    </p>
                  </div>
                </div>
              </div>
            )}

            {activeSection === "privacy" && (
              <div className="space-y-6 text-zinc-300">
                <h2 className="text-2xl font-bold text-white mb-4">Privacy Policy</h2>

                <div className="space-y-4">
                  <p>
                    <strong className="text-white">Last Updated:</strong> {lastUpdated || "January 2026"}
                  </p>

                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">Data Security</h3>
                    <p>
                      The PMB Inspector Tool processes all images locally in real-time. We do not store, save, or retain any industrial
                      images uploaded to our service to ensure operational integrity and security.
                    </p>
                  </div>

                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">What We Collect</h3>
                    <ul className="list-disc list-inside space-y-2 ml-4">
                      <li>
                        <strong className="text-white">No industrial images:</strong> Images are processed temporarily and
                        never stored
                      </li>
                      <li>
                        <strong className="text-white">Usage analytics:</strong> Anonymous usage statistics to improve
                        service quality
                      </li>
                      <li>
                        <strong className="text-white">Error logs:</strong> Technical logs for debugging (no personal
                        data included)
                      </li>
                    </ul>
                  </div>

                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">Data Security</h3>
                    <p>
                      All data transmission is encrypted using industry-standard SSL/TLS protocols. Images are processed
                      in memory only and never written to disk or databases.
                    </p>
                  </div>

                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">Third-Party Services</h3>
                    <p>
                      We may use third-party analytics services that collect anonymous usage data. These services do not
                      have access to any uploaded images or proprietary operational information.
                    </p>
                  </div>

                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">Your Rights</h3>
                    <p>
                      Since we do not store personal data or images, there is no personal data to access, modify, or
                      delete. Your privacy is protected by design.
                    </p>
                  </div>

                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">Contact</h3>
                    <p>
                      For privacy-related questions, please contact us through our GitHub repository or X (Twitter)
                      account.
                    </p>
                  </div>
                </div>
              </div>
            )}

            {activeSection === "terms" && (
              <div className="space-y-6 text-zinc-300">
                <h2 className="text-2xl font-bold text-white mb-4">Terms of Use</h2>

                <div className="space-y-4">
                  <p>
                    <strong className="text-white">Last Updated:</strong> {lastUpdated || "January 2026"}
                  </p>

                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">Acceptance of Terms</h3>
                    <p>
                      By accessing and using AC Inspect, you accept and agree to be bound by these Terms of Use. If you do
                      not agree to these terms, please do not use this service.
                    </p>
                  </div>

                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">Use License</h3>
                    <p>
                      AC Inspect is provided for educational and research purposes. You are granted a limited,
                      non-exclusive, non-transferable license to use the service in accordance with these terms.
                    </p>
                  </div>

                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">Prohibited Uses</h3>
                    <ul className="list-disc list-inside space-y-2 ml-4">
                      <li>Using the service for commercial safety-critical decisions without proper oversight</li>
                      <li>Attempting to reverse engineer or compromise the service</li>
                      <li>Uploading malicious files or attempting to exploit vulnerabilities</li>
                      <li>Using the service in violation of any applicable laws or regulations</li>
                    </ul>
                  </div>

                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">Disclaimer of Warranties</h3>
                    <p>
                      THE SERVICE IS PROVIDED "AS IS" AND "AS AVAILABLE" WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS
                      OR IMPLIED. WE DO NOT WARRANT THAT THE SERVICE WILL BE UNINTERRUPTED, ERROR-FREE, OR FREE OF
                      VIRUSES.
                    </p>
                  </div>

                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">Limitation of Liability</h3>
                    <p>
                      TO THE FULLEST EXTENT PERMITTED BY LAW, AC INSPECT AND ITS CREATORS SHALL NOT BE LIABLE FOR ANY
                      INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES ARISING FROM YOUR USE OF THE
                      SERVICE.
                    </p>
                  </div>

                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">Modifications</h3>
                    <p>
                      We reserve the right to modify these terms at any time. Continued use of the service after
                      modifications constitutes acceptance of the updated terms.
                    </p>
                  </div>

                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">Open Source</h3>
                    <p>
                      AC Inspect is an open-source project. The source code is available on GitHub under applicable open-source
                      licenses. Contributions and improvements are welcome.
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </motion.div>
      </div>
    </div>
  )
}
