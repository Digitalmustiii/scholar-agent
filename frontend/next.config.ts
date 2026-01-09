/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    turbo: {
      // Tell Turbopack the real project root
      root: __dirname
    }
  }
};

module.exports = nextConfig;
