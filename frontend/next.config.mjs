/** @type {import('next').NextConfig} */
const nextConfig = {
  typescript: {
    ignoreBuildErrors: process.env.NODE_ENV === 'development',
  },
  images: {
    unoptimized: true,
  },
  // Origins allowed to reach the Next.js dev server from other devices.
  // To open the app from a phone/tablet on the plant Wi-Fi, add THIS
  // computer's LAN IP here (run `ipconfig` to find it), then restart the
  // frontend. Without an entry, cross-origin asset requests are blocked in
  // dev mode and the page will not render correctly on other devices.
  allowedDevOrigins: [
    'http://10.20.113.136:3000',
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

