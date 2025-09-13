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
        hostname: 'image-gallery-wcle.onrender.com',
        port: '',
        pathname: '/static/uploads/**',
      },
    ],
  },
};

module.exports = nextConfig;

