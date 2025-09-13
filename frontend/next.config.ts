import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  typescript: {
    ignoreBuildErrors: true, // <-- allow building even with TS errors
  },
};

export default nextConfig;
