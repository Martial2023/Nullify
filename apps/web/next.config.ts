import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'hgt7gaeh66.ufs.sh',
        pathname: '/f/**',
      },
      {
        protocol: 'https',
        hostname: 'utfs.io',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: '*.ufs.sh',
        pathname: '/f/**',
      }
    ],
  },
};

export default nextConfig;
