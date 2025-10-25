"""
Multi-language localization support for global accessibility
"""

from typing import Dict

# 🌍 Translations for key UI elements and educational content
TRANSLATIONS = {
    # Dashboard titles and headers
    'portfolio_overview': {
        'en': 'Portfolio Overview',
        'es': 'Resumen de Cartera',
        'sw': 'Muhtasari wa Portfolio',
        'ar': 'نظرة عامة على المحفظة',
        'zh': '投资组合概览'
    },
    'total_value': {
        'en': 'Total Value',
        'es': 'Valor Total',
        'sw': 'Thamani Jumla',
        'ar': 'القيمة الإجمالية',
        'zh': '总价值'
    },
    'risk_level': {
        'en': 'Risk Level',
        'es': 'Nivel de Riesgo',
        'sw': 'Kiwango cha Hatari',
        'ar': 'مستوى المخاطر',
        'zh': '风险水平'
    },
    
    # User tier labels
    'tier_beginner': {
        'en': 'Beginner - Safe & Stable',
        'es': 'Principiante - Seguro y Estable',
        'sw': 'Mwanzo - Salama na Thabiti',
        'ar': 'مبتدئ - آمن ومستقر',
        'zh': '初学者 - 安全稳定'
    },
    'tier_intermediate': {
        'en': 'Intermediate - Balanced Growth',
        'es': 'Intermedio - Crecimiento Equilibrado',
        'sw': 'Wa Kati - Ukuaji Ulio Sawa',
        'ar': 'متوسط - نمو متوازن',
        'zh': '中级 - 平衡增长'
    },
    'tier_advanced': {
        'en': 'Advanced - Maximum Returns',
        'es': 'Avanzado - Retornos Máximos',
        'sw': 'Wa Juu - Faida Ya Juu',
        'ar': 'متقدم - عوائد قصوى',
        'zh': '高级 - 最大回报'
    },
    
    # Safety explanations (brief versions)
    'usdc_safe': {
        'en': '💰 USDC is a stablecoin (1 USDC = $1 USD). Very safe for storing value.',
        'es': '💰 USDC es una moneda estable (1 USDC = $1 USD). Muy seguro para almacenar valor.',
        'sw': '💰 USDC ni sarafu thabiti (1 USDC = $1 USD). Salama sana kwa kuhifadhi thamani.',
        'ar': '💰 USDC عملة مستقرة (1 USDC = $1 USD). آمن جدًا لحفظ القيمة.',
        'zh': '💰 USDC 是稳定币 (1 USDC = $1 美元)。储值非常安全。'
    },
    'btc_volatile': {
        'en': '⚠️ Bitcoin is volatile. Price can swing ±20% weekly. Only invest what you can afford to lose.',
        'es': '⚠️ Bitcoin es volátil. El precio puede variar ±20% semanalmente. Solo invierte lo que puedas perder.',
        'sw': '⚠️ Bitcoin ina mabadiliko. Bei inaweza kubadilika ±20% kwa wiki. Wekeza tu unachoweza kupoteza.',
        'ar': '⚠️ البيتكوين متقلب. السعر يمكن أن يتأرجح ±20% أسبوعيًا. استثمر فقط ما يمكنك خسارته.',
        'zh': '⚠️ 比特币波动大。价格每周可能波动 ±20%。只投资你能承受损失的资金。'
    },
    'xlm_native': {
        'en': '⭐ XLM is Stellar\'s native currency. Needed for network fees (very small amounts).',
        'es': '⭐ XLM es la moneda nativa de Stellar. Necesaria para tarifas de red (cantidades muy pequeñas).',
        'sw': '⭐ XLM ni sarafu ya asili ya Stellar. Inahitajika kwa ada za mtandao (kiasi kidogo sana).',
        'ar': '⭐ XLM هي العملة الأصلية لـ Stellar. ضرورية لرسوم الشبكة (كميات صغيرة جدًا).',
        'zh': '⭐ XLM 是 Stellar 的原生货币。用于网络手续费（极少量）。'
    },
    
    # Gold-backed tokens
    'paxg_safe': {
        'en': '🏆 PAXG is backed by physical gold. Each token = 1 troy ounce of gold stored in secure vaults. Very stable.',
        'es': '🏆 PAXG está respaldado por oro físico. Cada token = 1 onza troy de oro en bóvedas seguras. Muy estable.',
        'sw': '🏆 PAXG imeuungwa na dhahabu halisi. Token moja = 1 troy oz ya dhahabu katika hazina salama. Thabiti sana.',
        'ar': '🏆 PAXG مدعوم بالذهب الفعلي. كل رمز = 1 أونصة تروي من الذهب في خزائن آمنة. مستقر جداً.',
        'zh': '🏆 PAXG 由实物黄金支持。每个代币 = 1 盎司黄金存储在安全金库中。非常稳定。'
    },
    'xaut_safe': {
        'en': '🏆 Tether Gold (XAUT) is backed 1:1 by physical gold. Safe store of value.',
        'es': '🏆 Tether Gold (XAUT) está respaldado 1:1 por oro físico. Almacén seguro de valor.',
        'sw': '🏆 Tether Gold (XAUT) imeuungwa 1:1 na dhahabu halisi. Hifadhi salama ya thamani.',
        'ar': '🏆 تيثر جولد (XAUT) مدعوم 1:1 بالذهب الفعلي. مخزن آمن للقيمة.',
        'zh': '🏆 Tether Gold (XAUT) 由实物黄金 1:1 支持。安全的价值存储。'
    },
    'gold_safe': {
        'en': '🏆 Gold token backed by physical gold. Historically stable and holds value during market volatility.',
        'es': '🏆 Token de oro respaldado por oro físico. Históricamente estable y mantiene valor durante volatilidad.',
        'sw': '🏆 Token ya dhahabu imeuungwa na dhahabu halisi. Kihistoria thabiti na hubakia na thamani wakati wa mabadiliko.',
        'ar': '🏆 رمز ذهب مدعوم بالذهب الفعلي. مستقر تاريخياً ويحتفظ بالقيمة أثناء تقلب السوق.',
        'zh': '🏆 黄金代币由实物黄金支持。历史上稳定，在市场波动时保值。'
    },
    
    # Tokenized money market fund
    'benji_safe': {
        'en': '🏦 BENJI is Franklin Templeton\'s tokenized U.S. Government Money Market Fund (FOBXX). Backed by U.S. Treasury securities. Very low risk, stable yield.',
        'es': '🏦 BENJI es el fondo del mercado monetario del gobierno de EE. UU. tokenizado de Franklin Templeton (FOBXX). Respaldado por valores del Tesoro de EE. UU. Riesgo muy bajo, rendimiento estable.',
        'sw': '🏦 BENJI ni mfuko wa soko la fedha wa serikali ya Marekani wa Franklin Templeton (FOBXX) uliobadilishwa kuwa token. Unategemezwa na hati za Hazina ya Marekani. Hatari ndogo sana, mapato thabiti.',
        'ar': '🏦 BENJI هو صندوق سوق المال الحكومي الأمريكي المرمز لـ Franklin Templeton (FOBXX). مدعوم بسندات الخزانة الأمريكية. مخاطر منخفضة جداً، عائد مستقر.',
        'zh': '🏦 BENJI 是富兰克林邓普顿的代币化美国政府货币市场基金 (FOBXX)。由美国国债支持。风险极低，稳定收益。'
    },
    
    # Real estate
    'reit_safe': {
        'en': '🏢 REIT is a real estate token. Backed by property investments. Moderate risk, steady returns.',
        'es': '🏢 REIT es un token inmobiliario. Respaldado por inversiones en propiedades. Riesgo moderado, retornos constantes.',
        'sw': '🏢 REIT ni token ya mali isiyohamishika. Imeuungwa na uwekezaji wa mali. Hatari ya kati, mapato thabiti.',
        'ar': '🏢 REIT هو رمز عقاري. مدعوم باستثمارات عقارية. مخاطر معتدلة، عوائد ثابتة.',
        'zh': '🏢 REIT 是房地产代币。由房产投资支持。中等风险，稳定回报。'
    },
    
    # Action buttons
    'run_trading': {
        'en': 'Run Trading Cycle',
        'es': 'Ejecutar Ciclo de Trading',
        'sw': 'Fanya Mzunguko wa Biashara',
        'ar': 'تشغيل دورة التداول',
        'zh': '运行交易周期'
    },
    'select_tier': {
        'en': 'Select Your Experience Level',
        'es': 'Seleccione Su Nivel de Experiencia',
        'sw': 'Chagua Kiwango Chako cha Uzoefu',
        'ar': 'اختر مستوى خبرتك',
        'zh': '选择您的经验等级'
    },
    
    # Educational tooltips
    'what_is_var': {
        'en': 'VaR (Value at Risk): Estimated maximum loss over a time period with 95% confidence.',
        'es': 'VaR (Valor en Riesgo): Pérdida máxima estimada durante un período con 95% de confianza.',
        'sw': 'VaR (Thamani katika Hatari): Hasara ya juu inayokadiriwa kwa wakati fulani na uhakika wa 95%.',
        'ar': 'VaR (القيمة المعرضة للخطر): الخسارة القصوى المقدرة خلال فترة زمنية بثقة 95%.',
        'zh': 'VaR（风险价值）：在一定时期内，95% 置信度下的最大估计损失。'
    },
    'what_is_sharpe': {
        'en': 'Sharpe Ratio: Measures returns vs risk. Higher is better (>1.0 is good).',
        'es': 'Ratio de Sharpe: Mide retornos vs riesgo. Mayor es mejor (>1.0 es bueno).',
        'sw': 'Uwiano wa Sharpe: Unapima mapato dhidi ya hatari. Kubwa zaidi ni bora (>1.0 ni nzuri).',
        'ar': 'نسبة شارب: تقيس العوائد مقابل المخاطر. أعلى أفضل (>1.0 جيد).',
        'zh': '夏普比率：衡量收益与风险。越高越好（>1.0 为好）。'
    },
    
    # Warning messages
    'tier_restriction': {
        'en': '⚠️ Some assets are not available at your current tier. Upgrade to access more options.',
        'es': '⚠️ Algunos activos no están disponibles en su nivel actual. Actualice para acceder a más opciones.',
        'sw': '⚠️ Baadhi ya mali hazipatikani katika kiwango chako cha sasa. Boresha kupata chaguzi zaidi.',
        'ar': '⚠️ بعض الأصول غير متاحة في مستواك الحالي. قم بالترقية للوصول إلى المزيد من الخيارات.',
        'zh': '⚠️ 某些资产在您当前等级不可用。升级以访问更多选项。'
    },
    'high_risk_warning': {
        'en': '⚠️ HIGH RISK: This asset can lose significant value quickly. Proceed with caution.',
        'es': '⚠️ ALTO RIESGO: Este activo puede perder valor significativo rápidamente. Proceda con precaución.',
        'sw': '⚠️ HATARI YA JUU: Mali hii inaweza kupoteza thamani kubwa haraka. Endelea kwa uangalifu.',
        'ar': '⚠️ مخاطر عالية: يمكن أن يفقد هذا الأصل قيمة كبيرة بسرعة. تابع بحذر.',
        'zh': '⚠️ 高风险：该资产可能迅速损失大量价值。请谨慎操作。'
    }
}


def get_translation(key: str, language: str = 'en') -> str:
    """Get translation for a key in specified language"""
    if key in TRANSLATIONS:
        return TRANSLATIONS[key].get(language, TRANSLATIONS[key]['en'])
    return key  # Return key itself if not found


def get_tier_description(tier: str, language: str = 'en') -> str:
    """Get detailed description for a user tier"""
    descriptions = {
        'beginner': {
            'en': """
**For First-Time Investors**
- Focus on stable, low-risk assets (stablecoins, bonds)
- Maximum safety and capital preservation
- Educational guidance with simple explanations
- Limited to 2% portfolio risk
            """,
            'es': """
**Para Inversores Principiantes**
- Enfoque en activos estables de bajo riesgo (monedas estables, bonos)
- Máxima seguridad y preservación de capital
- Orientación educativa con explicaciones simples
- Limitado al 2% de riesgo de cartera
            """,
            'sw': """
**Kwa Wawekezaji wa Mara ya Kwanza**
- Zingatia mali thabiti zenye hatari ndogo (sarafu thabiti, dhamana)
- Usalama wa juu na uhifadhi wa mtaji
- Mwongozo wa elimu na maelezo rahisi
- Imepunguzwa hadi hatari ya 2% ya mkoba
            """,
            'ar': """
**للمستثمرين لأول مرة**
- التركيز على الأصول المستقرة منخفضة المخاطر (العملات المستقرة والسندات)
- أقصى درجات الأمان والحفاظ على رأس المال
- إرشادات تعليمية مع شروحات بسيطة
- محدود بمخاطر محفظة بنسبة 2%
            """,
            'zh': """
**适合首次投资者**
- 专注于稳定、低风险资产（稳定币、债券）
- 最大安全性和资本保值
- 教育性指导，解释简单
- 投资组合风险限制在 2%
            """
        },
        'intermediate': {
            'en': """
**For Growing Investors**
- Access to major cryptocurrencies (BTC, ETH, etc.)
- Balanced risk-reward with metrics guidance
- Show VaR, Sharpe Ratio, and volatility data
- Up to 5% portfolio risk allowed
            """,
            'es': """
**Para Inversores en Crecimiento**
- Acceso a las principales criptomonedas (BTC, ETH, etc.)
- Riesgo-recompensa equilibrado con orientación de métricas
- Mostrar VaR, Ratio de Sharpe y datos de volatilidad
- Hasta 5% de riesgo de cartera permitido
            """,
            'sw': """
**Kwa Wawekezaji Wanaokua**
- Ufikiaji wa sarafu kuu za crypto (BTC, ETH, n.k.)
- Hatari-tuzo zilizosawazishwa na mwongozo wa vipimo
- Onyesha VaR, Uwiano wa Sharpe, na data ya mabadiliko
- Hadi hatari ya 5% ya mkoba inaruhusiwa
            """,
            'ar': """
**للمستثمرين الناميين**
- الوصول إلى العملات المشفرة الرئيسية (BTC, ETH, إلخ.)
- توازن المخاطر والعوائد مع إرشادات المقاييس
- عرض VaR ونسبة شارب وبيانات التقلب
- يُسمح بمخاطر محفظة تصل إلى 5%
            """,
            'zh': """
**适合成长型投资者**
- 访问主要加密货币（BTC、ETH 等）
- 平衡风险收益，提供指标指导
- 显示 VaR、夏普比率和波动性数据
- 允许高达 5% 的投资组合风险
            """
        },
        'advanced': {
            'en': """
**For Experienced Traders**
- Full access to all assets and strategies
- Technical, data-driven analysis
- Advanced risk metrics (CVaR, Max Drawdown, etc.)
- Up to 10% portfolio risk for high returns
            """,
            'es': """
**Para Traders Experimentados**
- Acceso completo a todos los activos y estrategias
- Análisis técnico basado en datos
- Métricas de riesgo avanzadas (CVaR, Max Drawdown, etc.)
- Hasta 10% de riesgo de cartera para altos retornos
            """,
            'sw': """
**Kwa Wafanyabiashara Wenye Uzoefu**
- Ufikiaji kamili wa mali na mikakati yote
- Uchambuzi wa kiufundi unaotegemea data
- Vipimo vya hatari vya hali ya juu (CVaR, Kuanguka Kwa Juu, n.k.)
- Hadi hatari ya 10% ya mkoba kwa mapato ya juu
            """,
            'ar': """
**للمتداولين ذوي الخبرة**
- وصول كامل لجميع الأصول والاستراتيجيات
- تحليل تقني قائم على البيانات
- مقاييس مخاطر متقدمة (CVaR، الانخفاض الأقصى، إلخ.)
- ما يصل إلى 10% من مخاطر المحفظة للحصول على عوائد عالية
            """
        }
    }
    
    return descriptions.get(tier, {}).get(language, descriptions.get(tier, {}).get('en', ''))


def get_risk_explanation(risk_level: str, language: str = 'en') -> str:
    """Get risk level explanation"""
    explanations = {
        'low': {
            'en': '✅ Low Risk - Safe and stable',
            'es': '✅ Bajo Riesgo - Seguro y estable',
            'sw': '✅ Hatari Ndogo - Salama na thabiti',
            'ar': '✅ مخاطر منخفضة - آمن ومستقر',
            'zh': '✅ 低风险 - 安全稳定'
        },
        'medium': {
            'en': '⚠️ Medium Risk - Some volatility expected',
            'es': '⚠️ Riesgo Medio - Se espera algo de volatilidad',
            'sw': '⚠️ Hatari ya Kati - Mabadiliko yanatarajiwa',
            'ar': '⚠️ مخاطر متوسطة - يُتوقع بعض التقلب',
            'zh': '⚠️ 中等风险 - 预期有一定波动'
        },
        'high': {
            'en': '❌ High Risk - Significant losses possible',
            'es': '❌ Alto Riesgo - Pérdidas significativas posibles',
            'sw': '❌ Hatari ya Juu - Hasara kubwa inawezekana',
            'ar': '❌ مخاطر عالية - خسائر كبيرة محتملة',
            'zh': '❌ 高风险 - 可能有重大损失'
        }
    }
    
    return explanations.get(risk_level, {}).get(language, explanations.get(risk_level, {}).get('en', ''))

