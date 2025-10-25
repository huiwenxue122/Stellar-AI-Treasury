"""
User Tier Management System
Handles user classification, asset filtering, and risk budget allocation
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class TierConfig:
    """Configuration for a specific user tier"""
    name: str
    risk_budget: str
    max_portfolio_var: float
    max_single_asset_percent: int
    allowed_assets: List[str]
    allowed_asset_types: List[str]
    prompt_style: str
    explanation_depth: str
    allowed_risk_levels: List[str] = None  # 🎯 New: risk-based filtering
    safety_focus: bool = False
    use_analogies: bool = False
    show_metrics: bool = False
    metrics_to_show: List[str] = None
    show_raw_data: bool = False
    enable_derivatives: bool = False
    enable_structured_strategies: bool = False
    localization: Dict[str, Any] = None


class TierManager:
    """Manages user tier system and adapts system behavior accordingly"""
    
    def __init__(self, config: dict):
        """Initialize tier manager with configuration"""
        self.config = config
        self.tier_system_config = config.get('user_tier_system', {})
        self.enabled = self.tier_system_config.get('enabled', False)
        self.default_tier = self.tier_system_config.get('default_tier', 'beginner')
        
        # Load tier configurations
        self.tiers: Dict[str, TierConfig] = {}
        if self.enabled:
            self._load_tier_configs()
    
    def _load_tier_configs(self):
        """Load all tier configurations from config"""
        tier_defs = self.tier_system_config.get('tiers', {})
        
        for tier_name, tier_data in tier_defs.items():
            self.tiers[tier_name] = TierConfig(
                name=tier_name,
                risk_budget=tier_data.get('risk_budget', 'low'),
                max_portfolio_var=tier_data.get('max_portfolio_var', 0.05),
                max_single_asset_percent=tier_data.get('max_single_asset_percent', 30),
                allowed_assets=tier_data.get('allowed_assets', []),
                allowed_asset_types=tier_data.get('allowed_asset_types', []),
                allowed_risk_levels=tier_data.get('allowed_risk_levels', ['safe']),  # 🎯 New
                prompt_style=tier_data.get('prompt_style', 'balanced'),
                explanation_depth=tier_data.get('explanation_depth', 'moderate'),
                safety_focus=tier_data.get('safety_focus', False),
                use_analogies=tier_data.get('use_analogies', False),
                show_metrics=tier_data.get('show_metrics', False),
                metrics_to_show=tier_data.get('metrics_to_show', []),
                show_raw_data=tier_data.get('show_raw_data', False),
                enable_derivatives=tier_data.get('enable_derivatives', False),
                enable_structured_strategies=tier_data.get('enable_structured_strategies', False),
                localization=tier_data.get('localization', {})
            )
    
    def get_tier_config(self, tier_name: str = None) -> TierConfig:
        """Get configuration for a specific tier"""
        if not self.enabled:
            # Return a default permissive config if system is disabled
            return TierConfig(
                name='default',
                risk_budget='medium',
                max_portfolio_var=0.05,
                max_single_asset_percent=40,
                allowed_assets='all',
                allowed_asset_types='all',
                prompt_style='balanced',
                explanation_depth='moderate'
            )
        
        tier_name = tier_name or self.default_tier
        return self.tiers.get(tier_name, self.tiers.get(self.default_tier))
    
    def filter_allowed_assets(self, all_assets: List[str], tier_name: str = None) -> List[str]:
        """Filter assets based on user tier restrictions"""
        tier_config = self.get_tier_config(tier_name)
        
        # If tier allows all assets, return all
        if tier_config.allowed_assets == 'all':
            return all_assets
        
        # Filter to only allowed assets
        allowed = [asset for asset in all_assets if asset.upper() in [a.upper() for a in tier_config.allowed_assets]]
        return allowed if allowed else all_assets  # Fallback to all if filter results in empty list
    
    def get_assets_by_risk_level(self, tier_name: str = None) -> Dict[str, List[str]]:
        """Get assets grouped by risk level based on user tier
        
        Returns:
            Dict with keys: 'safe', 'moderate', 'high_risk'
            Each containing a list of allowed asset codes
        """
        tier_config = self.get_tier_config(tier_name)
        
        # Get allowed risk levels from tier config
        allowed_risk_levels = getattr(tier_config, 'allowed_risk_levels', ['safe'])
        if not allowed_risk_levels:
            allowed_risk_levels = ['safe']  # Fallback
        
        # Get asset risk classification from config
        asset_risk_classification = self.config.get('asset_risk_classification', {})
        
        result = {}
        
        # Process each risk level
        for risk_level in ['safe', 'moderate', 'high_risk']:
            if risk_level in allowed_risk_levels:
                # Get all assets in this risk level
                risk_level_data = asset_risk_classification.get(risk_level, {})
                assets_in_level = []
                
                # Flatten all categories within this risk level
                for category, asset_list in risk_level_data.items():
                    if isinstance(asset_list, list):
                        assets_in_level.extend(asset_list)
                
                result[risk_level] = assets_in_level
            else:
                result[risk_level] = []  # Empty list if not allowed
        
        return result
    
    def get_asset_risk_level(self, asset_code: str) -> str:
        """Get the risk level of a specific asset
        
        Returns:
            'safe', 'moderate', 'high_risk', or 'unknown'
        """
        asset_code_upper = asset_code.upper()
        asset_risk_classification = self.config.get('asset_risk_classification', {})
        
        for risk_level, categories in asset_risk_classification.items():
            for category, asset_list in categories.items():
                if isinstance(asset_list, list) and asset_code_upper in [a.upper() for a in asset_list]:
                    return risk_level
        
        return 'unknown'
    
    def get_prompt_template(self, agent_type: str, tier_name: str = None) -> str:
        """Generate prompt template based on user tier and agent type"""
        tier_config = self.get_tier_config(tier_name)
        style = tier_config.prompt_style
        depth = tier_config.explanation_depth
        
        prompts = {
            'trading': self._get_trading_prompt(style, depth, tier_config),
            'risk': self._get_risk_prompt(style, depth, tier_config),
            'payment': self._get_payment_prompt(style, depth, tier_config)
        }
        
        return prompts.get(agent_type, prompts['trading'])
    
    def _get_trading_prompt(self, style: str, depth: str, config: TierConfig) -> str:
        """Generate trading agent prompt based on tier"""
        if style == 'educational_friendly':
            return f"""You are a financial coach for first-time investors from diverse global backgrounds.
Your goal is to help users understand safe investment opportunities that preserve capital.

Key Principles:
- Focus on SAFETY FIRST - explain why stablecoins like USDC are safer than volatile assets
- Use simple analogies: "Think of USDC like a digital savings account"
- Prioritize stable assets: USDC, tokenized bonds, gold-backed tokens
- Avoid risky or complex assets
- Explain every decision step-by-step
- Risk Budget: VERY LOW (max 2% potential loss)
- Always mention: "This is safer because..."

Available Safe Assets: {', '.join(config.allowed_assets)}

Remember: Your users may be new to both crypto AND investing. Make them feel confident and safe."""

        elif style == 'balanced_metrics':
            return f"""You are a financial assistant for a semi-experienced investor.
Balance between safety and growth opportunities.

Key Principles:
- Explain key metrics: VaR (Value at Risk), Sharpe Ratio, Volatility
- Show both risks and opportunities
- Diversify between stablecoins and major cryptocurrencies
- Risk Budget: MEDIUM (max 5% VaR)
- Include brief metric insights: "BTC has higher volatility (±15%) but historical returns..."

Available Assets: {', '.join(config.allowed_assets)}
Metrics to Show: {', '.join(config.metrics_to_show)}

Provide balanced, data-informed recommendations."""

        else:  # technical_quant
            return f"""You are a quant trading co-pilot optimizing risk-adjusted returns.
Use multi-asset strategies and advanced portfolio optimization.

Key Principles:
- Data-driven decisions only
- Optimize Sharpe Ratio, minimize CVaR
- Use all available instruments including derivatives
- Risk Budget: FULL (max 10% VaR acceptable)
- Focus on alpha generation and correlation analysis

Available: ALL ASSETS + structured strategies

Provide technical, quantitative analysis without unnecessary explanations."""
    
    def _get_risk_prompt(self, style: str, depth: str, config: TierConfig) -> str:
        """Generate risk agent prompt based on tier"""
        if style == 'educational_friendly':
            return f"""You are a safety guardian for first-time investors.
Your job is to protect users from taking risks they don't understand.

Key Principles:
- Reject ANY portfolio with > 2% VaR
- Explain risks in simple terms: "This could lose X% of your money if..."
- Always suggest safer alternatives
- Maximum single asset: {config.max_single_asset_percent}%
- Prioritize capital preservation over growth

Use language like: "I recommend against this because..." or "A safer option would be..."

Remember: These users are learning. Be supportive but firm on safety."""

        elif style == 'balanced_metrics':
            return f"""You are a risk manager balancing safety with growth.
Evaluate portfolios using standard risk metrics.

Key Principles:
- Accept portfolios with VaR < 5%
- Check Sharpe Ratio (target > 1.0)
- Ensure diversification across asset classes
- Maximum single asset: {config.max_single_asset_percent}%
- Flag high-risk strategies with clear reasoning

Provide metric-based analysis and clear approval/rejection."""

        else:  # technical_quant
            return f"""You are a quantitative risk analyst.
Evaluate portfolio risk using advanced metrics.

Key Principles:
- Accept VaR up to 10%
- Analyze CVaR, max drawdown, beta, correlation matrices
- Maximum single asset: {config.max_single_asset_percent}%
- Approve aggressive strategies if risk-adjusted returns justify it

Provide concise, data-driven risk assessment."""
    
    def _get_payment_prompt(self, style: str, depth: str, config: TierConfig) -> str:
        """Generate payment agent prompt based on tier"""
        # Payment agent is generally consistent across tiers
        return """You are an execution specialist responsible for trade execution.
Execute approved trades efficiently and settle to USDC as instructed."""
    
    def get_safety_explanation(self, asset: str, tier_name: str = None, language: str = 'en') -> str:
        """Get safety explanation for an asset based on user tier"""
        tier_config = self.get_tier_config(tier_name)
        
        if not tier_config.safety_focus:
            return ""
        
        # Import translations from localization module
        from app.localization import TRANSLATIONS
        
        # Map asset codes to translation keys
        asset_key_map = {
            'USDC': 'usdc_safe',
            'USDT': 'usdc_safe',  # Similar to USDC
            'BTC': 'btc_volatile',
            'ETH': 'btc_volatile',  # Similar volatility warning
            'PAXG': 'paxg_safe',
            'XAUT': 'xaut_safe',
            'GOLD': 'gold_safe',
            'BENJI': 'benji_safe',
            'REIT': 'reit_safe',
            'XLM': 'xlm_native'
        }
        
        translation_key = asset_key_map.get(asset.upper())
        if translation_key and translation_key in TRANSLATIONS:
            return TRANSLATIONS[translation_key].get(language, TRANSLATIONS[translation_key].get('en', ''))
        
        return ""
    
    def should_show_metric(self, metric_name: str, tier_name: str = None) -> bool:
        """Check if a specific metric should be shown to user"""
        tier_config = self.get_tier_config(tier_name)
        
        if not tier_config.show_metrics:
            return False
        
        if tier_config.show_raw_data:  # Advanced users see everything
            return True
        
        return metric_name.lower() in [m.lower() for m in (tier_config.metrics_to_show or [])]
    
    def get_risk_budget_limits(self, tier_name: str = None) -> Dict[str, float]:
        """Get risk budget limits for a tier"""
        tier_config = self.get_tier_config(tier_name)
        
        return {
            'max_var': tier_config.max_portfolio_var,
            'max_single_asset': tier_config.max_single_asset_percent / 100.0,
            'risk_level': tier_config.risk_budget
        }
    
    def get_available_languages(self, tier_name: str = None) -> List[str]:
        """Get available languages for a tier"""
        tier_config = self.get_tier_config(tier_name)
        return tier_config.localization.get('languages', ['en']) if tier_config.localization else ['en']
    
    def is_tts_enabled(self, tier_name: str = None) -> bool:
        """Check if text-to-speech is enabled for a tier"""
        tier_config = self.get_tier_config(tier_name)
        return tier_config.localization.get('enable_tts', False) if tier_config.localization else False

