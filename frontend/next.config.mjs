/** @type {import('next').NextConfig} */
const nextConfig = {
  typescript: {
    ignoreBuildErrors: process.env.NODE_ENV === 'development',
  },
  images: {
    unoptimized: true,
  },
  allowedDevOrigins: [
    'http://10.20.113.136:3000', // current LAN IP (showcase)
    'http://10.20.112.1:3000',
    'http://10.20.112.240:3000',
    'http://192.168.56.1:3000',
  ],
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:5001/api/:path*',
      },
    ]
  },
}

export default nextConfig

