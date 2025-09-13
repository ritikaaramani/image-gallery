import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  typescript: {
    ignoreBuildErrors: true, // <-- allow building even with TS errors
  },
  eslint: {
    ignoreDuringBuilds: true, // <-- THIS is what you're missing!
  },
};

export default nextConfig;