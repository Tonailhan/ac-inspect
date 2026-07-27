"use client"

import { motion } from "framer-motion"
import { CheckCircle, XCircle, TrendingUp, Clock, Shield } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"

interface ResultDisplayProps {
  result: {
    status: string
    confidence: number
    timestamp: string
  }
}

export function ResultDisplay({ result }: ResultDisplayProps) {
  const isNormal = result.status === 'OK'
  const confidence = parseFloat(result.confidence.toString())

  const getConfidenceColor = (conf: number) => {
    if (conf >= 0.9) return 'text-emerald-500'
    if (conf >= 0.8) return 'text-blue-500'
    if (conf >= 0.7) return 'text-yellow-500'
    return 'text-red-500'
  }

  const getConfidenceText = (conf: number) => {
    if (conf >= 0.9) return 'Very High'
    if (conf >= 0.8) return 'High'
    if (conf >= 0.7) return 'Moderate'
    return 'Low'
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-2xl bg-zinc-900 border border-zinc-800 p-6"
    >
      <div className="flex items-start space-x-4">
        <div className="flex-shrink-0">
          {isNormal ? (
            <CheckCircle className="w-12 h-12 text-emerald-500" />
          ) : (
            <XCircle className="w-12 h-12 text-red-500" />
          )}
        </div>

        <div className="flex-1">
          <div className="flex items-center space-x-3 mb-4">
            <h3 className="text-2xl font-bold text-white">
              {isNormal ? 'Standard Met' : 'Defect Detected'}
            </h3>
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${
              isNormal 
                ? 'bg-emerald-500/20 text-emerald-400' 
                : 'bg-red-500/20 text-red-400'
            }`}>
              {result.status}
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div className="space-y-4">
              <Card className="bg-zinc-950 border-zinc-800">
                <CardContent className="flex items-center justify-between p-4">
                  <div className="flex items-center space-x-3">
                    <TrendingUp className="w-5 h-5 text-white" />
                    <span className="font-medium text-zinc-300">Confidence</span>
                  </div>
                  <div className="text-right">
                    <div className={`text-lg font-bold ${getConfidenceColor(confidence)}`}>
                      {(confidence * 100).toFixed(1)}%
                    </div>
                    <div className="text-sm text-zinc-500">
                      {getConfidenceText(confidence)}
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-zinc-950 border-zinc-800">
                <CardContent className="flex items-center justify-between p-4">
                  <div className="flex items-center space-x-3">
                    <Clock className="w-5 h-5 text-white" />
                    <span className="font-medium text-zinc-300">Analysis Time</span>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-bold text-white">
                      {new Date(result.timestamp).toLocaleTimeString()}
                    </div>
                    <div className="text-sm text-zinc-500">
                      {new Date(result.timestamp).toLocaleDateString('en-GB')}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            <div className="space-y-4">


              <Card className="bg-zinc-950 border-zinc-800">
                <CardContent className="p-4">
                  <h4 className="font-medium text-zinc-300 mb-2">Technical Finding:</h4>
                  <p className="text-sm text-zinc-400">
                    {isNormal 
                      ? "Standard Met: Powder profile appears visually normal based on training data."
                      : "Anomaly Detected: Inspect for irregular powder thickness, poor compactness, shaping issues, or anode cover drops."
                    }
                  </p>
                </CardContent>
              </Card>
            </div>
          </div>


        </div>
      </div>
    </motion.div>
  )
}
