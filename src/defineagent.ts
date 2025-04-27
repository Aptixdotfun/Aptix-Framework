/**
 * Agent Definition Module
 * 
 * This file defines the metadata and configuration for AI agents
 * deployed through the Aptix Framework.
 * 
 * @version 1.2.4
 * @author Aptixdotfun
 */

/**
 * Agent details interface defining the structure of agent configuration
 */
export interface AgentDetails {
  name: string;
  symbol: string;
  initialBuyAmount: number;
  description: string;
  capabilities?: string[];
  social: {
    twitter?: string;
    telegram?: string;
    discord?: string;
    github?: string;
  };
  website: string;
  imagePath: string;
  personality: string;
  version: string;
  defaultBehavior?: string;
}

/**
 * Default agent configuration
 */
export const agentDetails: AgentDetails = {
  name: "Aptix",
  symbol: "APTX",
  initialBuyAmount: 0.05,
  description: "Powerful AI agent deployed on the Aptix Framework for Solana blockchain analysis and interaction",
  capabilities: [
    "market-analysis",
    "token-tracking",
    "trend-detection",
    "holder-analysis",
    "transaction-history"
  ],
  social: {
    twitter: "https://twitter.com/aptixdotfun",
    telegram: "https://t.me/aptixdotfun",
    discord: "https://discord.gg/aptixdotfun",
    github: "https://github.com/aptixdotfun"
  },
  website: "https://aptix.fun",
  imagePath: "src/agent_logo/aptix_logo.png",
  personality: "Helpful crypto assistant specializing in Solana token analysis and market trends",
  version: "1.2.4",
  defaultBehavior: "Provides factual, concise information about blockchain data with a friendly tone"
};
