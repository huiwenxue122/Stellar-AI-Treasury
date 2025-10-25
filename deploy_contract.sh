#!/bin/bash

# ============================================================================
# Stellar Smart Contract Deployment Script
# ============================================================================

set -e  # Exit on error

echo "🚀 Deploying AI Treasury Vault to Stellar Testnet..."
echo ""

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo "✅ Environment variables loaded from .env"
else
    echo "❌ Error: .env file not found"
    exit 1
fi

# Check required variables
if [ -z "$STELLAR_SECRET" ]; then
    echo "❌ Error: STELLAR_SECRET not found in .env"
    exit 1
fi

if [ -z "$STELLAR_PUBLIC" ]; then
    echo "❌ Error: STELLAR_PUBLIC not found in .env"
    exit 1
fi

echo "📋 Using Stellar Account:"
echo "   Public Key: $STELLAR_PUBLIC"
echo ""

# Navigate to contract directory
cd contracts/ai_treasury_vault

# Source cargo environment
source ~/.cargo/env

# Build contract (if not already built)
echo "🔨 Building smart contract..."
stellar contract build
echo ""

# Deploy contract
echo "🚢 Deploying contract to testnet..."
CONTRACT_ID=$(stellar contract deploy \
  --wasm target/wasm32v1-none/release/ai_treasury_vault.wasm \
  --source "$STELLAR_SECRET" \
  --network testnet 2>&1 | tail -1)

if [ -z "$CONTRACT_ID" ]; then
    echo "❌ Error: Contract deployment failed"
    exit 1
fi

echo "✅ Contract deployed successfully!"
echo "📋 Contract ID: $CONTRACT_ID"
echo ""

# Save contract ID to .env
cd ../..
if grep -q "CONTRACT_ID" .env; then
    # Update existing CONTRACT_ID
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/^CONTRACT_ID=.*/CONTRACT_ID=$CONTRACT_ID/" .env
    else
        # Linux
        sed -i "s/^CONTRACT_ID=.*/CONTRACT_ID=$CONTRACT_ID/" .env
    fi
    echo "✅ Updated CONTRACT_ID in .env"
else
    # Add new CONTRACT_ID
    echo "" >> .env
    echo "# Smart Contract" >> .env
    echo "CONTRACT_ID=$CONTRACT_ID" >> .env
    echo "✅ Added CONTRACT_ID to .env"
fi

echo ""
echo "🔧 Initializing contract..."

# USDC contract on Stellar testnet
USDC_CONTRACT="CBIELTK6YBZJU5UP2WWQEUCYKLPU6AUNZ2BQ4WWFEIE3USCIHMXQDAMA"

# Initialize contract
source ~/.cargo/env && stellar contract invoke \
  --id "$CONTRACT_ID" \
  --source "$STELLAR_SECRET" \
  --network testnet \
  -- \
  initialize \
  --admin "$STELLAR_PUBLIC" \
  --risk_agent "$STELLAR_PUBLIC" \
  --usdc_contract "$USDC_CONTRACT" \
  --max_position_size "10000000000" \
  --min_sharpe_ratio "500000" \
  --max_drawdown "2000000"

echo ""
echo "✅ Contract initialized successfully!"
echo ""

# Check contract status
echo "🔍 Checking contract status..."
IS_OPERATIONAL=$(source ~/.cargo/env && stellar contract invoke \
  --id "$CONTRACT_ID" \
  --network testnet \
  -- \
  is_operational)

echo "   Operational Status: $IS_OPERATIONAL"
echo ""

# Print summary
echo "╔════════════════════════════════════════════════════════════╗"
echo "║          🎉 Deployment Complete!                           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 Contract Information:"
echo "   Contract ID: $CONTRACT_ID"
echo "   Network: Testnet"
echo "   Admin: $STELLAR_PUBLIC"
echo "   Risk Agent: $STELLAR_PUBLIC"
echo "   USDC Contract: $USDC_CONTRACT"
echo ""
echo "🌐 View on Stellar Explorer:"
echo "   https://stellar.expert/explorer/testnet/contract/$CONTRACT_ID"
echo ""
echo "📝 Contract ID saved to .env file"
echo ""
echo "🚀 Next Steps:"
echo "   1. Update app/config.yaml to enable smart contract"
echo "   2. Run: python smart_start.py"
echo "   3. Configure assets and start trading!"
echo ""

