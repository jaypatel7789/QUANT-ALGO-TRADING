"""
SVG Diagrams Generator for GitHub Repository Presentation.
Generates ultra-crisp, high-definition, 100% W3C XML-compliant SVG graphics:
1. Hero Header Banner
2. Complete 5-Tier System Architecture (Validated XML, no raw '&')
3. Mobile Command Center UI Showcase (Sanitized: No private IPs/IDs)
4. Live MT5 Execution & Slippage Retry Flowchart
"""

import os
import xml.etree.ElementTree as ET

os.makedirs("assets", exist_ok=True)

# Universal web-safe font stack that renders crisply on all GitHub environments
FONT_TITLE = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
FONT_MONO = "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', monospace"

# ==========================================
# 1. HERO BANNER
# ==========================================
hero_svg = f'''<svg width="1200" height="340" viewBox="0 0 1200 340" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#060911" />
      <stop offset="50%" stop-color="#0a101d" />
      <stop offset="100%" stop-color="#04060a" />
    </linearGradient>
    <linearGradient id="cyan-glow" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#00f2fe" />
      <stop offset="100%" stop-color="#4facfe" />
    </linearGradient>
    <filter id="glow-blur" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="35" result="blur" />
    </filter>
  </defs>

  <rect width="1200" height="340" rx="16" fill="url(#bg-grad)" stroke="#1e293b" stroke-width="2"/>

  <!-- Ambient Glow Orbs -->
  <circle cx="200" cy="80" r="140" fill="#00f2fe" opacity="0.08" filter="url(#glow-blur)"/>
  <circle cx="1000" cy="220" r="160" fill="#f59e0b" opacity="0.07" filter="url(#glow-blur)"/>
  <circle cx="600" cy="170" r="180" fill="#8b5cf6" opacity="0.05" filter="url(#glow-blur)"/>

  <!-- Grid Pattern Overlay -->
  <g opacity="0.12" stroke="#334155" stroke-width="0.8">
    <line x1="0" y1="60" x2="1200" y2="60"/>
    <line x1="0" y1="120" x2="1200" y2="120"/>
    <line x1="0" y1="180" x2="1200" y2="180"/>
    <line x1="0" y1="240" x2="1200" y2="240"/>
    <line x1="0" y1="300" x2="1200" y2="300"/>
    <line x1="200" y1="0" x2="200" y2="340"/>
    <line x1="400" y1="0" x2="400" y2="340"/>
    <line x1="600" y1="0" x2="600" y2="340"/>
    <line x1="800" y1="0" x2="800" y2="340"/>
    <line x1="1000" y1="0" x2="1000" y2="340"/>
  </g>

  <!-- Top Badge -->
  <rect x="420" y="28" width="360" height="28" rx="14" fill="#0f172a" stroke="#00f2fe" stroke-opacity="0.4" stroke-width="1.2"/>
  <circle cx="438" cy="42" r="4" fill="#10b981"/>
  <text x="452" y="47" font-family="{FONT_MONO}" font-size="11" font-weight="600" fill="#38bdf8" letter-spacing="1.5">INSTITUTIONAL QUANT MULTI-AGENT</text>

  <!-- Title -->
  <text x="600" y="112" font-family="{FONT_TITLE}" font-size="44" font-weight="800" fill="#ffffff" text-anchor="middle" letter-spacing="-0.5">
    SHARK MT5 SENTINEL
  </text>
  <text x="600" y="152" font-family="{FONT_TITLE}" font-size="20" font-weight="600" fill="url(#cyan-glow)" text-anchor="middle" letter-spacing="3">
    CLOUD VPS 24/7 QUANT COMMAND PLATFORM
  </text>

  <!-- Subtitle Description -->
  <text x="600" y="196" font-family="{FONT_TITLE}" font-size="13.5" fill="#94a3b8" text-anchor="middle">
    Multi-Agent Quantitative Alpha Generation • Real Interbank MT5 Tick Verification • Low-Latency Cloud Bridge • Zero-Trust Mobile PWA
  </text>

  <!-- Metric Badges Row -->
  <g transform="translate(180, 235)">
    <rect x="0" y="0" width="180" height="64" rx="8" fill="#0f172a" stroke="#334155" stroke-width="1"/>
    <text x="90" y="24" font-family="{FONT_MONO}" font-size="10" fill="#94a3b8" text-anchor="middle">PORTFOLIO-GOLD-H1</text>
    <text x="90" y="48" font-family="{FONT_TITLE}" font-size="17" font-weight="700" fill="#fbbf24" text-anchor="middle">+37.84% (PF 1.72)</text>

    <rect x="220" y="0" width="180" height="64" rx="8" fill="#0f172a" stroke="#334155" stroke-width="1"/>
    <text x="310" y="24" font-family="{FONT_MONO}" font-size="10" fill="#94a3b8" text-anchor="middle">EUR MASTER ELITE</text>
    <text x="310" y="48" font-family="{FONT_TITLE}" font-size="17" font-weight="700" fill="#10b981" text-anchor="middle">76.6% WIN (PF 3.09)</text>

    <rect x="440" y="0" width="180" height="64" rx="8" fill="#0f172a" stroke="#334155" stroke-width="1"/>
    <text x="530" y="24" font-family="{FONT_MONO}" font-size="10" fill="#94a3b8" text-anchor="middle">BTC-011 VPIN TOXICITY</text>
    <text x="530" y="48" font-family="{FONT_TITLE}" font-size="17" font-weight="700" fill="#38bdf8" text-anchor="middle">+26.91% (DD 6.1%)</text>

    <rect x="660" y="0" width="180" height="64" rx="8" fill="#0f172a" stroke="#334155" stroke-width="1"/>
    <text x="750" y="24" font-family="{FONT_MONO}" font-size="10" fill="#94a3b8" text-anchor="middle">CLOUD SUPERVISOR</text>
    <text x="750" y="48" font-family="{FONT_TITLE}" font-size="17" font-weight="700" fill="#c084fc" text-anchor="middle">24/7 CLOUD DAEMON</text>
  </g>
</svg>'''

# ==========================================
# 2. SYSTEM ARCHITECTURE SVG (100% Valid XML)
# ==========================================
arch_svg = f'''<svg width="1200" height="760" viewBox="0 0 1200 760" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="tier-bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0d1424" />
      <stop offset="100%" stop-color="#080c16" />
    </linearGradient>
  </defs>

  <!-- Canvas Background -->
  <rect width="1200" height="760" rx="16" fill="#050811" stroke="#1e293b" stroke-width="2"/>

  <!-- Title Area -->
  <text x="600" y="45" font-family="{FONT_TITLE}" font-size="26" font-weight="800" fill="#ffffff" text-anchor="middle">
    SHARK MT5 SENTINEL — END-TO-END PRODUCTION ARCHITECTURE
  </text>
  <text x="600" y="70" font-family="{FONT_MONO}" font-size="12" fill="#94a3b8" text-anchor="middle">
    High-Frequency Data Ingestion • Multi-Agent Optimization • Cloud VPS Bridge • Mobile Command Center
  </text>

  <!-- TIER 1: DATA INGESTION & MARKET MICROSTRUCTURE -->
  <g transform="translate(40, 100)">
    <rect width="250" height="610" rx="12" fill="url(#tier-bg)" stroke="#1e293b" stroke-width="1.5"/>
    <rect width="250" height="38" rx="12" fill="#0f172a" stroke="#1e293b"/>
    <text x="125" y="24" font-family="{FONT_TITLE}" font-size="14" font-weight="700" fill="#38bdf8" text-anchor="middle">1. DATA INGESTION</text>

    <!-- Card 1 -->
    <rect x="15" y="55" width="220" height="95" rx="8" fill="#131c2e" stroke="#334155"/>
    <text x="25" y="78" font-family="{FONT_TITLE}" font-size="12" font-weight="700" fill="#f8fafc">Interbank Real-Tick Feed</text>
    <text x="25" y="98" font-family="{FONT_TITLE}" font-size="10.5" fill="#94a3b8">• EURUSD, XAUUSD, BTCUSD</text>
    <text x="25" y="115" font-family="{FONT_TITLE}" font-size="10.5" fill="#94a3b8">• 100% Real-Tick Precision</text>
    <text x="25" y="132" font-family="{FONT_TITLE}" font-size="10.5" fill="#94a3b8">• Spread &amp; Rollover Swap Modeling</text>

    <!-- Card 2 -->
    <rect x="15" y="165" width="220" height="110" rx="8" fill="#131c2e" stroke="#334155"/>
    <text x="25" y="188" font-family="{FONT_TITLE}" font-size="12" font-weight="700" fill="#f8fafc">Order Book &amp; Microstructure</text>
    <text x="25" y="208" font-family="{FONT_TITLE}" font-size="10.5" fill="#94a3b8">• Binance Futures L2 Depth</text>
    <text x="25" y="225" font-family="{FONT_TITLE}" font-size="10.5" fill="#94a3b8">• VPIN Volume Toxicity Buckets</text>
    <text x="25" y="242" font-family="{FONT_TITLE}" font-size="10.5" fill="#94a3b8">• Kyle's Lambda Impact Estimator</text>
    <text x="25" y="259" font-family="{FONT_TITLE}" font-size="10.5" fill="#94a3b8">• Depth Exhaustion Cascade</text>

    <!-- Card 3 -->
    <rect x="15" y="290" width="220" height="100" rx="8" fill="#131c2e" stroke="#334155"/>
    <text x="25" y="313" font-family="{FONT_TITLE}" font-size="12" font-weight="700" fill="#f8fafc">Derivatives &amp; Macro Ingestion</text>
    <text x="25" y="333" font-family="{FONT_TITLE}" font-size="10.5" fill="#94a3b8">• Deribit IV Surface Smile Skew</text>
    <text x="25" y="350" font-family="{FONT_TITLE}" font-size="10.5" fill="#94a3b8">• Dealer Gamma Pinning Levels</text>
    <text x="25" y="367" font-family="{FONT_TITLE}" font-size="10.5" fill="#94a3b8">• 8-Hour Funding Arbitrage Filter</text>

    <!-- Card 4 -->
    <rect x="15" y="405" width="220" height="100" rx="8" fill="#131c2e" stroke="#334155"/>
    <text x="25" y="428" font-family="{FONT_TITLE}" font-size="12" font-weight="700" fill="#f8fafc">Macroeconomic News Scraper</text>
    <text x="25" y="448" font-family="{FONT_TITLE}" font-size="10.5" fill="#94a3b8">• High-Impact Economic Events</text>
    <text x="25" y="465" font-family="{FONT_TITLE}" font-size="10.5" fill="#94a3b8">• USD, EUR, GBP Volatility Shock</text>
    <text x="25" y="482" font-family="{FONT_TITLE}" font-size="10.5" fill="#94a3b8">• IST vs UTC Clock Synchronization</text>

    <!-- Card 5 -->
    <rect x="15" y="520" width="220" height="75" rx="8" fill="#131c2e" stroke="#334155"/>
    <text x="25" y="543" font-family="{FONT_TITLE}" font-size="12" font-weight="700" fill="#f8fafc">Feature Engineering Matrix</text>
    <text x="25" y="563" font-family="{FONT_TITLE}" font-size="10.5" fill="#94a3b8">• Normalized Volatility Ratios</text>
    <text x="25" y="580" font-family="{FONT_TITLE}" font-size="10.5" fill="#94a3b8">• Anchored Session VWAP Bands</text>
  </g>

  <!-- TIER 2: QUANT RESEARCH & BACKTESTING ENGINE -->
  <g transform="translate(325, 100)">
    <rect width="250" height="610" rx="12" fill="url(#tier-bg)" stroke="#1e293b" stroke-width="1.5"/>
    <rect width="250" height="38" rx="12" fill="#0f172a" stroke="#1e293b"/>
    <text x="125" y="24" font-family="{FONT_TITLE}" font-size="14" font-weight="700" fill="#fbbf24" text-anchor="middle">2. QUANT ENGINE</text>

    <rect x="15" y="55" width="220" height="110" rx="8" fill="#131c2e" stroke="#f59e0b" stroke-opacity="0.3"/>
    <text x="25" y="78" font-family="{FONT_TITLE}" font-size="12" font-weight="700" fill="#fbbf24">Gold Spot Modules (GOLD.i#)</text>
    <text x="25" y="98" font-family="{FONT_TITLE}" font-size="10.5" fill="#cbd5e1">• PORTFOLIO-GOLD-H1 (+37.8%)</text>
    <text x="25" y="115" font-family="{FONT_TITLE}" font-size="10.5" fill="#cbd5e1">• GOLD-CUSTOM London VWAP</text>
    <text x="25" y="132" font-family="{FONT_TITLE}" font-size="10.5" fill="#cbd5e1">• XAU-024 London ORB Expansion</text>
    <text x="25" y="149" font-family="{FONT_TITLE}" font-size="10.5" fill="#cbd5e1">• AlphaMaster 4-Engine Ensemble</text>

    <rect x="15" y="180" width="220" height="110" rx="8" fill="#131c2e" stroke="#10b981" stroke-opacity="0.3"/>
    <text x="25" y="203" font-family="{FONT_TITLE}" font-size="12" font-weight="700" fill="#34d399">EURUSD Modules (Interbank)</text>
    <text x="25" y="223" font-family="{FONT_TITLE}" font-size="10.5" fill="#cbd5e1">• EUR Master Elite (76.6% Win, PF 3.09)</text>
    <text x="25" y="240" font-family="{FONT_TITLE}" font-size="10.5" fill="#cbd5e1">• EUR-031 Dual Confluence (80% Win)</text>
    <text x="25" y="257" font-family="{FONT_TITLE}" font-size="10.5" fill="#cbd5e1">• EUR-027B Macro Cascade + BE</text>
    <text x="25" y="274" font-family="{FONT_TITLE}" font-size="10.5" fill="#cbd5e1">• EUR-005B London ORB BreakEven</text>

    <rect x="15" y="305" width="220" height="110" rx="8" fill="#131c2e" stroke="#38bdf8" stroke-opacity="0.3"/>
    <text x="25" y="328" font-family="{FONT_TITLE}" font-size="12" font-weight="700" fill="#38bdf8">BTCUSD Modules (Derivatives)</text>
    <text x="25" y="348" font-family="{FONT_TITLE}" font-size="10.5" fill="#cbd5e1">• BTC-011 VPIN Flow Toxicity (+26.9%)</text>
    <text x="25" y="365" font-family="{FONT_TITLE}" font-size="10.5" fill="#cbd5e1">• BTC-018 Markov Volatility Regime</text>
    <text x="25" y="382" font-family="{FONT_TITLE}" font-size="10.5" fill="#cbd5e1">• BTC-CUSTOM Volatility Ratio Breakout</text>
    <text x="25" y="399" font-family="{FONT_TITLE}" font-size="10.5" fill="#cbd5e1">• PORTFOLIO-BTC-H1 (+27.5%)</text>

    <rect x="15" y="430" width="220" height="165" rx="8" fill="#131c2e" stroke="#334155"/>
    <text x="25" y="453" font-family="{FONT_TITLE}" font-size="12" font-weight="700" fill="#f8fafc">Institutional Risk Filters</text>
    <text x="25" y="473" font-family="{FONT_TITLE}" font-size="10.5" fill="#94a3b8">• 1-Year Real-Tick Walk-Forward</text>
    <text x="25" y="490" font-family="{FONT_TITLE}" font-size="10.5" fill="#94a3b8">• Monte Carlo Reshuffling (99% Conf)</text>
    <text x="25" y="507" font-family="{FONT_TITLE}" font-size="10.5" fill="#94a3b8">• Max DD Limit: Strict &lt; 8.0%</text>
    <text x="25" y="524" font-family="{FONT_TITLE}" font-size="10.5" fill="#94a3b8">• Daily Loss Limit: Strict &lt; 5.0%</text>
    <text x="25" y="541" font-family="{FONT_TITLE}" font-size="10.5" fill="#94a3b8">• Profit Factor Floor: &gt; 1.50</text>
    <text x="25" y="558" font-family="{FONT_TITLE}" font-size="10.5" fill="#94a3b8">• Minimum Trades: &gt; 50 Per Cycle</text>
    <text x="25" y="575" font-family="{FONT_TITLE}" font-size="10.5" fill="#10b981">✓ Prop-Firm Challenge Certified</text>
  </g>

  <!-- TIER 3: SENTINEL CLOUD VPS & MT5 BRIDGE -->
  <g transform="translate(610, 100)">
    <rect width="250" height="610" rx="12" fill="url(#tier-bg)" stroke="#1e293b" stroke-width="1.5"/>
    <rect width="250" height="38" rx="12" fill="#0f172a" stroke="#1e293b"/>
    <text x="125" y="24" font-family="{FONT_TITLE}" font-size="14" font-weight="700" fill="#a855f7" text-anchor="middle">3. CLOUD VPS BRIDGE</text>

    <rect x="15" y="55" width="220" height="110" rx="8" fill="#131c2e" stroke="#334155"/>
    <text x="25" y="78" font-family="{FONT_TITLE}" font-size="12" font-weight="700" fill="#f8fafc">Dedicated Cloud VPS</text>
    <text x="25" y="98" font-family="{FONT_TITLE}" font-size="10.5" fill="#94a3b8">• High-Availability Windows Host</text>
    <text x="25" y="115" font-family="{FONT_TITLE}" font-size="10.5" fill="#94a3b8">• 24/7 Background System Daemon</text>
    <text x="25" y="132" font-family="{FONT_TITLE}" font-size="10.5" fill="#94a3b8">• Auto-Boot on Crash / Restart</text>
    <text x="25" y="149" font-family="{FONT_TITLE}" font-size="10.5" fill="#94a3b8">• Low-Latency Broker Cross-Connect</text>

    <rect x="15" y="180" width="220" height="115" rx="8" fill="#131c2e" stroke="#334155"/>
    <text x="25" y="203" font-family="{FONT_TITLE}" font-size="12" font-weight="700" fill="#f8fafc">FastAPI Sentinel Backend</text>
    <text x="25" y="223" font-family="{FONT_TITLE}" font-size="10.5" fill="#94a3b8">• High-Throughput REST + WebSocket</text>
    <text x="25" y="240" font-family="{FONT_TITLE}" font-size="10.5" fill="#94a3b8">• SHA-256 PIN Security Gate</text>
    <text x="25" y="257" font-family="{FONT_TITLE}" font-size="10.5" fill="#94a3b8">• IP Brute-Force Rate Limiting</text>
    <text x="25" y="274" font-family="{FONT_TITLE}" font-size="10.5" fill="#94a3b8">• Atomic JSON State Persistence</text>

    <rect x="15" y="310" width="220" height="135" rx="8" fill="#131c2e" stroke="#334155"/>
    <text x="25" y="333" font-family="{FONT_TITLE}" font-size="12" font-weight="700" fill="#f8fafc">MT5 Execution Engine</text>
    <text x="25" y="353" font-family="{FONT_TITLE}" font-size="10.5" fill="#94a3b8">• MetaTrader 5 Python IPC Driver</text>
    <text x="25" y="370" font-family="{FONT_TITLE}" font-size="10.5" fill="#94a3b8">• IOC / FOK / Return Retry Ladder</text>
    <text x="25" y="387" font-family="{FONT_TITLE}" font-size="10.5" fill="#94a3b8">• Sandbox Policy Synchronization</text>
    <text x="25" y="404" font-family="{FONT_TITLE}" font-size="10.5" fill="#94a3b8">• 2-Second Hold Panic Liquidation</text>
    <text x="25" y="421" font-family="{FONT_TITLE}" font-size="10.5" fill="#94a3b8">• Dynamic Slippage Backoff</text>

    <rect x="15" y="460" width="220" height="135" rx="8" fill="#131c2e" stroke="#334155"/>
    <text x="25" y="483" font-family="{FONT_TITLE}" font-size="12" font-weight="700" fill="#f8fafc">Cloudflare Zero-Trust Tunnel</text>
    <text x="25" y="503" font-family="{FONT_TITLE}" font-size="10.5" fill="#94a3b8">• Encrypted Edge Reverse-Proxy</text>
    <text x="25" y="520" font-family="{FONT_TITLE}" font-size="10.5" fill="#94a3b8">• Zero Open Inbound Firewall Ports</text>
    <text x="25" y="537" font-family="{FONT_TITLE}" font-size="10.5" fill="#94a3b8">• TLS 1.3 End-to-End Encryption</text>
    <text x="25" y="554" font-family="{FONT_TITLE}" font-size="10.5" fill="#94a3b8">• Global Anycast Edge Routing</text>
    <text x="25" y="571" font-family="{FONT_TITLE}" font-size="10.5" fill="#10b981">✓ Secure Mobile Command Anywhere</text>
  </g>

  <!-- TIER 4: MOBILE COMMAND CENTER PWA -->
  <g transform="translate(895, 100)">
    <rect width="265" height="610" rx="12" fill="url(#tier-bg)" stroke="#1e293b" stroke-width="1.5"/>
    <rect width="265" height="38" rx="12" fill="#0f172a" stroke="#1e293b"/>
    <text x="132" y="24" font-family="{FONT_TITLE}" font-size="14" font-weight="700" fill="#10b981" text-anchor="middle">4. MOBILE COMMAND</text>

    <rect x="15" y="55" width="235" height="95" rx="8" fill="#131c2e" stroke="#334155"/>
    <text x="25" y="78" font-family="{FONT_TITLE}" font-size="12" font-weight="700" fill="#f8fafc">Biometric &amp; PIN Security</text>
    <text x="25" y="98" font-family="{FONT_TITLE}" font-size="10.5" fill="#94a3b8">• Hardware FaceID / Fingerprint</text>
    <text x="25" y="115" font-family="{FONT_TITLE}" font-size="10.5" fill="#94a3b8">• 4-Digit Security PIN Gateway</text>
    <text x="25" y="132" font-family="{FONT_TITLE}" font-size="10.5" fill="#94a3b8">• Auto-Lock on Backgrounding</text>

    <rect x="15" y="165" width="235" height="110" rx="8" fill="#131c2e" stroke="#334155"/>
    <text x="25" y="188" font-family="{FONT_TITLE}" font-size="12" font-weight="700" fill="#f8fafc">Prop-Firm Risk Shield</text>
    <text x="25" y="208" font-family="{FONT_TITLE}" font-size="10.5" fill="#94a3b8">• Real-Time Daily Loss Floor Meter</text>
    <text x="25" y="225" font-family="{FONT_TITLE}" font-size="10.5" fill="#94a3b8">• Max Trailing Drawdown Meter</text>
    <text x="25" y="242" font-family="{FONT_TITLE}" font-size="10.5" fill="#94a3b8">• Visual Warning Thresholds</text>
    <text x="25" y="259" font-family="{FONT_TITLE}" font-size="10.5" fill="#94a3b8">• Auto-Freeze Execution Safeguard</text>

    <rect x="15" y="290" width="235" height="100" rx="8" fill="#131c2e" stroke="#334155"/>
    <text x="25" y="313" font-family="{FONT_TITLE}" font-size="12" font-weight="700" fill="#f8fafc">Interactive Equity Trajectory</text>
    <text x="25" y="333" font-family="{FONT_TITLE}" font-size="10.5" fill="#94a3b8">• High-DPI HTML5 Canvas Chart</text>
    <text x="25" y="350" font-family="{FONT_TITLE}" font-size="10.5" fill="#94a3b8">• Target Projection (+8%)</text>
    <text x="25" y="367" font-family="{FONT_TITLE}" font-size="10.5" fill="#94a3b8">• Touch Scrubbing Tooltip Inspector</text>

    <rect x="15" y="405" width="235" height="95" rx="8" fill="#131c2e" stroke="#334155"/>
    <text x="25" y="428" font-family="{FONT_TITLE}" font-size="12" font-weight="700" fill="#f8fafc">16 Strategy Control Grid</text>
    <text x="25" y="448" font-family="{FONT_TITLE}" font-size="10.5" fill="#94a3b8">• Individual EA Enable / Disable</text>
    <text x="25" y="465" font-family="{FONT_TITLE}" font-size="10.5" fill="#94a3b8">• Master Kill Switch Override</text>
    <text x="25" y="482" font-family="{FONT_TITLE}" font-size="10.5" fill="#94a3b8">• Magic Number Live Attribution</text>

    <rect x="15" y="515" width="235" height="80" rx="8" fill="#131c2e" stroke="#334155"/>
    <text x="25" y="538" font-family="{FONT_TITLE}" font-size="12" font-weight="700" fill="#f8fafc">MT5 Terminal Log Stream</text>
    <text x="25" y="558" font-family="{FONT_TITLE}" font-size="10.5" fill="#94a3b8">• Direct WebSocket Pipe from MT5</text>
    <text x="25" y="575" font-family="{FONT_TITLE}" font-size="10.5" fill="#94a3b8">• Order Fills, Rejections &amp; BE Locks</text>
  </g>

  <!-- Flow Arrows connecting tiers -->
  <g stroke="#00f2fe" stroke-width="2" stroke-dasharray="4 4" opacity="0.6">
    <line x1="290" y1="200" x2="325" y2="200"/>
    <line x1="290" y1="350" x2="325" y2="350"/>
    <line x1="290" y1="500" x2="325" y2="500"/>

    <line x1="575" y1="200" x2="610" y2="200"/>
    <line x1="575" y1="350" x2="610" y2="350"/>
    <line x1="575" y1="500" x2="610" y2="500"/>

    <line x1="860" y1="200" x2="895" y2="200"/>
    <line x1="860" y1="350" x2="895" y2="350"/>
    <line x1="860" y1="500" x2="895" y2="500"/>
  </g>
</svg>'''

# ==========================================
# 3. MOBILE COMMAND CENTER UI MOCKUP SVG (Sanitized: No Private IDs/IPs)
# ==========================================
mockup_svg = f'''<svg width="1000" height="600" viewBox="0 0 1000 600" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="phone-bg" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#0a0e17" />
      <stop offset="100%" stop-color="#05070d" />
    </linearGradient>
    <linearGradient id="card-glass" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#131c2e" stop-opacity="0.8" />
      <stop offset="100%" stop-color="#0d1424" stop-opacity="0.9" />
    </linearGradient>
    <linearGradient id="panic-btn" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#ef4444" />
      <stop offset="100%" stop-color="#b91c1c" />
    </linearGradient>
  </defs>

  <rect width="1000" height="600" rx="16" fill="#04060b" stroke="#1e293b" stroke-width="2"/>

  <!-- Left: Explanatory Callouts -->
  <g transform="translate(60, 50)">
    <text x="0" y="30" font-family="{FONT_TITLE}" font-size="28" font-weight="800" fill="#ffffff">MOBILE COMMAND CENTER</text>
    <text x="0" y="55" font-family="{FONT_MONO}" font-size="12" fill="#38bdf8">PROGRESSIVE WEB APPLICATION (PWA) • SECURE WEBSOCKET</text>

    <!-- Point 1 -->
    <circle cx="10" cy="110" r="10" fill="#0f172a" stroke="#00f2fe" stroke-width="1.5"/>
    <text x="10" y="114" font-family="{FONT_TITLE}" font-size="11" font-weight="700" fill="#00f2fe" text-anchor="middle">1</text>
    <text x="35" y="105" font-family="{FONT_TITLE}" font-size="14" font-weight="700" fill="#f8fafc">Biometric &amp; PIN Defense</text>
    <text x="35" y="123" font-family="{FONT_TITLE}" font-size="11" fill="#94a3b8">SHA-256 gated 4-digit PIN with hardware FaceID integration.</text>

    <!-- Point 2 -->
    <circle cx="10" cy="180" r="10" fill="#0f172a" stroke="#fbbf24" stroke-width="1.5"/>
    <text x="10" y="184" font-family="{FONT_TITLE}" font-size="11" font-weight="700" fill="#fbbf24" text-anchor="middle">2</text>
    <text x="35" y="175" font-family="{FONT_TITLE}" font-size="14" font-weight="700" fill="#f8fafc">Prop-Firm Risk Shield</text>
    <text x="35" y="193" font-family="{FONT_TITLE}" font-size="11" fill="#94a3b8">Real-time daily loss floor and max trailing drawdown meters.</text>

    <!-- Point 3 -->
    <circle cx="10" cy="250" r="10" fill="#0f172a" stroke="#ef4444" stroke-width="1.5"/>
    <text x="10" y="254" font-family="{FONT_TITLE}" font-size="11" font-weight="700" fill="#ef4444" text-anchor="middle">3</text>
    <text x="35" y="245" font-family="{FONT_TITLE}" font-size="14" font-weight="700" fill="#f8fafc">2-Second Hold Panic Liquidation</text>
    <text x="35" y="263" font-family="{FONT_TITLE}" font-size="11" fill="#94a3b8">Emergency kill switch that liquidates all positions across MT5 instantly.</text>

    <!-- Point 4 -->
    <circle cx="10" cy="320" r="10" fill="#0f172a" stroke="#10b981" stroke-width="1.5"/>
    <text x="10" y="324" font-family="{FONT_TITLE}" font-size="11" font-weight="700" fill="#10b981" text-anchor="middle">4</text>
    <text x="35" y="315" font-family="{FONT_TITLE}" font-size="14" font-weight="700" fill="#f8fafc">16 Algorithm Control Grid</text>
    <text x="35" y="333" font-family="{FONT_TITLE}" font-size="11" fill="#94a3b8">Granular switches for BTC, Gold, and EUR quantitative strategy engines.</text>

    <!-- Point 5 -->
    <circle cx="10" cy="390" r="10" fill="#0f172a" stroke="#a855f7" stroke-width="1.5"/>
    <text x="10" y="394" font-family="{FONT_TITLE}" font-size="11" font-weight="700" fill="#a855f7" text-anchor="middle">5</text>
    <text x="35" y="385" font-family="{FONT_TITLE}" font-size="14" font-weight="700" fill="#f8fafc">High-Impact News Shield</text>
    <text x="35" y="403" font-family="{FONT_TITLE}" font-size="11" fill="#94a3b8">Auto-freezes trading 30m before and 15m after major macroeconomic shocks.</text>

    <!-- Cloud VPS Live Status Box (Sanitized) -->
    <rect x="0" y="440" width="460" height="75" rx="8" fill="#0f172a" stroke="#334155"/>
    <circle cx="25" cy="465" r="5" fill="#10b981"/>
    <text x="38" y="469" font-family="{FONT_TITLE}" font-size="13" font-weight="700" fill="#10b981">LIVE CLOUD VPS STATUS: ACTIVE 24/7</text>
    <text x="38" y="492" font-family="{FONT_MONO}" font-size="10.5" fill="#94a3b8">Dedicated Cloud Server | Native MT5 Interbank Bridge | 100% Uptime</text>
  </g>

  <!-- Right: Mobile Device Frame Preview -->
  <g transform="translate(600, 30)">
    <rect width="340" height="540" rx="36" fill="#000000" stroke="#334155" stroke-width="4"/>
    <rect x="12" y="12" width="316" height="516" rx="26" fill="url(#phone-bg)"/>

    <rect x="120" y="18" width="100" height="14" rx="7" fill="#000000"/>

    <!-- App Top Bar -->
    <g transform="translate(25, 45)">
      <text x="0" y="16" font-family="{FONT_TITLE}" font-size="13" font-weight="800" fill="#f8fafc" letter-spacing="1">SHARK SENTINEL</text>
      <text x="0" y="27" font-family="{FONT_MONO}" font-size="8" fill="#38bdf8">CLOUD MT5 COMMAND</text>
      
      <rect x="195" y="5" width="75" height="18" rx="9" fill="#10b981" fill-opacity="0.15" stroke="#10b981" stroke-width="0.8"/>
      <circle cx="206" cy="14" r="3" fill="#10b981"/>
      <text x="214" y="17" font-family="{FONT_MONO}" font-size="8" font-weight="600" fill="#10b981">ONLINE</text>
    </g>

    <!-- Master Banner -->
    <g transform="translate(25, 85)">
      <rect width="290" height="36" rx="8" fill="#10b981" fill-opacity="0.1" stroke="#10b981" stroke-opacity="0.3"/>
      <text x="12" y="15" font-family="{FONT_MONO}" font-size="8" fill="#94a3b8">MASTER ALGO TRADING</text>
      <text x="12" y="27" font-family="{FONT_TITLE}" font-size="11" font-weight="700" fill="#10b981">RUNNING (16 ALGOS)</text>
      <rect x="240" y="8" width="38" height="20" rx="10" fill="#10b981"/>
      <circle cx="266" cy="18" r="7" fill="#ffffff"/>
    </g>

    <!-- Account Overview Card (Sanitized) -->
    <g transform="translate(25, 130)">
      <rect width="290" height="110" rx="12" fill="url(#card-glass)" stroke="#1e293b"/>
      <text x="15" y="22" font-family="{FONT_MONO}" font-size="9" fill="#94a3b8">TOTAL LIVE EQUITY</text>
      <text x="15" y="50" font-family="{FONT_TITLE}" font-size="24" font-weight="800" fill="#ffffff">$10,131.25</text>
      <text x="170" y="48" font-family="{FONT_TITLE}" font-size="13" font-weight="700" fill="#10b981">+$131.25 (+1.3%)</text>

      <line x1="15" y1="65" x2="275" y2="65" stroke="#1e293b"/>

      <text x="15" y="82" font-family="{FONT_MONO}" font-size="8" fill="#64748b">Balance</text>
      <text x="15" y="98" font-family="{FONT_TITLE}" font-size="11" font-weight="700" fill="#cbd5e1">$10,000.00</text>

      <text x="95" y="82" font-family="{FONT_MONO}" font-size="8" fill="#64748b">Free Margin</text>
      <text x="95" y="98" font-family="{FONT_TITLE}" font-size="11" font-weight="700" fill="#cbd5e1">$9,814.80</text>

      <text x="185" y="82" font-family="{FONT_MONO}" font-size="8" fill="#64748b">Margin Level</text>
      <text x="185" y="98" font-family="{FONT_TITLE}" font-size="11" font-weight="700" fill="#38bdf8">5,510%</text>
    </g>

    <!-- Prop Firm Meters -->
    <g transform="translate(25, 250)">
      <rect width="290" height="75" rx="10" fill="url(#card-glass)" stroke="#1e293b"/>
      <text x="12" y="18" font-family="{FONT_MONO}" font-size="8.5" font-weight="700" fill="#cbd5e1">PROP-FIRM RISK SHIELD</text>
      <text x="225" y="18" font-family="{FONT_MONO}" font-size="8" fill="#10b981">PROTECTED</text>

      <text x="12" y="36" font-family="{FONT_TITLE}" font-size="8" fill="#94a3b8">Daily Loss Floor ($450 max)</text>
      <text x="235" y="36" font-family="{FONT_MONO}" font-size="8" fill="#10b981">$0.00</text>
      <rect x="12" y="42" width="266" height="5" rx="2.5" fill="#0f172a"/>
      <rect x="12" y="42" width="8" height="5" rx="2.5" fill="#10b981"/>

      <text x="12" y="58" font-family="{FONT_TITLE}" font-size="8" fill="#94a3b8">Trailing Drawdown ($800 max)</text>
      <text x="235" y="58" font-family="{FONT_MONO}" font-size="8" fill="#10b981">$0.00</text>
      <rect x="12" y="64" width="266" height="5" rx="2.5" fill="#0f172a"/>
      <rect x="12" y="64" width="6" height="5" rx="2.5" fill="#10b981"/>
    </g>

    <!-- Action Buttons -->
    <g transform="translate(25, 335)">
      <rect width="140" height="42" rx="8" fill="url(#panic-btn)"/>
      <text x="70" y="26" font-family="{FONT_TITLE}" font-size="10.5" font-weight="700" fill="#ffffff" text-anchor="middle">PANIC CLOSE ALL</text>

      <rect x="150" width="140" height="42" rx="8" fill="#131c2e" stroke="#334155"/>
      <text x="220" y="26" font-family="{FONT_TITLE}" font-size="10.5" font-weight="700" fill="#38bdf8" text-anchor="middle">NEWS SHIELD: ON</text>
    </g>

    <!-- Mini Trades List -->
    <g transform="translate(25, 388)">
      <rect width="290" height="80" rx="10" fill="url(#card-glass)" stroke="#1e293b"/>
      <text x="12" y="20" font-family="{FONT_TITLE}" font-size="10" font-weight="700" fill="#f8fafc">ACTIVE TRADES ATTRIBUTION</text>
      
      <text x="12" y="42" font-family="{FONT_MONO}" font-size="9" font-weight="700" fill="#fbbf24">BUY 0.05 GOLD.i#</text>
      <text x="12" y="55" font-family="{FONT_TITLE}" font-size="7.5" fill="#64748b">Magic 14024 • London ORB</text>
      <text x="230" y="45" font-family="{FONT_MONO}" font-size="10" font-weight="700" fill="#10b981">+$84.50</text>

      <text x="12" y="70" font-family="{FONT_MONO}" font-size="9" font-weight="700" fill="#38bdf8">BUY 0.02 BTCUSD#</text>
      <text x="230" y="72" font-family="{FONT_MONO}" font-size="10" font-weight="700" fill="#10b981">+$46.75</text>
    </g>

    <!-- Bottom Navigation Bar -->
    <g transform="translate(25, 480)">
      <rect width="290" height="38" rx="19" fill="#0c121f" stroke="#1e293b"/>
      <text x="35" y="24" font-family="{FONT_TITLE}" font-size="9" font-weight="700" fill="#00f2fe" text-anchor="middle">Dashboard</text>
      <text x="95" y="24" font-family="{FONT_TITLE}" font-size="9" fill="#64748b" text-anchor="middle">Trades</text>
      <text x="155" y="24" font-family="{FONT_TITLE}" font-size="9" fill="#64748b" text-anchor="middle">Algos (16)</text>
      <text x="215" y="24" font-family="{FONT_TITLE}" font-size="9" fill="#64748b" text-anchor="middle">News</text>
      <text x="265" y="24" font-family="{FONT_TITLE}" font-size="9" fill="#64748b" text-anchor="middle">Logs</text>
    </g>
  </g>
</svg>'''

# ==========================================
# 4. EXECUTION FLOW SVG
# ==========================================
flow_svg = f'''<svg width="1100" height="380" viewBox="0 0 1100 380" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="step-bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0f172a" />
      <stop offset="100%" stop-color="#0a0f1d" />
    </linearGradient>
  </defs>

  <rect width="1100" height="380" rx="16" fill="#040711" stroke="#1e293b" stroke-width="2"/>

  <text x="550" y="40" font-family="{FONT_TITLE}" font-size="22" font-weight="800" fill="#ffffff" text-anchor="middle">
    LIVE EXECUTION RETRY LADDER &amp; SUPERVISOR FLOW
  </text>
  <text x="550" y="65" font-family="{FONT_MONO}" font-size="11" fill="#94a3b8" text-anchor="middle">
    Sub-Millisecond Order Routing • Slippage Backoff • Atomic State Guard
  </text>

  <!-- Step 1 -->
  <g transform="translate(50, 100)">
    <rect width="170" height="220" rx="10" fill="url(#step-bg)" stroke="#38bdf8" stroke-width="1.2"/>
    <rect width="170" height="30" rx="10" fill="#0284c7" fill-opacity="0.2"/>
    <text x="85" y="20" font-family="{FONT_TITLE}" font-size="11" font-weight="700" fill="#38bdf8" text-anchor="middle">1. ALPHA TRIGGER</text>
    <text x="15" y="55" font-family="{FONT_TITLE}" font-size="10.5" fill="#cbd5e1">• Strategy Bar Close</text>
    <text x="15" y="75" font-family="{FONT_TITLE}" font-size="10.5" fill="#cbd5e1">• Microstructure Filter</text>
    <text x="15" y="95" font-family="{FONT_TITLE}" font-size="10.5" fill="#cbd5e1">• VPIN Toxicity Gate</text>
    <text x="15" y="115" font-family="{FONT_TITLE}" font-size="10.5" fill="#cbd5e1">• ADX &gt;= 22.0 Regime</text>
    <text x="15" y="145" font-family="{FONT_MONO}" font-size="9" fill="#94a3b8">Payload generated with StopLoss &amp; TakeProfit</text>
  </g>

  <!-- Arrow 1 -->
  <line x1="225" y1="210" x2="265" y2="210" stroke="#00f2fe" stroke-width="2" stroke-dasharray="4 4"/>
  <polygon points="265,210 257,205 257,215" fill="#00f2fe"/>

  <!-- Step 2 -->
  <g transform="translate(270, 100)">
    <rect width="170" height="220" rx="10" fill="url(#step-bg)" stroke="#f59e0b" stroke-width="1.2"/>
    <rect width="170" height="30" rx="10" fill="#d97706" fill-opacity="0.2"/>
    <text x="85" y="20" font-family="{FONT_TITLE}" font-size="11" font-weight="700" fill="#fbbf24" text-anchor="middle">2. SENTINEL SHIELD</text>
    <text x="15" y="55" font-family="{FONT_TITLE}" font-size="10.5" fill="#cbd5e1">• Master Algo Enabled?</text>
    <text x="15" y="75" font-family="{FONT_TITLE}" font-size="10.5" fill="#cbd5e1">• EA Magic Active?</text>
    <text x="15" y="95" font-family="{FONT_TITLE}" font-size="10.5" fill="#cbd5e1">• News Shield Standby?</text>
    <text x="15" y="115" font-family="{FONT_TITLE}" font-size="10.5" fill="#cbd5e1">• Daily Floor Intact?</text>
    <text x="15" y="145" font-family="{FONT_MONO}" font-size="9" fill="#10b981">✓ All 4 Guards Passed</text>
  </g>

  <!-- Arrow 2 -->
  <line x1="445" y1="210" x2="485" y2="210" stroke="#00f2fe" stroke-width="2" stroke-dasharray="4 4"/>
  <polygon points="485,210 477,205 477,215" fill="#00f2fe"/>

  <!-- Step 3 -->
  <g transform="translate(490, 100)">
    <rect width="170" height="220" rx="10" fill="url(#step-bg)" stroke="#10b981" stroke-width="1.2"/>
    <rect width="170" height="30" rx="10" fill="#059669" fill-opacity="0.2"/>
    <text x="85" y="20" font-family="{FONT_TITLE}" font-size="11" font-weight="700" fill="#10b981" text-anchor="middle">3. IOC EXECUTION</text>
    <text x="15" y="55" font-family="{FONT_TITLE}" font-size="10.5" fill="#cbd5e1">• Immediate-or-Cancel</text>
    <text x="15" y="75" font-family="{FONT_TITLE}" font-size="10.5" fill="#cbd5e1">• Strict 2-Pip Slippage</text>
    <text x="15" y="95" font-family="{FONT_TITLE}" font-size="10.5" fill="#cbd5e1">• Sub-10ms Fill Window</text>
    <text x="15" y="125" font-family="{FONT_MONO}" font-size="9" fill="#f8fafc">Return code check: 10009 (TRADE_DONE)</text>
    <text x="15" y="155" font-family="{FONT_TITLE}" font-size="9" fill="#94a3b8">If requoted → Stage 4</text>
  </g>

  <!-- Arrow 3 -->
  <line x1="665" y1="210" x2="705" y2="210" stroke="#00f2fe" stroke-width="2" stroke-dasharray="4 4"/>
  <polygon points="705,210 697,205 697,215" fill="#00f2fe"/>

  <!-- Step 4 -->
  <g transform="translate(710, 100)">
    <rect width="170" height="220" rx="10" fill="url(#step-bg)" stroke="#a855f7" stroke-width="1.2"/>
    <rect width="170" height="30" rx="10" fill="#7e22ce" fill-opacity="0.2"/>
    <text x="85" y="20" font-family="{FONT_TITLE}" font-size="11" font-weight="700" fill="#c084fc" text-anchor="middle">4. RETRY LADDER</text>
    <text x="15" y="55" font-family="{FONT_TITLE}" font-size="10.5" fill="#cbd5e1">• Attempt FOK Fill</text>
    <text x="15" y="75" font-family="{FONT_TITLE}" font-size="10.5" fill="#cbd5e1">• Slippage +1 Pip Step</text>
    <text x="15" y="95" font-family="{FONT_TITLE}" font-size="10.5" fill="#cbd5e1">• Backoff: 50ms Exponential</text>
    <text x="15" y="115" font-family="{FONT_TITLE}" font-size="10.5" fill="#cbd5e1">• Max 3 Attempts Allowed</text>
    <text x="15" y="145" font-family="{FONT_MONO}" font-size="9" fill="#cbd5e1">Prevents toxic fills in flash moves</text>
  </g>

  <!-- Arrow 4 -->
  <line x1="885" y1="210" x2="925" y2="210" stroke="#00f2fe" stroke-width="2" stroke-dasharray="4 4"/>
  <polygon points="925,210 917,205 917,215" fill="#00f2fe"/>

  <!-- Step 5 -->
  <g transform="translate(930, 100)">
    <rect width="140" height="220" rx="10" fill="url(#step-bg)" stroke="#10b981" stroke-width="1.2"/>
    <rect width="140" height="30" rx="10" fill="#059669" fill-opacity="0.2"/>
    <text x="70" y="20" font-family="{FONT_TITLE}" font-size="11" font-weight="700" fill="#34d399" text-anchor="middle">5. BE &amp; RISK</text>
    <text x="12" y="55" font-family="{FONT_TITLE}" font-size="10.5" fill="#cbd5e1">• BE Lock at 1.5R</text>
    <text x="12" y="75" font-family="{FONT_TITLE}" font-size="10.5" fill="#cbd5e1">• WebSocket Stream</text>
    <text x="12" y="95" font-family="{FONT_TITLE}" font-size="10.5" fill="#cbd5e1">• PnL Attribution</text>
    <text x="12" y="115" font-family="{FONT_TITLE}" font-size="10.5" fill="#cbd5e1">• Telemetry Broadcast</text>
    <text x="12" y="145" font-family="{FONT_MONO}" font-size="8.5" fill="#10b981">Zero-Loss Protection Active</text>
  </g>
</svg>'''

files = {
    "assets/hero_banner.svg": hero_svg,
    "assets/system_architecture.svg": arch_svg,
    "assets/mobile_sentinel_mockup.svg": mockup_svg,
    "assets/execution_flow.svg": flow_svg
}

for path, content in files.items():
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    # Strict validation of XML well-formedness
    try:
        ET.parse(path)
        print(f"SUCCESS: {path} is 100% valid XML and verified.")
    except Exception as e:
        print(f"FAILED XML PARSE on {path}: {e}")
        raise e
