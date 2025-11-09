/** @type {import('next').NextConfig} */
const nextConfig = {
  webpack: (config, { isServer }) => {
    // Handle canvas for pdfjs-dist
    if (!isServer) {
      config.resolve.alias.canvas = false;
    }

    // Configure pdfjs-dist to work with Next.js
    config.resolve.alias = {
      ...config.resolve.alias,
      canvas: false,
      encoding: false,
    };

    return config;
  },
}

module.exports = nextConfig
