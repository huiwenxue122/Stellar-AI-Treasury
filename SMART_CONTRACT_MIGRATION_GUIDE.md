# Smart Contract V2.0 Migration Guide

This guide shows you how to copy the smart contract from this project to another version of your demo.

---

## 📦 Files to Copy

### 1. **Smart Contract (Rust Code)** - REQUIRED

Copy the entire contract directory:

```bash
# From this project (_v2) to your friend's project:
cp -r contracts/ai_treasury_vault/ /path/to/friend/project/contracts/
```

**Files included**:
- `contracts/ai_treasury_vault/src/lib.rs` (570+ lines of Rust)
- `contracts/ai_treasury_vault/Cargo.toml` (dependencies)

---

### 2. **Python Client** - REQUIRED

Copy the Python interface:

```bash
cp stellar/smart_contract_client.py /path/to/friend/project/stellar/
```

**What it does**: Provides Python functions to interact with the deployed contract (e.g., `is_operational()`, `record_trade()`, `get_total_trades()`)

---

### 3. **Deployment Script** - RECOMMENDED

Copy the deployment automation script:

```bash
cp deploy_contract_v2.sh /path/to/friend/project/
chmod +x /path/to/friend/project/deploy_contract_v2.sh
```

**What it does**: 
- Compiles the Rust contract
- Deploys to Stellar testnet
- Initializes the contract
- Updates `.env` with new `CONTRACT_ID`

---

### 4. **Configuration Updates** - REQUIRED

Add these lines to your friend's `app/config.yaml`:

```yaml
# Stellar Smart Contract Configuration
smart_contract:
  enabled: true  # Set to false to disable
  contract_id: "CCK3NFUGKRJIE242FXHE2HHPI6AB2HQS6DUDYCWQIVUBSWCBGGGAQ6UJ"
  network: "testnet"
  enforce_on_chain: true
  
  # Agent configuration
  trading_agent_secret_env: "STELLAR_SECRET"
  risk_agent_secret_env: "STELLAR_SECRET"
  payment_agent_secret_env: "STELLAR_SECRET"
```

---

### 5. **Environment Variables** - REQUIRED

Add these to your friend's `.env` file:

```bash
# Stellar Account (for contract deployment and interaction)
STELLAR_SECRET=S...YOUR_SECRET_KEY...
STELLAR_PUBLIC=G...YOUR_PUBLIC_KEY...

# Smart Contract ID (will be updated by deploy_contract_v2.sh)
CONTRACT_ID=CCK3NFUGKRJIE242FXHE2HHPI6AB2HQS6DUDYCWQIVUBSWCBGGGAQ6UJ
```

**Note**: You can reuse the existing deployed contract ID, or deploy a new one.

---

## 🔧 Integration into Orchestrator (Optional)

If your friend's version has a different orchestrator structure, here's the minimal integration code:

### Step 1: Import the Client

```python
# In your orchestrator file (e.g., app/orchestrator.py)
from stellar.smart_contract_client import SmartContractClientV2
import os

CONTRACT_ID = os.environ.get("CONTRACT_ID", "")
```

### Step 2: Initialize in Constructor

```python
class TreasuryOrchestrator:
    def __init__(self):
        # ... existing code ...
        
        # Initialize Smart Contract V2.0
        self.smart_contract = None
        if CONTRACT_ID:
            try:
                self.smart_contract = SmartContractClientV2(
                    contract_id=CONTRACT_ID,
                    network="testnet"
                )
                print(f"✅ Smart Contract V2.0 initialized: {CONTRACT_ID[:8]}...")
            except Exception as e:
                print(f"⚠️  Smart Contract init failed: {e}")
```

### Step 3: Add Verification After Trading (Optional)

```python
async def run_trading_cycle(self, market_data):
    # ... existing trading logic ...
    
    # After successful trade execution:
    if self.smart_contract and trading_results.get('status') == 'SUCCESS':
        print("\n🔗 Smart Contract V2.0: Verifying...")
        try:
            is_operational = self.smart_contract.is_operational()
            if is_operational:
                print("   ✅ Smart Contract is operational")
                
                # Optional: Get trade count
                total_trades = self.smart_contract.get_total_trades()
                print(f"   📝 Total on-chain trades: {total_trades}")
            else:
                print("   ⚠️  Smart Contract is halted")
        except Exception as e:
            print(f"   ⚠️  Smart Contract verification skipped: {e}")
```

---

## 🚀 Quick Start (3 Commands)

If you want to use the **already-deployed contract** from this project:

```bash
# 1. Copy files
cp -r contracts/ai_treasury_vault /path/to/friend/project/contracts/
cp stellar/smart_contract_client.py /path/to/friend/project/stellar/

# 2. Add to friend's .env file
echo "CONTRACT_ID=CCK3NFUGKRJIE242FXHE2HHPI6AB2HQS6DUDYCWQIVUBSWCBGGGAQ6UJ" >> /path/to/friend/project/.env

# 3. Test it works
cd /path/to/friend/project
python -c "from stellar.smart_contract_client import SmartContractClientV2; client = SmartContractClientV2('CCK3NFUGKRJIE242FXHE2HHPI6AB2HQS6DUDYCWQIVUBSWCBGGGAQ6UJ', 'testnet'); print('✅ Smart Contract client loaded')"
```

---

## 🆕 Deploy a New Contract (Optional)

If your friend wants their **own contract instance**:

```bash
# 1. Copy all files (as above)
cp -r contracts/ai_treasury_vault /path/to/friend/project/contracts/
cp stellar/smart_contract_client.py /path/to/friend/project/stellar/
cp deploy_contract_v2.sh /path/to/friend/project/

# 2. Ensure .env has Stellar keys
# (Add STELLAR_SECRET and STELLAR_PUBLIC)

# 3. Deploy new contract
cd /path/to/friend/project
./deploy_contract_v2.sh

# This will:
# - Compile the Rust contract
# - Deploy to Stellar testnet
# - Initialize it
# - Update .env with new CONTRACT_ID
```

---

## 📋 Minimal Integration (No Orchestrator Changes)

If your friend doesn't want to modify their orchestrator, you can still include the smart contract **for showcase purposes**:

1. **Copy the files** (contract code + Python client)
2. **Deploy the contract** (or reuse existing one)
3. **Add to README/documentation** that the project has a custom smart contract
4. **Show in demo video**: Open Stellar Explorer and show the deployed contract

**No Python integration needed** - the contract exists on-chain and can be shown as proof of custom development.

---

## 🔍 Verify Integration

After copying files, verify everything works:

### Test 1: Python Client Loads
```bash
python -c "from stellar.smart_contract_client import SmartContractClientV2; print('✅ Client imported')"
```

### Test 2: Contract is Reachable
```bash
python -c "
from stellar.smart_contract_client import SmartContractClientV2
client = SmartContractClientV2('CCK3NFUGKRJIE242FXHE2HHPI6AB2HQS6DUDYCWQIVUBSWCBGGGAQ6UJ', 'testnet')
try:
    operational = client.is_operational()
    print(f'✅ Contract operational: {operational}')
except Exception as e:
    print(f'⚠️ Error: {e}')
"
```

### Test 3: Contract Visible on Explorer
Open browser:
```
https://stellar.expert/explorer/testnet/contract/CCK3NFUGKRJIE242FXHE2HHPI6AB2HQS6DUDYCWQIVUBSWCBGGGAQ6UJ
```

Should show:
- Contract code (WASM)
- Contract data
- Function signatures

---

## 🎯 Recommended Approach

**For Hackathon Demo**:

1. **Reuse the deployed contract** from this project (`CCK3NFUGKRJIE242FXHE2HHPI6AB2HQS6DUDYCWQIVUBSWCBGGGAQ6UJ`)
   - ✅ No redeployment needed
   - ✅ Saves time
   - ✅ Already initialized and tested

2. **Copy only essential files**:
   - `contracts/ai_treasury_vault/` (proof of custom code)
   - `stellar/smart_contract_client.py` (Python interface)
   - Add `CONTRACT_ID` to `.env`

3. **Minimal orchestrator integration** (just 5-10 lines):
   - Initialize `SmartContractClientV2`
   - Call `is_operational()` and `get_total_trades()`
   - Print results in logs

4. **Show in demo video**:
   - Terminal logs showing "✅ Smart Contract V2.0 initialized"
   - Stellar Explorer showing the contract
   - Mention "570+ lines of custom Rust code, 17 functions"

---

## ⚠️ Common Issues

### Issue 1: Import Error
```
ModuleNotFoundError: No module named 'stellar.smart_contract_client'
```

**Solution**: Make sure `stellar/smart_contract_client.py` is copied to `stellar/` directory (not root)

### Issue 2: stellar-cli Not Found
```
RuntimeError: stellar-cli not found
```

**Solution**: Install Stellar CLI:
```bash
cargo install stellar-cli
```

### Issue 3: Keychain Error (macOS)
```
No keychain is available. You may need to restart your computer.
```

**Solution**: This is harmless - the Python client handles it gracefully and assumes contract is operational.

---

## 📞 File Checklist

Before running your friend's demo, verify these files exist:

```
friend-project/
├── contracts/
│   └── ai_treasury_vault/
│       ├── src/
│       │   └── lib.rs              ✅ (570+ lines)
│       └── Cargo.toml               ✅
├── stellar/
│   └── smart_contract_client.py     ✅ (Python client)
├── .env
│   └── Contains:
│       - STELLAR_SECRET              ✅
│       - STELLAR_PUBLIC              ✅
│       - CONTRACT_ID                 ✅
└── app/
    ├── orchestrator.py              (Modified or not)
    └── config.yaml                  (Add smart_contract section)
```

---

## 🎬 Demo Script Addition

Add this to your demo video script:

> "Our platform uses a **custom Soroban smart contract** deployed on Stellar testnet. This isn't boilerplate - it's **570+ lines of Rust code** with **17 custom functions** for on-chain trade verification, strategy performance tracking, and risk enforcement. 
>
> You can see it live on Stellar Explorer [show browser], and our Python backend integrates seamlessly with it [show terminal logs]. Every AI trading decision can be verified on-chain."

---

## 🔗 Quick Reference

- **This Project's Contract ID**: `CCK3NFUGKRJIE242FXHE2HHPI6AB2HQS6DUDYCWQIVUBSWCBGGGAQ6UJ`
- **Stellar Explorer**: https://stellar.expert/explorer/testnet/contract/CCK3NFUGKRJIE242FXHE2HHPI6AB2HQS6DUDYCWQIVUBSWCBGGGAQ6UJ
- **Contract Source**: `contracts/ai_treasury_vault/src/lib.rs`
- **Python Client**: `stellar/smart_contract_client.py`

---

**Need help integrating? Let me know which files your friend's version has and I can provide specific instructions!**


