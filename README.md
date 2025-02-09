
![Logo](https://media.discordapp.net/attachments/1333920253532569601/1333988510171926589/shdfghfdsg.png?ex=67a8bcdd&is=67a76b5d&hm=a88726545f41f5516774f094d356c67dd7f28e4912f06b237abb30faf85a8c16&=&format=webp&quality=lossless&width=960&height=191)

# AptixAI Agent Framework
##### The Aptix Framework open-source code allows users to create AI agents directly in their CLI, with Aptixbot acting as a co-pilot to help build them. The Aptix API enables interaction with the AI agents created using the Aptix Framework's open-source code.

### 🌟 Key Features
- Agent Deployment: Deploy custom AI agents onto the Solana blockchain.
- Agent Interaction: Use natural language queries to interact with deployed agents.
- Market Analysis: Fetch real-time blockchain data, including market cap, top token holders, and trading activity
- Trend Insights: Discover trending tokens and analyze trading patterns.
- Custom Queries: Execute powerful custom queries for advanced data analysis.
- Bitquery Integration: Seamlessly integrates with Bitquery APIs to fetch blockchain data.

### 🛠 Framework Capabilities:
- Token Interaction: Query token metrics such as market cap and top holders.
- Trading Analysis: Identify trending tokens and analyze transaction data.
- Customizable Commands: Easily define custom scripts for agent interaction and deployment.
- Cross-Platform: Fully compatible with modern Node.js environments.

## 🚀 Quick Start
### Prerequisites
- Node.js (>= 16.x)
- npm (or yarn) installed
- A valid Bitquery API key
- read .env.example for rest of the Prerequisites

### Installation 
1. Clone the repository
``` bash 
git clone https://github.com/aptixdotfun/aptix-framework.git
cd aptix-framework
```
2. Install dependencies:
``` bash
npm install
```
3. Set up environment variables: Create a .env file in the root directory and add the following variables:
 
```bash
PRIVATE_KEYPAIR=<YOUR_PRIVATE_KEYPAIR>
OPENAI_API_KEY=<YOUR_OPENAI_API_KEY> 
RPC_ENDPOINT=https://api.mainnet-beta.solana.com 
Add your Bitquery API in interactAgent.ts 
```
4. Build the Framework
```bash
npm run build
```

## 📜 Available Commands
1. Ask Queries to an Agent:
```bash
npm run askaptixbot {agentName} {yourQuestion}
```
   - example
   ```bash
   npm run askaptixbot Aura "What is the market cap of Solana?"
```
2. Deploy an Agent or Token:
- Go to defineAgent.ts and replace placeholders as you want. 
- Then Run,
```bash 
npm run build 
```
```bash
npm run deployaptixbot
```
- Deploys a new agent or token to the Solana blockchain.

3. Interact with an Agent:
```bash
npm run interactaptixbot {agent_name} ask "Your question"
```
- Example 
```bash
npm run interactaptixbot Aura ask "Trending token 24h"
```
4. Fetch Trending Tokens:
```bash 
npm run interactaptixbot Aura ask "Trending token 24h"
```
5. Fetch Top Token Holders:
```bash
npm run interactaptixbot Aura ask "Top holders: {mintAddress}"
```
- Example 
```bash
npm run interactaptixbot Aura ask "Top holders: 6LKbpcg2fQ84Ay3kKXVyo3bHUGe3s36g9EVbKYSupump"
```
6. Fetch Market Cap Data:
```bash
npm run interactaptixbot Aura ask "Marketcap count:{count} term:\"{term}\""
``` 
- Example
```bash
npm run interactaptixbot Aura ask "Marketcap count:50 term:\"pump\""
```
7. Fetch First Top Buyers:
```bash
npm run interactaptixbot {agentName} ask "First top {count} buyers for: {mintAddress}"
```
- Example 
```bash 
npm run interactaptixbot Aura ask "First top 10 buyers for: 6LKbpcg2fQ84Ay3kKXVyo3bHUGe3s36g9EVbKYSupump"
```
8. Trade tokens
```bash 
npm run aptixbot-trade {agent_name}
```
## Dependencies

The project utilizes the following dependencies:

| Dependency         | Version  | Description                                                                 |
|--------------------|----------|-------------------------------------------------------------------------|
| `@solana/web3.js`          | ^1.98.0  | Interact with Solana blockchain.	                             |
| `dotenv`             | ^16.4.7   | Load environment variables from a .env file.           |
| `firebase`   | ^11.1.0  | Firebase SDK for secure and scalable data storage.                          |
| `node-fetch`           | ^3.3.2  | Lightweight HTTP client for making API requests.                            |
| `openai`           | ^4.77.3  | Integration with OpenAI APIs for natural language queries.              |
| `bs58`          | ^6.0.0	  | Base58 encoding/decoding for Solana addresses.	                             |
| `form-data`             | ^4.0.1   | Handle multipart/form-data requests.          |
| `punycode`   | ^2.3.1	  | Utility for converting Unicode strings.


## Dev Dependencies

The project utilizes the following development dependencies:

| Dependency         | Version  | Purpose                                                                 |
|--------------------|----------|-------------------------------------------------------------------------|
| `typescript`          | ^5.7.3  | Strongly-typed JavaScript for scalable and reliable code.	                                      |
| `ts-node`   | ^10.9.2  | Execute TypeScript code without transpiling it first.                          |
| `tsconfig-paths`           | ^4.2.0  | Resolve module paths in TypeScript projects for better structure.                            

## 🛠 Scripts Overview
#### The framework comes with several npm scripts for ease of use:

- `npm run build`: Transpile TypeScript to JavaScript.
- `npm run askaptixbot`: Ask general questions to your AI agents.
- `npm run deployaptixbot`: Deploy a new agent to the Solana blockchain.
- `npm run interactaptixbot`: Interact with deployed agents using queries.
- `npm run aptixbot-trade`: Trade tokens on solana blockchain.

## 🔧 How It Works
- Firebase Integration: Provides secure storage and retrieval of agent-related data.
- Bitquery Integration: Fetches real-time and historical blockchain data for queries.
- Command Parsing: Processes user commands to route them to the appropriate functionality.
- Customizable Framework: Modify or extend the framework to suit your specific needs.
