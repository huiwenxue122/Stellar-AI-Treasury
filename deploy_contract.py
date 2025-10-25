#!/usr/bin/env python3
"""
Automated Stellar Smart Contract Deployment Script

This script will:
1. Build the Soroban smart contract
2. Deploy it to Stellar testnet
3. Initialize the contract with your account
4. Save the CONTRACT_ID to .env
5. Verify deployment
"""

import os
import subprocess
import sys
import re
from pathlib import Path
from dotenv import load_dotenv, set_key

def run_command(cmd, capture_output=True):
    """Run a shell command and return the result"""
    print(f"🔧 Running: {' '.join(cmd)}")
    result = subprocess.run(
        cmd,
        capture_output=capture_output,
        text=True,
        shell=False
    )
    if result.returncode != 0:
        print(f"❌ Error: {result.stderr}")
        return None
    return result.stdout.strip()

def main():
    print("=" * 70)
    print("🚀 Stellar AI Treasury - Smart Contract Deployment")
    print("=" * 70)
    print()
    
    # Load environment variables
    project_root = Path(__file__).parent
    env_file = project_root / ".env"
    
    if not env_file.exists():
        print("❌ Error: .env file not found")
        print("   Please create .env with STELLAR_SECRET and STELLAR_PUBLIC")
        sys.exit(1)
    
    load_dotenv(env_file)
    
    stellar_secret = os.getenv("STELLAR_SECRET")
    stellar_public = os.getenv("STELLAR_PUBLIC")
    
    if not stellar_secret or not stellar_public:
        print("❌ Error: STELLAR_SECRET or STELLAR_PUBLIC not found in .env")
        sys.exit(1)
    
    print("✅ Environment variables loaded")
    print(f"📋 Stellar Public Key: {stellar_public}")
    print()
    
    # Step 1: Build contract
    print("=" * 70)
    print("Step 1: Building Smart Contract")
    print("=" * 70)
    
    contract_dir = project_root / "contracts" / "ai_treasury_vault"
    os.chdir(contract_dir)
    
    # Source cargo environment and build
    cargo_env = os.path.expanduser("~/.cargo/env")
    build_cmd = f"source {cargo_env} && stellar contract build"
    
    result = subprocess.run(
        build_cmd,
        shell=True,
        executable="/bin/bash",
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("❌ Build failed:")
        print(result.stderr)
        sys.exit(1)
    
    print("✅ Contract built successfully")
    print()
    
    # Check if wasm file exists
    wasm_file = contract_dir / "target" / "wasm32v1-none" / "release" / "ai_treasury_vault.wasm"
    if not wasm_file.exists():
        print(f"❌ Error: WASM file not found at {wasm_file}")
        sys.exit(1)
    
    print(f"📦 WASM file: {wasm_file}")
    print()
    
    # Step 2: Deploy contract
    print("=" * 70)
    print("Step 2: Deploying to Stellar Testnet")
    print("=" * 70)
    
    deploy_cmd = f"""source {cargo_env} && stellar contract deploy \
        --wasm {wasm_file} \
        --source {stellar_secret} \
        --network testnet"""
    
    result = subprocess.run(
        deploy_cmd,
        shell=True,
        executable="/bin/bash",
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("❌ Deployment failed:")
        print(result.stderr)
        sys.exit(1)
    
    # Extract contract ID from output
    contract_id = result.stdout.strip().split('\n')[-1].strip()
    
    # Validate contract ID format (starts with C and is ~56 chars)
    if not contract_id.startswith('C') or len(contract_id) < 50:
        print("❌ Error: Invalid contract ID received")
        print(f"   Output: {result.stdout}")
        sys.exit(1)
    
    print("✅ Contract deployed successfully!")
    print(f"📋 Contract ID: {contract_id}")
    print()
    
    # Step 3: Save to .env
    print("=" * 70)
    print("Step 3: Saving Configuration")
    print("=" * 70)
    
    os.chdir(project_root)
    
    # Update or add CONTRACT_ID to .env
    env_path = str(env_file)
    
    # Read current .env content
    with open(env_path, 'r') as f:
        env_content = f.read()
    
    if 'CONTRACT_ID' in env_content:
        # Update existing
        env_content = re.sub(
            r'^CONTRACT_ID=.*$',
            f'CONTRACT_ID={contract_id}',
            env_content,
            flags=re.MULTILINE
        )
        with open(env_path, 'w') as f:
            f.write(env_content)
        print("✅ Updated CONTRACT_ID in .env")
    else:
        # Add new
        with open(env_path, 'a') as f:
            f.write(f"\n# Smart Contract\nCONTRACT_ID={contract_id}\n")
        print("✅ Added CONTRACT_ID to .env")
    
    print()
    
    # Step 4: Initialize contract
    print("=" * 70)
    print("Step 4: Initializing Contract")
    print("=" * 70)
    
    # USDC contract on Stellar testnet
    usdc_contract = "CBIELTK6YBZJU5UP2WWQEUCYKLPU6AUNZ2BQ4WWFEIE3USCIHMXQDAMA"
    
    init_cmd = f"""source {cargo_env} && stellar contract invoke \
        --id {contract_id} \
        --source {stellar_secret} \
        --network testnet \
        -- \
        initialize \
        --admin {stellar_public} \
        --risk_agent {stellar_public} \
        --usdc_contract {usdc_contract} \
        --max_position_size 10000000000 \
        --min_sharpe_ratio 500000 \
        --max_drawdown 2000000"""
    
    result = subprocess.run(
        init_cmd,
        shell=True,
        executable="/bin/bash",
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("❌ Initialization failed:")
        print(result.stderr)
        print("\n⚠️  Contract is deployed but not initialized.")
        print(f"   You can initialize it manually later using CONTRACT_ID: {contract_id}")
    else:
        print("✅ Contract initialized successfully!")
    
    print()
    
    # Step 5: Verify deployment
    print("=" * 70)
    print("Step 5: Verifying Deployment")
    print("=" * 70)
    
    verify_cmd = f"""source {cargo_env} && stellar contract invoke \
        --id {contract_id} \
        --network testnet \
        -- \
        is_operational"""
    
    result = subprocess.run(
        verify_cmd,
        shell=True,
        executable="/bin/bash",
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        is_operational = result.stdout.strip()
        print(f"✅ Contract is operational: {is_operational}")
    else:
        print("⚠️  Could not verify operational status")
    
    print()
    
    # Print summary
    print("=" * 70)
    print("🎉 DEPLOYMENT COMPLETE!")
    print("=" * 70)
    print()
    print("📋 Contract Information:")
    print(f"   Contract ID: {contract_id}")
    print(f"   Network: Testnet")
    print(f"   Admin: {stellar_public}")
    print(f"   Risk Agent: {stellar_public}")
    print(f"   USDC Contract: {usdc_contract}")
    print()
    print("🌐 View on Stellar Explorer:")
    explorer_url = f"https://stellar.expert/explorer/testnet/contract/{contract_id}"
    print(f"   {explorer_url}")
    print()
    print("📝 Configuration:")
    print(f"   ✅ CONTRACT_ID saved to .env")
    print()
    print("🚀 Next Steps:")
    print("   1. Update app/config.yaml:")
    print("      smart_contract:")
    print("        enabled: true")
    print(f"        contract_id: \"{contract_id}\"")
    print("        network: \"testnet\"")
    print()
    print("   2. Start the dashboard:")
    print("      python smart_start.py")
    print()
    print("   3. Configure assets and run trading cycle!")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Deployment cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

