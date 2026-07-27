"use client"

import { useState, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { AlertTriangle, XCircle } from "lucide-react"
import { ImageUpload } from "./image-upload"
import { ResultDisplay } from "./result-display"
import { healthCheck, predictImage, PredictResponse } from "../lib/api"
import { Card } from "./ui/card"

export function ImageAnalysis() {
  const [result, setResult] = useState<PredictResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [apiStatus, setApiStatus] = useState<'checking' | 'healthy' | 'unavailable'>('checking')

  useEffect(() => {
    checkApiHealth()
  }, [])

  const checkApiHealth = async () => {
    try {
      const health = await healthCheck()
      setApiStatus(health.model_loaded ? 'healthy' : 'unavailable')
    } catch (error: any) {
      if (error?.code !== 'ECONNABORTED') {
        console.warn('Anode Cover Inspector AI service unavailable')
      }
      setApiStatus('unavailable')
    }
  }

  const handleImageUpload = async (file: File) => {
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      // Convert file to base64
      const base64Image = await fileToBase64(file)

      // Always use the real API — never fabricate inspection results
      const apiResult = await predictImage(base64Image)
      setResult(apiResult)
      setApiStatus('healthy')
    } catch (err: any) {
      console.error('Analysis failed:', err)
      setError(
        err.response?.data?.detail ||
        err.response?.data?.error ||
        'Failed to analyze image. Check that the AI service is running and try again.'
      )
      if (!err.response) {
        setApiStatus('unavailable')
      }
    } finally {
      setLoading(false)
    }
  }

  const fileToBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.readAsDataURL(file)
      reader.onload = () => resolve(reader.result as string)
      reader.onerror = error => reject(error)
    })
  }

  return (
    <section id="analyze" className="py-24 px-4">
      <div className="max-w-4xl mx-auto">
        {/* API Status Indicator */}
        {apiStatus === 'checking' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mb-6"
          >
            <Card className="text-center p-6">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white mx-auto mb-2"></div>
              <p className="text-sm text-zinc-400">Checking AI service...</p>
            </Card>
          </motion.div>
        )}

        {apiStatus === 'unavailable' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mb-6"
          >
            <Card className="bg-yellow-950/50 border-yellow-800 p-4">
              <div className="flex items-start space-x-3">
                <AlertTriangle className="w-5 h-5 text-yellow-400 mt-0.5" />
                <div>
                  <h4 className="font-medium text-yellow-300 mb-1">AI Service Unavailable</h4>
                  <p className="text-sm text-yellow-400/80">
                    The inspection service is unreachable or its model is not loaded.
                    Uploads will fail until it is back online.
                  </p>
                </div>
              </div>
            </Card>
          </motion.div>
        )}

        {/* Upload Section */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
          className="mb-8"
        >
          <Card className="p-6">
            <ImageUpload onUpload={handleImageUpload} onClear={() => { setResult(null); setError(null) }} loading={loading} />
          </Card>
        </motion.div>

        {/* Error Display */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="mb-6"
            >
              <Card className="bg-red-950/50 border-red-800 p-4">
                <div className="flex items-start space-x-3">
                  <XCircle className="w-5 h-5 text-red-400 mt-0.5" />
                  <div>
                    <h4 className="font-medium text-red-300 mb-1">Analysis Failed</h4>
                    <p className="text-sm text-red-400/80">{error}</p>
                  </div>
                </div>
              </Card>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Results Display */}
        <AnimatePresence>
          {result && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <ResultDisplay result={result} />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Disclaimer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="mt-8"
        >
          <Card className="bg-amber-950/50 border-amber-800 p-4">
            <div className="flex items-start space-x-3">
              <AlertTriangle className="w-5 h-5 text-amber-400 mt-0.5" />
              <div>
                <h4 className="font-medium text-amber-300 mb-1">Potline Safety Disclaimer</h4>
                <p className="text-sm text-amber-400/80">
                  This tool is for operational guidance only. AI-detected defects must be physically verified by a qualified technician or potline supervisor. 
                  Always follow Press Metal Bintulu Standard Operating Procedures (SOP) for maintenance tasks.
                </p>
              </div>
            </div>
          </Card>
        </motion.div>
      </div>
    </section>
  )
}
