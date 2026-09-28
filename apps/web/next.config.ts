import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  transpilePackages: ["@cop-studio/cop-types"],
};

export default nextConfig;

