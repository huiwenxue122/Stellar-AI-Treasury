# 🌍 Tiered User System & Global Accessibility Guide

## Overview

The Stellar AI Treasury now features a **Tiered User System** designed to make crypto trading accessible to users worldwide, regardless of their investment experience or technical background.

---

## 🎓 User Tiers

### 1️⃣ Beginner - Safe & Stable
**Target Users**: First-time investors, users from emerging markets, those seeking capital preservation

**Features**:
- 💰 **Risk Budget**: Very Low (max 2% VaR)
- 🛡️ **Allowed Assets**: USDC, USDT, XLM only (stablecoins and native currency)
- 📚 **Explanation Style**: Educational and friendly with simple analogies
- ✅ **Safety Focus**: Every decision explained step-by-step
- 🌍 **Languages**: English, Spanish, Swahili, Arabic, Chinese
- 🔊 **Text-to-Speech**: Enabled for low-literacy users

**Prompt Style Example**:
```
You are a financial coach for first-time investors.
Focus on SAFETY FIRST - explain why USDC is safer than volatile assets.
Use simple analogies: "Think of USDC like a digital savings account"
```

**Best For**:
- Users new to both crypto AND investing
- Risk-averse investors
- Users from regions with limited financial infrastructure (e.g., Africa, LATAM)

---

### 2️⃣ Intermediate - Balanced Growth
**Target Users**: Semi-experienced investors, those comfortable with basic metrics

**Features**:
- 📊 **Risk Budget**: Medium (max 5% VaR)
- 🪙 **Allowed Assets**: USDC, USDT, BTC, ETH, XLM, SOL, LINK
- 📈 **Explanation Style**: Balanced with metric insights
- 🎯 **Metrics Shown**: VaR, Sharpe Ratio, Volatility
- 🌍 **Languages**: English, Spanish, Chinese
- 🔊 **Text-to-Speech**: Disabled

**Prompt Style Example**:
```
You are a financial assistant for a semi-experienced investor.
Balance between safety and growth opportunities.
Explain key metrics: "BTC has higher volatility (±15%) but historical returns..."
```

**Best For**:
- Users with some investment experience
- Those seeking growth while managing risk
- Users comfortable with technical indicators

---

### 3️⃣ Advanced - Maximum Returns
**Target Users**: Experienced traders, quantitative analysts

**Features**:
- 🚀 **Risk Budget**: Full (max 10% VaR)
- 🌐 **Allowed Assets**: ALL (crypto, RWA, derivatives, structured products)
- 🔬 **Explanation Style**: Technical and data-driven
- 📊 **Metrics Shown**: All advanced metrics (CVaR, Max Drawdown, Alpha, Beta, etc.)
- 🌍 **Languages**: English only
- 🔊 **Text-to-Speech**: Disabled

**Prompt Style Example**:
```
You are a quant trading co-pilot optimizing risk-adjusted returns.
Data-driven decisions only. Focus on alpha generation and correlation analysis.
```

**Best For**:
- Professional traders
- Users seeking aggressive growth strategies
- Those comfortable with high volatility

---

## 🌍 Localization & Accessibility

### Supported Languages

1. **🇬🇧 English** - All tiers
2. **🇪🇸 Español (Spanish)** - Beginner, Intermediate
3. **🇹🇿 Kiswahili (Swahili)** - Beginner (for East Africa)
4. **🇸🇦 العربية (Arabic)** - Beginner (for MENA region)
5. **🇨🇳 中文 (Chinese)** - Beginner, Intermediate

### Localized Content

- ✅ Safety explanations for each asset
- ✅ Risk level descriptions
- ✅ Trading button labels
- ✅ Dashboard titles and headers
- ✅ Warning messages

### Example Translations

**USDC Safety Explanation**:
- **English**: "USDC is a stablecoin backed 1:1 by US dollars. Very safe for storing value."
- **Spanish**: "USDC es una moneda estable respaldada 1:1 por dólares estadounidenses. Muy seguro."
- **Swahili**: "USDC ni sarafu thabiti inayothaminiwa 1:1 na dola za Marekani. Salama sana."
- **Arabic**: "USDC هي عملة مستقرة مدعومة 1:1 بالدولار الأمريكي. آمن جداً."
- **Chinese**: "USDC 是 1:1 锚定美元的稳定币。储值非常安全。"

---

## 🎨 Dashboard Features

### Tier Selection UI

1. **Experience Level Selection**
   - Radio buttons for Beginner / Intermediate / Advanced
   - Visual tier descriptions with risk budgets
   - Language selector (flag emojis)

2. **Asset Filtering**
   - Only shows assets allowed for selected tier
   - Visual indicators:
     - ✅ = Safe for beginners (stablecoins, RWA)
     - ⚠️ = Volatile (BTC, ETH) - shown with warning for beginners

3. **Educational Tooltips**
   - Hover over assets to see safety explanations
   - Risk level indicators (Low ✅ / Medium ⚠️ / High ❌)
   - Localized content based on selected language

4. **Risk Budget Display**
   - Shows max VaR % for selected tier
   - Max single asset allocation %
   - Updates dynamically when tier changes

---

## 🔧 Technical Implementation

### Configuration (`config.yaml`)

```yaml
user_tier_system:
  enabled: true
  default_tier: "beginner"
  
  tiers:
    beginner:
      risk_budget: "very_low"
      max_portfolio_var: 0.02  # 2%
      max_single_asset_percent: 30
      allowed_assets: [USDC, USDT, XLM]
      prompt_style: "educational_friendly"
      explanation_depth: "high"
      localization:
        languages: ["en", "es", "sw", "ar", "zh"]
        enable_tts: true
```

### Core Classes

1. **`TierManager`** (`app/tier_manager.py`)
   - Manages tier configurations
   - Filters assets based on tier restrictions
   - Generates tier-specific prompts for AI agents

2. **`Localization`** (`app/localization.py`)
   - Provides multi-language translations
   - Stores safety explanations in 5 languages
   - Handles tier descriptions and risk explanations

3. **`MultiAgentOrchestratorWithTools`**
   - Accepts `tier_manager` parameter
   - Adapts Trading Agent and Risk Agent prompts based on user tier
   - Enforces tier-specific risk limits

---

## 📖 Usage Example

### For a Beginner User in Kenya 🇰🇪

1. **Select Tier**: Beginner
2. **Select Language**: Kiswahili (Swahili)
3. **Available Assets**: USDC, USDT, XLM (filtered automatically)
4. **Agent Behavior**:
   - Trading Agent uses educational tone: "Tunapendelea USDC kwa sababu ni salama (We prefer USDC because it's safe)"
   - Risk Agent rejects portfolios > 2% VaR
   - Payment Agent settles everything to USDC for safety

5. **Dashboard**:
   - Shows safety explanations in Swahili
   - Displays green ✅ checkmarks for stable assets
   - Provides step-by-step guidance

6. **Text-to-Speech** (optional):
   - Can enable voice narration for trading explanations
   - Helps users with limited literacy

---

## 🎯 Design Goals

### Global Accessibility
- **Africa**: Swahili support, focus on stable assets (USDC), low barrier to entry
- **LATAM**: Spanish support, educational content for first-time investors
- **APAC**: Chinese support, balanced growth strategies
- **MENA**: Arabic support, Sharia-compliant considerations (future enhancement)

### Financial Inclusion
- **Low-Literacy Users**: Text-to-Speech enabled for beginners
- **Risk-Averse Users**: Beginner tier limits to stable assets only
- **Growth Seekers**: Intermediate tier balances safety with growth
- **Professionals**: Advanced tier unlocks full capabilities

### Educational Focus
- Teach users about risk vs. reward
- Explain metrics (VaR, Sharpe) in simple terms
- Use analogies: "USDC is like a digital savings account"
- Gradual progression: Beginner → Intermediate → Advanced

---

## 🚀 Getting Started

### 1. Start the Dashboard

```bash
cd /Users/zxzhang/Desktop/stellar-ai-treasury
python smart_start.py
```

### 2. Configure Your Tier

- Navigate to "Asset Configuration" page
- Select your experience level (Beginner recommended for first-time users)
- Choose your language
- Review risk budget and allowed assets

### 3. Select Assets

- Choose from tier-appropriate assets
- See safety explanations for each asset
- Configure hedge currency (USDC recommended)

### 4. Start Trading

- AI agents will adapt their behavior to your tier
- Trading Agent uses tier-specific prompts
- Risk Agent enforces tier risk limits
- All explanations provided in your selected language

---

## 🔮 Future Enhancements

1. **More Languages**: Add French (for West Africa), Portuguese (for Brazil), Hindi (for India)
2. **Voice Input**: Allow users to configure portfolios using voice commands
3. **SMS Notifications**: Send trade alerts via SMS for users with limited internet
4. **Offline Mode**: Cache strategies for areas with poor connectivity
5. **Community Features**: Connect users within the same tier for peer learning
6. **Gamification**: Badges for completing educational milestones (e.g., "Learned about VaR")

---

## 📞 Support

For questions or issues with the tiered system:
- Check `docs/architecture.md` for system design
- Review `app/tier_manager.py` for tier logic
- See `app/localization.py` for language support

---

**Built with ❤️ for global financial inclusion**

