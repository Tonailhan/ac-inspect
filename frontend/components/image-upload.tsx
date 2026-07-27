"use client"

import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { motion } from 'framer-motion'
import { Upload, Image, X } from 'lucide-react'

interface ImageUploadProps {
  onUpload: (file: File) => void
  onClear?: () => void
  loading?: boolean
}

export function ImageUpload({ onUpload, onClear, loading = false }: ImageUploadProps) {
  const [preview, setPreview] = useState<string | null>(null)
  const [fileName, setFileName] = useState('')

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (file) {
      setFileName(file.name)
      const reader = new FileReader()
      reader.onload = () => {
        setPreview(reader.result as string)
      }
      reader.readAsDataURL(file)
      onUpload(file)
    }
  }, [onUpload])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.gif', '.bmp']
    },
    multiple: false,
    disabled: loading
  })

  const clearImage = () => {
    setPreview(null)
    setFileName('')
    onClear?.()
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-white mb-2">Upload Anode Image</h2>
        <p className="text-zinc-400">Drag and drop your anode cover image or click to browse</p>
      </div>

      {!preview ? (
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-200 ${
            isDragActive 
              ? 'border-zinc-600 bg-zinc-900/50' 
              : 'border-zinc-800 hover:border-zinc-600 hover:bg-zinc-900/30'
          } ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          <input {...getInputProps()} />
          <motion.div
            animate={isDragActive ? { scale: 1.1 } : { scale: 1 }}
            transition={{ duration: 0.2 }}
          >
            <Upload className={`w-16 h-16 mx-auto mb-4 ${
              isDragActive ? 'text-white' : 'text-zinc-500'
            }`} />
          </motion.div>
          <p className="text-lg font-medium text-white mb-2">
            {isDragActive ? 'Drop the image here' : 'Choose an anode cover image'}
          </p>
          <p className="text-sm text-zinc-500">
            Supports JPEG, PNG, GIF, BMP (Max 10MB)
          </p>
        </div>
      ) : (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="relative"
        >
          <div className="rounded-2xl bg-zinc-900 border border-zinc-800 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <Image className="w-6 h-6 text-white" />
                <span className="font-medium text-white">{fileName}</span>
              </div>
              {!loading && (
                <motion.button
                  onClick={clearImage}
                  className="p-2 text-zinc-400 hover:text-red-400 transition-colors"
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                >
                  <X className="w-5 h-5" />
                </motion.button>
              )}
            </div>
            <div className="relative">
              <img
                src={preview}
                alt="Anode preview"
                className="w-full h-64 object-contain rounded-lg border border-zinc-800"
              />
              {loading && (
                <div className="absolute inset-0 bg-zinc-950/80 rounded-lg flex items-center justify-center">
                  <div className="text-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white mx-auto mb-2"></div>
                    <p className="text-sm text-zinc-400">Processing...</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </motion.div>
      )}

      <div className="text-center">
        <p className="text-xs text-zinc-500">
          Your image is processed locally and not stored on our servers
        </p>
      </div>
    </div>
  )
}
