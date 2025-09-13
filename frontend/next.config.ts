/** @type {import('next').NextConfig} */
const nextConfig = {
  typescript: {
    ignoreBuildErrors: true,
  },
  eslint: {
    ignoreDuringBuilds: true,
  },
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'your-backend.onrender.com',
        pathname: '/static/uploads/**',
      },
    ],
  },
};

module.exports = nextConfig;

