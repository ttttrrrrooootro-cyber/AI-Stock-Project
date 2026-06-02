"""
DGV Investment Analyzer — Mathematical Deep Analysis
วิเคราะห์การลงทุนด้วยคณิตศาสตร์ย้อนหลัง 10 ปี
ราคา Real-time จาก Finnhub | ข้อมูลย้อนหลังจาก yfinance | AI โดย Claude (Anthropic)
"""

import time
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import yfinance as yf
import finnhub
import anthropic

# ─────────────────────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DGV · Investment Analyzer",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────
#  GLOBAL CSS  —  Dark "Terminal" theme
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
  --bg:        #070a11;
  --bg-2:      #0b0f1a;
  --surface:   #111726;
  --surface-2: #18203250;
  --border:    rgba(255,255,255,0.07);
  --glow-gold: rgba(230,195,92,0.18);
  --ink:       #e9eef7;
  --muted:     #79859a;
  --gold:      #e6c35c;
  --gold-dim:  #c8a84b;
  --green:     #2ee6a0;
  --cyan:      #34e3c4;
  --red:       #ff5d6c;
  --blue:      #5b8def;
}

/* App background — radial glow */
html, body, [class*="css"], .stApp {
  font-family: 'Space Grotesk','DM Sans', sans-serif !important;
  color: var(--ink) !important;
}
.stApp {
  background:
    radial-gradient(1100px 500px at 18% -8%, rgba(230,195,92,0.07), transparent 60%),
    radial-gradient(900px 500px at 95% 8%, rgba(52,227,196,0.05), transparent 55%),
    var(--bg) !important;
}
.block-container { padding-top: 1rem; }

/* Headings + numbers */
.dm-serif { font-family:'DM Serif Display',serif; }
.mono { font-family:'JetBrains Mono',monospace; }

/* ── Masthead ───────────────────────────────────────── */
.dgv-masthead {
  position: relative;
  background: linear-gradient(135deg, #0c1120 0%, #131b2e 60%, #0c1120 100%);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 22px 30px 20px;
  margin: -8px 0 26px;
  display: flex;
  align-items: center;
  gap: 18px;
  overflow: hidden;
  box-shadow: 0 8px 40px rgba(0,0,0,0.45), inset 0 1px 0 rgba(255,255,255,0.04);
}
.dgv-masthead::after {
  content:''; position:absolute; left:0; right:0; bottom:0; height:2px;
  background: linear-gradient(90deg, transparent, var(--gold), var(--cyan), transparent);
  opacity:.8;
}
.dgv-wordmark {
  font-family:'DM Serif Display',serif;
  font-size: 40px; line-height:1; letter-spacing:-2px;
  background: linear-gradient(120deg, var(--gold) 0%, #fff4cf 50%, var(--gold-dim) 100%);
  -webkit-background-clip:text; background-clip:text; color:transparent;
  filter: drop-shadow(0 2px 14px var(--glow-gold));
}
.dgv-tagline {
  font-family:'JetBrains Mono',monospace;
  font-size: 11px; color: var(--gold); letter-spacing: 4px; text-transform: uppercase;
}
.dgv-sub { font-size: 12px; color: var(--muted); margin-top: 4px; }

/* ── Real-time badge / dot ──────────────────────────── */
.rt-badge {
  display:inline-flex; align-items:center; gap:6px;
  background: rgba(46,230,160,0.10);
  border: 1px solid rgba(46,230,160,0.35);
  border-radius: 20px; padding: 3px 11px;
  font-size: 11px; color: var(--green);
  font-family:'JetBrains Mono',monospace; font-weight:600;
}
.rt-dot { width:7px; height:7px; background: var(--green); border-radius:50%;
  box-shadow:0 0 10px var(--green); animation: pulse 1.5s infinite; }
@keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.35;transform:scale(.7)} }

/* ── Finnhub price panel (glass) ────────────────────── */
.rt-panel {
  background: linear-gradient(160deg, rgba(255,255,255,0.04), rgba(255,255,255,0.01));
  backdrop-filter: blur(14px);
  border: 1px solid var(--border);
  border-radius: 14px; padding: 16px 20px; margin-bottom: 18px;
  display: grid; grid-template-columns: repeat(auto-fit, minmax(112px,1fr)); gap: 14px;
  box-shadow: 0 6px 30px rgba(0,0,0,0.35);
}
.rt-item-label { font-size:10px; letter-spacing:1.5px; text-transform:uppercase;
  color: var(--muted); margin-bottom:4px; font-family:'JetBrains Mono',monospace; }
.rt-item-val { font-family:'JetBrains Mono',monospace; font-size:17px; font-weight:600; color:#fff; }
.rt-item-val.pos { color: var(--green); text-shadow:0 0 12px rgba(46,230,160,.4); }
.rt-item-val.neg { color: var(--red);   text-shadow:0 0 12px rgba(255,93,108,.35); }
.rt-item-val.gold{ color: var(--gold);  text-shadow:0 0 14px var(--glow-gold); }

/* ── Section headers ────────────────────────────────── */
.section-title {
  font-family:'DM Serif Display',serif; font-size: 21px; color: var(--ink);
  margin-bottom: 14px; display:flex; align-items:center; gap:10px;
}
.section-title::before {
  content:''; width:4px; height:20px; border-radius:3px;
  background: linear-gradient(var(--gold), var(--cyan));
}

/* ── Metric cards (glass + glow rail) ───────────────── */
.mcard {
  background: linear-gradient(160deg, rgba(255,255,255,0.045), rgba(255,255,255,0.012));
  border: 1px solid var(--border); border-radius: 12px;
  padding: 13px 15px; position: relative; overflow:hidden;
  transition: transform .18s ease, box-shadow .18s ease;
}
.mcard:hover { transform: translateY(-2px); box-shadow:0 10px 26px rgba(0,0,0,.4); }
.mcard::before { content:''; position:absolute; top:0; left:0; bottom:0; width:3px;
  background: var(--gold); box-shadow: 0 0 14px var(--glow-gold); }
.mcard-label { font-size:10px; letter-spacing:1.5px; text-transform:uppercase;
  color: var(--muted); margin-bottom:5px; }
.mcard-value { font-family:'JetBrains Mono',monospace; font-size:21px; font-weight:600; color: var(--ink); }
.mcard-sub { font-size:11px; color: var(--muted); margin-top:3px; }
.mcard.pos .mcard-value { color: var(--green); }
.mcard.neg .mcard-value { color: var(--red); }
.mcard.gold .mcard-value{ color: var(--gold); }
.mcard.pos::before  { background: var(--green); box-shadow:0 0 14px rgba(46,230,160,.5); }
.mcard.neg::before  { background: var(--red);   box-shadow:0 0 14px rgba(255,93,108,.45); }
.mcard.blue::before { background: var(--blue); }

/* ── Score ring / verdict ───────────────────────────── */
.score-ring {
  display:flex; align-items:center; gap:26px;
  background: linear-gradient(135deg, #0d1322, #15203a);
  border: 1px solid var(--border); border-radius: 16px;
  padding: 20px 26px; margin-bottom: 18px; position:relative; overflow:hidden;
  box-shadow: inset 0 1px 0 rgba(255,255,255,.05);
}
.score-ring::after { content:''; position:absolute; right:-40px; top:-40px;
  width:180px; height:180px; border-radius:50%;
  background: radial-gradient(var(--glow-gold), transparent 70%); }
.score-num { font-family:'DM Serif Display',serif; font-size:58px; line-height:1;
  background: linear-gradient(120deg,var(--gold),#fff4cf,var(--gold-dim));
  -webkit-background-clip:text; background-clip:text; color:transparent;
  filter: drop-shadow(0 0 18px var(--glow-gold)); }
.score-label { font-size:11px; color: var(--muted); letter-spacing:2px; text-transform:uppercase; }
.score-verdict { font-size:19px; font-weight:700; color:#fff; margin-top:4px; }

/* ── Signal rows ────────────────────────────────────── */
.sig-row { display:flex; align-items:center; gap:11px; padding:8px 0;
  border-bottom:1px solid var(--border); font-size:13px; }
.sig-icon { font-size:16px; width:22px; text-align:center; }
.sig-text { flex:1; color: var(--ink); }
.sig-badge { font-family:'JetBrains Mono',monospace; font-size:11px; padding:2px 8px;
  border-radius:6px; background: rgba(255,255,255,0.05); color: var(--muted);
  border:1px solid var(--border); }

/* ── Chat ───────────────────────────────────────────── */
.chat-wrap { max-height:360px; overflow-y:auto; padding:12px;
  border:1px solid var(--border); border-radius:14px;
  background: linear-gradient(160deg, rgba(255,255,255,0.03), rgba(255,255,255,0.008));
  margin-bottom:8px; }
.msg-row { display:flex; gap:8px; margin-bottom:11px; align-items:flex-start; }
.msg-row.u { flex-direction: row-reverse; }
.av { width:28px; height:28px; border-radius:9px; display:flex; align-items:center;
  justify-content:center; font-size:11px; font-weight:700; flex-shrink:0; margin-top:2px; }
.av.ai { background: linear-gradient(135deg,#1a2236,#0e1320); color: var(--gold);
  font-family:'DM Serif Display',serif; border:1px solid var(--border);
  box-shadow:0 0 12px var(--glow-gold); }
.av.usr { background: linear-gradient(135deg, var(--blue), #3a63b8); color:#fff; }
.bub { max-width:82%; padding:10px 14px; border-radius:14px; font-size:13px; line-height:1.65; }
.bub.ai-b { background: rgba(255,255,255,0.05); color: var(--ink);
  border:1px solid var(--border); border-bottom-left-radius:4px; }
.bub.u-b  { background: linear-gradient(135deg,#1d2940,#16203a); color:#fff;
  border:1px solid var(--border); border-bottom-right-radius:4px; }

/* ── Calc result ────────────────────────────────────── */
.calc-result { background: linear-gradient(135deg,#0d1322,#15203a);
  border:1px solid var(--border); color:#fff; border-radius:14px; padding:16px 20px; }
.calc-row { display:flex; justify-content:space-between; padding:6px 0;
  border-bottom:1px solid var(--border); font-size:13px; }
.calc-row:last-child { border-bottom:none; }
.calc-row span:last-child { font-family:'JetBrains Mono',monospace; color: var(--gold); font-weight:600; }

/* ── Progress bar ───────────────────────────────────── */
.pb-bg { background: rgba(255,255,255,0.07); border-radius:6px; height:10px; width:100%; overflow:hidden; }
.pb-fill { height:10px; border-radius:6px; transition: width .6s ease; box-shadow:0 0 12px currentColor; }

/* ── Rank table ─────────────────────────────────────── */
.rank-table { width:100%; border-collapse: collapse; font-size:13px;
  background: rgba(255,255,255,0.02); border-radius:12px; overflow:hidden; }
.rank-table th { background: rgba(255,255,255,0.04); color: var(--gold); padding:11px 12px;
  text-align:left; font-family:'JetBrains Mono',monospace; font-weight:600;
  font-size:11px; letter-spacing:1px; border-bottom:1px solid var(--border); }
.rank-table td { padding:11px 12px; border-bottom:1px solid var(--border); vertical-align:middle; color:var(--ink); }
.rank-table tr:hover td { background: rgba(255,255,255,0.04); }
.rank-num { font-family:'DM Serif Display',serif; font-size:21px; color: var(--gold); }
.rank-ticker { font-family:'JetBrains Mono',monospace; font-weight:600; font-size:14px; color:var(--ink); }

/* ── Streamlit widgets (dark) ───────────────────────── */
.stTextInput input, .stNumberInput input {
  background: rgba(255,255,255,0.04) !important; color: var(--ink) !important;
  border:1px solid var(--border) !important; border-radius:10px !important; }
.stTextInput input:focus, .stNumberInput input:focus {
  border-color: var(--gold) !important; box-shadow:0 0 0 2px var(--glow-gold) !important; }
[data-testid="stMetricValue"] { font-family:'JetBrains Mono',monospace; color: var(--ink); }
[data-testid="stMetricLabel"] { color: var(--muted); }
.stCaption, .stMarkdown small { color: var(--muted) !important; }
.stChatInput textarea { background: rgba(255,255,255,0.04) !important; color: var(--ink) !important; }

/* ── Tabs ───────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] { gap:6px; border-bottom:1px solid var(--border); }
.stTabs [data-baseweb="tab"] {
  font-family:'Space Grotesk',sans-serif !important; font-size:13px !important; font-weight:600 !important;
  padding:9px 18px !important; border-radius:10px 10px 0 0 !important; color: var(--muted) !important; }
.stTabs [aria-selected="true"] {
  background: linear-gradient(160deg, rgba(230,195,92,0.14), rgba(255,255,255,0.02)) !important;
  color: var(--gold) !important; border-bottom:2px solid var(--gold) !important; }

/* alerts */
.stAlert { background: rgba(255,255,255,0.04) !important; border:1px solid var(--border) !important;
  border-radius:12px !important; color: var(--ink) !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
#  MASTHEAD
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="dgv-masthead">
  <div class="dgv-wordmark">DGV</div>
  <div>
    <div class="dgv-tagline">Mathematical Investment Analyzer</div>
    <div class="dgv-sub">
      วิเคราะห์การลงทุนด้วยคณิตศาสตร์ · ย้อนหลัง 10 ปี · ราคา Real-time จาก Finnhub · AI โดย Claude
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
#  CLIENTS  (Finnhub + Claude)
# ─────────────────────────────────────────────────────────────
@st.cache_resource
def get_finnhub_client():
    api_key = st.secrets.get("FINNHUB_API_KEY", "")
    return finnhub.Client(api_key=api_key)

@st.cache_resource
def get_claude_client():
    api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
    return anthropic.Anthropic(api_key=api_key)

finnhub_client = get_finnhub_client()

# โมเดล Claude — เปลี่ยนได้ตามต้องการ (เช่น claude-opus-4-6 / claude-haiku-4-5-20251001)
CLAUDE_MODEL = "claude-sonnet-4-6"

# ─────────────────────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────────────────────
for k, v in [
    ("history", {}),
    ("chat", [{"role": "assistant", "content":
               "สวัสดีครับ! 📊 ผมคือ Claude ที่วิเคราะห์จากคณิตศาสตร์ล้วน ๆ\nถามได้เลย: Sharpe, Drawdown, ผลตอบแทน, ความเสี่ยง, ขนาด Position..."}]),
    ("last_refresh", 0),
]:
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────────────────────
#  WATCHLIST
# ─────────────────────────────────────────────────────────────
WATCHLIST = {
    "GC=F":    "ทองคำ (Gold Futures)",
    "BTC-USD": "Bitcoin",
    "NVDA":    "NVIDIA",
    "AAPL":    "Apple",
    "MSFT":    "Microsoft",
    "TSLA":    "Tesla",
    "AMZN":    "Amazon",
    "META":    "Meta Platforms",
    "GOOGL":   "Alphabet (Google)",
    "^GSPC":   "S&P 500 Index",
}

FINNHUB_SYMBOL_MAP = {
    "GC=F":    None,
    "BTC-USD": "BINANCE:BTCUSDT",
    "^GSPC":   None,
    "EURUSD=X": "OANDA:EUR_USD",
    "GBPUSD=X": "OANDA:GBP_USD",
    "USDJPY=X": "OANDA:USD_JPY",
}

def get_finnhub_symbol(yf_symbol: str) -> str | None:
    if yf_symbol in FINNHUB_SYMBOL_MAP:
        return FINNHUB_SYMBOL_MAP[yf_symbol]
    if "=" not in yf_symbol and "-" not in yf_symbol and "^" not in yf_symbol:
        return yf_symbol
    return None

# ─────────────────────────────────────────────────────────────
#  REAL-TIME QUOTE (Finnhub)
# ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=15)
def fetch_realtime_quote(yf_symbol: str) -> dict | None:
    fh_sym = get_finnhub_symbol(yf_symbol)
    if fh_sym is None:
        return None
    try:
        q = finnhub_client.quote(fh_sym)
        if not q or q.get("c", 0) == 0:
            return None
        q["d"]  = q["c"] - q["pc"]
        q["dp"] = (q["d"] / q["pc"] * 100) if q["pc"] else 0
        q["symbol"] = fh_sym
        return q
    except Exception:
        return None

# ─────────────────────────────────────────────────────────────
#  MATH FUNCTIONS
# ─────────────────────────────────────────────────────────────
def calc_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / (loss + 1e-9)
    return 100 - (100 / (1 + rs))

def calc_macd(series, fast=12, slow=26, signal=9):
    ema_f = series.ewm(span=fast).mean()
    ema_s = series.ewm(span=slow).mean()
    macd  = ema_f - ema_s
    sig   = macd.ewm(span=signal).mean()
    hist  = macd - sig
    return macd, sig, hist

def calc_bollinger(series, window=20, std=2):
    ma    = series.rolling(window).mean()
    std_v = series.rolling(window).std()
    return ma, ma + std*std_v, ma - std*std_v

def sharpe_ratio(returns, rf=0.05):
    rf_daily = rf / 252
    excess = returns - rf_daily
    if excess.std() == 0:
        return 0.0
    return round((excess.mean() / excess.std()) * np.sqrt(252), 3)

def sortino_ratio(returns, rf=0.05):
    rf_daily = rf / 252
    excess = returns - rf_daily
    downside = returns[returns < 0].std()
    if downside == 0:
        return 0.0
    return round((excess.mean() / downside) * np.sqrt(252), 3)

def max_drawdown(prices):
    roll_max = prices.cummax()
    drawdown = (prices - roll_max) / (roll_max + 1e-9)
    return round(drawdown.min() * 100, 2)

def calmar_ratio(returns, prices):
    cagr_v = ((prices.iloc[-1] / prices.iloc[0]) ** (252 / len(prices)) - 1) * 100
    mdd  = abs(max_drawdown(prices))
    if mdd == 0:
        return 0.0
    return round(cagr_v / mdd, 3)

def cagr(prices):
    years = len(prices) / 252
    if years == 0 or prices.iloc[0] == 0:
        return 0.0
    return round(((prices.iloc[-1] / prices.iloc[0]) ** (1 / years) - 1) * 100, 2)

def zscore(series, window=60):
    roll_mean = series.rolling(window).mean()
    roll_std  = series.rolling(window).std()
    return (series - roll_mean) / (roll_std + 1e-9)

def linear_trend(prices):
    x = np.arange(len(prices), dtype=float)
    y = prices.values.astype(float)
    coeffs = np.polyfit(x, y, 1)
    slope  = coeffs[0]
    y_hat  = np.polyval(coeffs, x)
    ss_res = np.sum((y - y_hat) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    r2     = 1 - ss_res / (ss_tot + 1e-9)
    n      = len(x)
    se     = np.sqrt(ss_res / max(n - 2, 1) / (np.sum((x - x.mean())**2) + 1e-9))
    t_stat = slope / (se + 1e-9)
    p_val  = 2 * (1 - _norm_cdf(abs(t_stat)))
    annual_slope = slope * 252 / (prices.mean() + 1e-9) * 100
    return round(annual_slope, 2), round(r2, 3), round(float(p_val), 4)

def _norm_cdf(x):
    t = 1 / (1 + 0.2316419 * abs(x))
    poly = t * (0.319381530 + t * (-0.356563782 + t * (1.781477937
           + t * (-1.821255978 + t * 1.330274429))))
    cdf = 1 - (1 / np.sqrt(2 * np.pi)) * np.exp(-0.5 * x**2) * poly
    return cdf if x >= 0 else 1 - cdf

def momentum_score(prices):
    weights = {22: 0.4, 66: 0.3, 126: 0.2, 252: 0.1}
    score = 0.0
    cur = prices.iloc[-1]
    for d, w in weights.items():
        if len(prices) > d:
            ret = (cur / prices.iloc[-d] - 1) * 100
            score += w * ret
    return round(score, 2)

def volatility_regime(returns, window=30):
    vol_s = returns.tail(window).std() * np.sqrt(252) * 100
    vol_l = returns.std() * np.sqrt(252) * 100
    ratio = vol_s / (vol_l + 1e-9)
    return round(vol_s, 2), round(vol_l, 2), round(ratio, 2)

def value_at_risk(returns, confidence=0.95):
    return round(np.percentile(returns.dropna(), (1 - confidence) * 100) * 100, 3)

def expected_shortfall(returns, confidence=0.95):
    var = np.percentile(returns.dropna(), (1 - confidence) * 100)
    es  = returns[returns <= var].mean()
    return round(es * 100, 3)

def winrate_backtest(df, strategy="ma_cross"):
    d = df.copy()
    d["MA20"] = d["Close"].rolling(20).mean()
    d["MA50"] = d["Close"].rolling(50).mean()
    d["RSI"]  = calc_rsi(d["Close"], 14)
    wins = losses = 0
    entries = []
    for i in range(50, len(d) - 10):
        cross_up = (d["MA20"].iloc[i-1] <= d["MA50"].iloc[i-1]) and \
                   (d["MA20"].iloc[i]    >  d["MA50"].iloc[i])
        rsi_ok   = 35 < d["RSI"].iloc[i] < 65
        if cross_up and rsi_ok:
            entry = d["Close"].iloc[i]
            fwd   = d["Close"].iloc[i+1:i+11]
            max_r = (fwd.max() - entry) / entry * 100
            min_r = (fwd.min() - entry) / entry * 100
            if max_r >= 1.5:
                wins += 1
                entries.append((d.index[i], entry, "win"))
            elif min_r <= -1.5:
                losses += 1
                entries.append((d.index[i], entry, "lose"))
    total = wins + losses
    wr = round(wins / total * 100, 1) if total else 0
    return {"wins": wins, "losses": losses, "total": total, "winrate": wr, "entries": entries}

def full_math_analysis(df, symbol):
    d = df.copy()
    prices  = d["Close"].dropna()
    returns = prices.pct_change().dropna()

    sh  = sharpe_ratio(returns)
    so  = sortino_ratio(returns)
    mdd = max_drawdown(prices)
    cal = calmar_ratio(returns, prices)
    ag  = cagr(prices)
    mom = momentum_score(prices)
    vol_s, vol_l, vol_r = volatility_regime(returns)
    vr  = value_at_risk(returns)
    es  = expected_shortfall(returns)
    trend_slope, r2, pval = linear_trend(prices)

    d["MA20"]  = prices.rolling(20).mean()
    d["MA50"]  = prices.rolling(50).mean()
    d["MA200"] = prices.rolling(200).mean()
    d["MA20"]  = d["MA20"].reindex(d.index)
    d["MA50"]  = d["MA50"].reindex(d.index)
    d["MA200"] = d["MA200"].reindex(d.index)
    d["RSI"]           = calc_rsi(d["Close"], 14)
    d["MACD"], d["MACDsig"], d["MACDhist"] = calc_macd(d["Close"])
    d["BB_mid"], d["BB_up"], d["BB_dn"]    = calc_bollinger(d["Close"])
    d["ZScore"]        = zscore(d["Close"])

    cur    = prices.iloc[-1]
    ma20   = d["MA20"].iloc[-1]
    ma50   = d["MA50"].iloc[-1]
    ma200v = d["MA200"].iloc[-1] if not pd.isna(d["MA200"].iloc[-1]) else None
    rsi_v  = d["RSI"].iloc[-1]
    macd_v = d["MACD"].iloc[-1]
    sig_v  = d["MACDsig"].iloc[-1]
    z_v    = d["ZScore"].iloc[-1]
    bb_up  = d["BB_up"].iloc[-1]
    bb_dn  = d["BB_dn"].iloc[-1]

    ret_1m  = (cur / prices.iloc[-22]  - 1) * 100 if len(prices) >= 22  else 0
    ret_3m  = (cur / prices.iloc[-66]  - 1) * 100 if len(prices) >= 66  else 0
    ret_6m  = (cur / prices.iloc[-126] - 1) * 100 if len(prices) >= 126 else 0
    ret_1y  = (cur / prices.iloc[-252] - 1) * 100 if len(prices) >= 252 else 0
    ret_3y  = (cur / prices.iloc[-756] - 1) * 100 if len(prices) >= 756 else 0

    score = 0
    signals = []

    if sh >= 1.5:
        score += 20
        signals.append(("✅", f"Sharpe Ratio {sh:.2f}", "ดีเยี่ยม (≥1.5)", "pos"))
    elif sh >= 0.8:
        score += 12
        signals.append(("⚠️", f"Sharpe Ratio {sh:.2f}", "พอใช้ (0.8–1.5)", "neu"))
    else:
        signals.append(("❌", f"Sharpe Ratio {sh:.2f}", "ต่ำ (<0.8)", "neg"))

    if so >= 2.0:
        score += 15
        signals.append(("✅", f"Sortino Ratio {so:.2f}", "Downside risk ต่ำ", "pos"))
    elif so >= 1.0:
        score += 8
        signals.append(("⚠️", f"Sortino Ratio {so:.2f}", "ปานกลาง", "neu"))
    else:
        signals.append(("❌", f"Sortino Ratio {so:.2f}", "ความเสี่ยงขาลงสูง", "neg"))

    if mdd > -20:
        score += 15
        signals.append(("✅", f"Max Drawdown {mdd:.1f}%", "ทนทานต่อวิกฤต", "pos"))
    elif mdd > -40:
        score += 8
        signals.append(("⚠️", f"Max Drawdown {mdd:.1f}%", "ปานกลาง", "neu"))
    else:
        signals.append(("❌", f"Max Drawdown {mdd:.1f}%", "ความเสี่ยงสูงมาก", "neg"))

    if ag >= 15:
        score += 15
        signals.append(("✅", f"CAGR {ag:.1f}%/ปี", "ผลตอบแทนดีเยี่ยม", "pos"))
    elif ag >= 7:
        score += 8
        signals.append(("⚠️", f"CAGR {ag:.1f}%/ปี", "ดีกว่าพันธบัตร", "neu"))
    else:
        signals.append(("❌", f"CAGR {ag:.1f}%/ปี", "ต่ำกว่าเงินเฟ้อ", "neg"))

    if mom >= 10:
        score += 10
        signals.append(("✅", f"Momentum Score {mom:.1f}%", "แรงโมเมนตัมสูง", "pos"))
    elif mom >= 0:
        score += 5
        signals.append(("⚠️", f"Momentum Score {mom:.1f}%", "โมเมนตัมอ่อน", "neu"))
    else:
        signals.append(("❌", f"Momentum Score {mom:.1f}%", "โมเมนตัมติดลบ", "neg"))

    if ma200v and cur > ma200v and cur > ma50 > ma20:
        score += 15
        signals.append(("✅", "MA Alignment", "Bullish (Price>MA200>MA50>MA20)", "pos"))
    elif cur > ma50:
        score += 7
        signals.append(("⚠️", "MA Alignment", "Partial Bullish", "neu"))
    else:
        signals.append(("❌", "MA Alignment", "ราคาต่ำกว่า MA50", "neg"))

    if -1.5 < z_v < 1.5:
        score += 10
        signals.append(("✅", f"Z-Score {z_v:.2f}", "ราคาไม่ Extreme", "pos"))
    elif z_v >= 1.5:
        signals.append(("⚠️", f"Z-Score {z_v:.2f}", "Overbought ระวัง", "neg"))
    else:
        score += 5
        signals.append(("⚠️", f"Z-Score {z_v:.2f}", "Oversold โอกาสเข้า", "pos"))

    verdict = ("Strong Buy" if score >= 75 else
               "Buy" if score >= 60 else
               "Hold/Watch" if score >= 45 else
               "Underweight" if score >= 30 else "Avoid")

    return {
        "score": score, "verdict": verdict, "signals": signals,
        "sharpe": sh, "sortino": so, "mdd": mdd, "calmar": cal,
        "cagr": ag, "momentum": mom,
        "vol_s": vol_s, "vol_l": vol_l, "vol_r": vol_r,
        "var95": vr, "es95": es,
        "trend_slope": trend_slope, "r2": r2, "pval": pval,
        "cur": cur, "ma20": ma20, "ma50": ma50, "ma200": ma200v,
        "rsi": rsi_v, "macd": macd_v, "macd_sig": sig_v,
        "zscore": z_v, "bb_up": bb_up, "bb_dn": bb_dn,
        "ret_1m": ret_1m, "ret_3m": ret_3m, "ret_6m": ret_6m,
        "ret_1y": ret_1y, "ret_3y": ret_3y,
        "df": d,
    }

def score_color(score):
    if score >= 75: return "pos"
    if score >= 50: return "gold"
    return "neg"

# Plotly dark theme helper
def dark_layout(fig, height=580, title=None):
    fig.update_layout(
        height=height,
        title=title,
        xaxis_rangeslider_visible=False,
        margin=dict(l=10, r=10, t=40, b=10),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Space Grotesk", color="#c3cbd9", size=12),
        legend=dict(bgcolor="rgba(20,26,40,0.7)", bordercolor="rgba(255,255,255,0.1)",
                    borderwidth=1, font=dict(size=11, color="#c3cbd9")),
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.08)",
                     linecolor="rgba(255,255,255,0.12)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.08)",
                     linecolor="rgba(255,255,255,0.12)")
    return fig

# ─────────────────────────────────────────────────────────────
#  FETCH DATA (yfinance — historical)
# ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def fetch_data(symbol, period="10y"):
    try:
        t = yf.Ticker(symbol)
        d = t.history(period=period)
        return d if not d.empty else None
    except Exception:
        return None

@st.cache_data(ttl=60)
def fetch_watchlist_scores():
    results = []
    for sym, name in WATCHLIST.items():
        df = fetch_data(sym)
        if df is None or len(df) < 252:
            continue
        try:
            m = full_math_analysis(df, sym)
            bt = winrate_backtest(df)
            results.append({
                "sym": sym, "name": name,
                "score": m["score"], "verdict": m["verdict"],
                "cagr": m["cagr"], "sharpe": m["sharpe"],
                "mdd": m["mdd"], "winrate": bt["winrate"],
                "momentum": m["momentum"], "vol": m["vol_l"],
                "cur": m["cur"],
            })
        except Exception:
            continue
    return sorted(results, key=lambda x: x["score"], reverse=True)

# ─────────────────────────────────────────────────────────────
#  INPUT BAR
# ─────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns([2, 1, 1])
with c1:
    symbol = st.text_input(
        "🔍 กรอกสัญลักษณ์",
        "AAPL",
        placeholder="เช่น AAPL, BTC-USD, GC=F, EURUSD=X",
        label_visibility="collapsed",
    ).upper().replace("/", "").strip()

# ─────────────────────────────────────────────────────────────
#  FETCH: Historical (yfinance) + Real-time (Finnhub)
# ─────────────────────────────────────────────────────────────
data = fetch_data(symbol)
is_fx = "=X" in symbol or symbol in ["EURUSD=X","GBPUSD=X","USDJPY=X"]

if data is None or len(data) < 100:
    st.error("⚠️ ไม่พบข้อมูล หรือข้อมูลไม่เพียงพอ กรุณาลองใหม่")
    st.stop()

rt_quote = fetch_realtime_quote(symbol)

if rt_quote and rt_quote.get("c", 0) > 0:
    cur_price     = rt_quote["c"]
    prev_price    = rt_quote["pc"]
    price_chg     = rt_quote["d"]
    price_chg_pct = rt_quote["dp"]
    price_source  = "finnhub"
else:
    cur_price     = data["Close"].iloc[-1]
    prev_price    = data["Close"].iloc[-2]
    price_chg     = cur_price - prev_price
    price_chg_pct = price_chg / prev_price * 100
    price_source  = "yfinance"

fmt_p = lambda v: f"{v:,.4f}" if is_fx else f"${v:,.2f}"

with c2:
    delta_str = (f"{price_chg:+.4f} ({price_chg_pct:+.2f}%)" if is_fx
                 else f"${price_chg:+.2f} ({price_chg_pct:+.2f}%)")
    st.metric(f"{symbol}", fmt_p(cur_price), delta=delta_str)

with c3:
    data_years = len(data) / 252
    source_label = "🟢 Finnhub Real-time" if price_source == "finnhub" else "📊 yfinance (ล่าสุด)"
    st.caption(f"{source_label}\n📅 Historical {data_years:.1f} ปี | {len(data):,} วัน")

# ─────────────────────────────────────────────────────────────
#  REAL-TIME PANEL
# ─────────────────────────────────────────────────────────────
if rt_quote:
    chg_cls   = "pos" if price_chg >= 0 else "neg"
    chg_arrow = "▲" if price_chg >= 0 else "▼"
    st.markdown(f"""
    <div class="rt-panel">
      <div class="rt-item">
        <div class="rt-item-label">REAL-TIME</div>
        <div class="rt-item-val gold">{fmt_p(rt_quote['c'])}</div>
      </div>
      <div class="rt-item">
        <div class="rt-item-label">เปลี่ยนแปลง</div>
        <div class="rt-item-val {chg_cls}">{chg_arrow} {price_chg:+.2f} ({price_chg_pct:+.2f}%)</div>
      </div>
      <div class="rt-item">
        <div class="rt-item-label">HIGH วันนี้</div>
        <div class="rt-item-val">{fmt_p(rt_quote['h'])}</div>
      </div>
      <div class="rt-item">
        <div class="rt-item-label">LOW วันนี้</div>
        <div class="rt-item-val">{fmt_p(rt_quote['l'])}</div>
      </div>
      <div class="rt-item">
        <div class="rt-item-label">เปิด (OPEN)</div>
        <div class="rt-item-val">{fmt_p(rt_quote['o'])}</div>
      </div>
      <div class="rt-item">
        <div class="rt-item-label">ปิดก่อนหน้า</div>
        <div class="rt-item-val">{fmt_p(rt_quote['pc'])}</div>
      </div>
      <div class="rt-item">
        <div class="rt-item-label">แหล่งข้อมูล</div>
        <div class="rt-item-val" style="font-size:12px">
          <span class="rt-badge"><span class="rt-dot"></span>Finnhub LIVE</span>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
#  COMPUTE Math Analysis
# ─────────────────────────────────────────────────────────────
with st.spinner("กำลังวิเคราะห์คณิตศาสตร์..."):
    m   = full_math_analysis(data, symbol)
    bt  = winrate_backtest(data)

# ─────────────────────────────────────────────────────────────
#  TABS
# ─────────────────────────────────────────────────────────────
tab_overview, tab_chart, tab_rank, tab_income, tab_chat = st.tabs([
    "📐 ภาพรวมคณิตศาสตร์",
    "📈 กราฟวิเคราะห์",
    "🏆 อันดับสินทรัพย์",
    "💰 คำนวณรายได้",
    "🤖 AI Assistant",
])

# ══════════════════════════════════════════════════════════════
#  TAB 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════
with tab_overview:
    col_left, col_right = st.columns([3, 2])

    with col_left:
        sc = m["score"]
        verdict_emoji = {"Strong Buy":"🚀","Buy":"📈","Hold/Watch":"⏳","Underweight":"⚠️","Avoid":"🚫"}
        st.markdown(f"""
        <div class="score-ring">
          <div>
            <div class="score-label">COMPOSITE SCORE</div>
            <div class="score-num">{sc}</div>
            <div style="font-size:10px;color:#888">/ 100</div>
          </div>
          <div>
            <div class="score-label">คำแนะนำ</div>
            <div class="score-verdict">{verdict_emoji.get(m['verdict'],'')} {m['verdict']}</div>
            <div style="font-size:11px;color:#9aa6b8;margin-top:6px">Win Rate Backtest: {bt['winrate']}%
            ({bt['wins']}W/{bt['losses']}L)</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        wr = bt["winrate"]
        wr_col = "#2ee6a0" if wr>=60 else "#e6c35c" if wr>=45 else "#ff5d6c"
        st.markdown(f"""
        <div style="margin-bottom:8px">
          <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:4px">
            <span>Win Rate (MA Cross Strategy · ย้อนหลัง 10 ปี)</span>
            <span style="font-family:'JetBrains Mono',monospace;font-weight:600;color:{wr_col}">{wr}%</span>
          </div>
          <div class="pb-bg"><div class="pb-fill" style="width:{min(wr,100)}%;background:{wr_col};color:{wr_col}"></div></div>
          <div style="font-size:11px;color:var(--muted);margin-top:3px">{bt['total']} สัญญาณ | {bt['wins']} ชนะ | {bt['losses']} แพ้</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="section-title">📋 ผลการวิเคราะห์ตัวชี้วัด</div>', unsafe_allow_html=True)
        for icon, label, detail, _ in m["signals"]:
            st.markdown(f"""
            <div class="sig-row">
              <div class="sig-icon">{icon}</div>
              <div class="sig-text"><strong>{label}</strong></div>
              <div class="sig-badge">{detail}</div>
            </div>
            """, unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="section-title">📊 ตัวเลขสำคัญ</div>', unsafe_allow_html=True)

        def mcard(label, value, sub="", cls=""):
            st.markdown(f"""
            <div class="mcard {cls}" style="margin-bottom:10px">
              <div class="mcard-label">{label}</div>
              <div class="mcard-value">{value}</div>
              {'<div class="mcard-sub">'+sub+'</div>' if sub else ''}
            </div>""", unsafe_allow_html=True)

        if rt_quote:
            mcard("PRICE (REAL-TIME)",
                  fmt_p(rt_quote['c']),
                  f"H: {fmt_p(rt_quote['h'])} · L: {fmt_p(rt_quote['l'])}",
                  "pos" if price_chg >= 0 else "neg")

        mcard("CAGR (ต่อปี)", f"{m['cagr']:+.1f}%",
              f"ย้อนหลัง {len(data)/252:.0f} ปี",
              "pos" if m['cagr']>0 else "neg")
        mcard("SHARPE RATIO", f"{m['sharpe']:.2f}",
              "ผลตอบแทนต่อหน่วยความเสี่ยง",
              "pos" if m['sharpe']>=1 else "neg" if m['sharpe']<0 else "")
        mcard("SORTINO RATIO", f"{m['sortino']:.2f}",
              "ความเสี่ยงขาลงเท่านั้น",
              "pos" if m['sortino']>=1 else "neg" if m['sortino']<0 else "")
        mcard("MAX DRAWDOWN", f"{m['mdd']:.1f}%",
              "จุดต่ำสุดจาก Peak",
              "neg" if m['mdd']<-30 else "")
        mcard("CALMAR RATIO", f"{m['calmar']:.2f}",
              "CAGR / |MaxDD|",
              "pos" if m['calmar']>1 else "")
        mcard("VALUE AT RISK (95%)", f"{m['var95']:.2f}%",
              "ขาดทุนสูงสุด/วัน (95% CI)", "neg")
        mcard("VOLATILITY (30D)", f"{m['vol_s']:.1f}%",
              f"Long-term: {m['vol_l']:.1f}% · Ratio: {m['vol_r']:.2f}", "")
        mcard("LINEAR TREND", f"{m['trend_slope']:+.1f}%/ปี",
              f"R²={m['r2']:.2f} · p={m['pval']:.3f}",
              "pos" if m['trend_slope']>0 else "neg")
        mcard("MOMENTUM SCORE", f"{m['momentum']:+.1f}%",
              "Weighted 1M/3M/6M/12M",
              "pos" if m['momentum']>0 else "neg")
        mcard("Z-SCORE (60D)", f"{m['zscore']:+.2f}",
              ">+2: Overbought | <-2: Oversold",
              "neg" if abs(m['zscore'])>2 else "pos")

        st.markdown('<div class="section-title" style="margin-top:16px">📅 ผลตอบแทนย้อนหลัง</div>',
                    unsafe_allow_html=True)
        for label, val in [("1 เดือน", m["ret_1m"]), ("3 เดือน", m["ret_3m"]),
                            ("6 เดือน", m["ret_6m"]), ("1 ปี", m["ret_1y"]),
                            ("3 ปี",    m["ret_3y"])]:
            col = "#2ee6a0" if val>=0 else "#ff5d6c"
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;padding:5px 0;
                        border-bottom:1px solid var(--border);font-size:13px">
              <span>{label}</span>
              <span style="font-family:'JetBrains Mono',monospace;font-weight:600;color:{col}">{val:+.1f}%</span>
            </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  TAB 2 — CHART
# ══════════════════════════════════════════════════════════════
with tab_chart:
    col_ctrl, _ = st.columns([2, 3])
    with col_ctrl:
        tf = st.select_slider("ช่วงเวลา (ปี)",
                               options=[1, 2, 3, 5, 10],
                               value=10 if len(data)>=2500 else 5,
                               format_func=lambda x: f"{x} ปี")
    n = min(int(tf * 252), len(data))
    df_c = m["df"].tail(n).copy()

    chart_type = st.radio("ประเภทกราฟ", ["Candlestick","Line + BB","Z-Score","Drawdown Curve"],
                           horizontal=True)

    if chart_type == "Candlestick":
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                            row_heights=[0.55, 0.22, 0.23],
                            vertical_spacing=0.025,
                            subplot_titles=("Price · MA · Bollinger Bands",
                                            "RSI (14)", "MACD (12,26,9)"))
        fig.add_trace(go.Candlestick(
            x=df_c.index, open=df_c["Open"], high=df_c["High"],
            low=df_c["Low"], close=df_c["Close"], name="Price",
            increasing_line_color="#2ee6a0", decreasing_line_color="#ff5d6c"
        ), row=1, col=1)
        for col_ma, width, dash, name_ma in [
            ("MA20", 1.2, "dot", "MA20"),
            ("MA50", 1.5, "solid", "MA50"),
            ("MA200", 1.8, "dash", "MA200"),
        ]:
            if col_ma in df_c.columns and not df_c[col_ma].isna().all():
                colors = {"MA20":"#f3b34c","MA50":"#a877e6","MA200":"#ff5d6c"}
                fig.add_trace(go.Scatter(
                    x=df_c.index, y=df_c[col_ma], mode="lines",
                    name=name_ma, line=dict(color=colors[col_ma], width=width, dash=dash)
                ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df_c.index, y=df_c["BB_up"], name="BB Upper",
            line=dict(color="rgba(91,141,239,0.5)", width=1), fill=None, showlegend=False
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df_c.index, y=df_c["BB_dn"], name="BB Band",
            fill='tonexty', fillcolor='rgba(91,141,239,0.08)',
            line=dict(color="rgba(91,141,239,0.5)", width=1), showlegend=False
        ), row=1, col=1)

        if rt_quote:
            fig.add_hline(y=rt_quote["c"], row=1, col=1,
                          line_color="#e6c35c", line_dash="dot", line_width=1.5,
                          annotation_text=f"RT {fmt_p(rt_quote['c'])}",
                          annotation_font_color="#e6c35c",
                          annotation_position="right")

        fig.add_trace(go.Scatter(
            x=df_c.index, y=df_c["RSI"], mode="lines",
            name="RSI", line=dict(color="#a877e6", width=1.5)
        ), row=2, col=1)
        fig.add_hline(y=70, line_color="#ff5d6c", line_dash="dash", line_width=1, row=2, col=1)
        fig.add_hline(y=30, line_color="#2ee6a0", line_dash="dash", line_width=1, row=2, col=1)
        fig.add_hline(y=50, line_color="#7d8799", line_dash="dot", line_width=0.8, row=2, col=1)
        hist_c = ["#2ee6a0" if v >= 0 else "#ff5d6c" for v in df_c["MACDhist"]]
        fig.add_trace(go.Bar(
            x=df_c.index, y=df_c["MACDhist"], name="Histogram",
            marker_color=hist_c, opacity=0.65
        ), row=3, col=1)
        fig.add_trace(go.Scatter(
            x=df_c.index, y=df_c["MACD"], mode="lines",
            name="MACD", line=dict(color="#5b8def", width=1.4)
        ), row=3, col=1)
        fig.add_trace(go.Scatter(
            x=df_c.index, y=df_c["MACDsig"], mode="lines",
            name="Signal", line=dict(color="#e6c35c", width=1.4)
        ), row=3, col=1)
        dark_layout(fig, height=600)

    elif chart_type == "Line + BB":
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                            row_heights=[0.7, 0.3], vertical_spacing=0.03,
                            subplot_titles=("Price + Bollinger Bands", "Z-Score (60D)"))
        fig.add_trace(go.Scatter(
            x=df_c.index, y=df_c["Close"], mode="lines",
            name="ราคา", line=dict(color="#5b8def", width=2)
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df_c.index, y=df_c["BB_up"], name="BB+2σ",
            line=dict(color="#e6c35c", width=1, dash="dash"), fill=None
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df_c.index, y=df_c["BB_dn"], name="BB-2σ",
            fill='tonexty', fillcolor='rgba(230,195,92,0.08)',
            line=dict(color="#e6c35c", width=1, dash="dash")
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df_c.index, y=df_c["BB_mid"], name="BB Mid",
            line=dict(color="#7d8799", width=1, dash="dot")
        ), row=1, col=1)
        if rt_quote:
            fig.add_hline(y=rt_quote["c"], row=1, col=1,
                          line_color="#e6c35c", line_dash="dot", line_width=1.5,
                          annotation_text=f"Live {fmt_p(rt_quote['c'])}",
                          annotation_font_color="#e6c35c")
        zs = df_c["ZScore"]
        z_col = ["#2ee6a0" if v < -1 else "#ff5d6c" if v > 1 else "#7d8799" for v in zs]
        fig.add_trace(go.Bar(x=df_c.index, y=zs, name="Z-Score",
                             marker_color=z_col, opacity=0.7), row=2, col=1)
        fig.add_hline(y=2,  line_color="#ff5d6c", line_dash="dash", row=2, col=1)
        fig.add_hline(y=-2, line_color="#2ee6a0", line_dash="dash", row=2, col=1)
        fig.add_hline(y=0,  line_color="#7d8799", row=2, col=1)
        dark_layout(fig, height=600)

    elif chart_type == "Z-Score":
        fig = go.Figure()
        zs = df_c["ZScore"]
        z_col = ["#2ee6a0" if v < -1.5 else "#ff5d6c" if v > 1.5 else "#5b8def" for v in zs]
        fig.add_trace(go.Bar(x=df_c.index, y=zs, name="Z-Score 60D",
                             marker_color=z_col, opacity=0.8))
        fig.add_hline(y=2,  line_color="#ff5d6c", line_dash="dash", annotation_text="Overbought +2σ")
        fig.add_hline(y=-2, line_color="#2ee6a0", line_dash="dash", annotation_text="Oversold -2σ")
        fig.add_hline(y=0,  line_color="#7d8799", line_width=0.8)
        dark_layout(fig, height=600, title="Z-Score (60-Day Rolling) — ระบุโซน Extreme")

    else:  # Drawdown
        prices_c = df_c["Close"]
        roll_max  = prices_c.cummax()
        dd        = (prices_c - roll_max) / (roll_max + 1e-9) * 100
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_c.index, y=dd, mode="lines", name="Drawdown",
            fill="tozeroy", fillcolor="rgba(255,93,108,0.15)",
            line=dict(color="#ff5d6c", width=1.5)
        ))
        fig.add_hline(y=-20, line_color="#e6c35c", line_dash="dash", annotation_text="-20% Threshold")
        fig.add_hline(y=-40, line_color="#ff5d6c", line_dash="dash", annotation_text="-40% Severe")
        dark_layout(fig, height=600, title="Drawdown Curve — ความเสียหายจาก Peak")

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    if bt["entries"]:
        st.markdown(f"**🔬 Backtest Entries** — {bt['total']} สัญญาณ | {bt['wins']}✅ {bt['losses']}❌")
        fig_bt = go.Figure()
        prices_full = m["df"]["Close"]
        fig_bt.add_trace(go.Scatter(
            x=prices_full.index, y=prices_full,
            mode="lines", name="ราคา", line=dict(color="#5b8def", width=1.5)
        ))
        w_d = [(e[0], e[1]) for e in bt["entries"] if e[2]=="win"  and e[0] in prices_full.index]
        l_d = [(e[0], e[1]) for e in bt["entries"] if e[2]=="lose" and e[0] in prices_full.index]
        if w_d:
            fig_bt.add_trace(go.Scatter(
                x=[x[0] for x in w_d], y=[x[1] for x in w_d], mode="markers",
                name="Win Entry", marker=dict(symbol="triangle-up", size=9, color="#2ee6a0")
            ))
        if l_d:
            fig_bt.add_trace(go.Scatter(
                x=[x[0] for x in l_d], y=[x[1] for x in l_d], mode="markers",
                name="Lose Entry", marker=dict(symbol="triangle-down", size=9, color="#ff5d6c")
            ))
        dark_layout(fig_bt, height=280)
        st.plotly_chart(fig_bt, use_container_width=True, config={"displayModeBar": False})

# ══════════════════════════════════════════════════════════════
#  TAB 3 — RANKING
# ══════════════════════════════════════════════════════════════
with tab_rank:
    st.markdown('<div class="section-title">🏆 อันดับสินทรัพย์ (Composite Score · คณิตศาสตร์ล้วน)</div>',
                unsafe_allow_html=True)
    st.caption("คำนวณจาก Sharpe, CAGR, Drawdown, Momentum, MA Alignment, Z-Score — ไม่มีปัจจัยข่าว")

    with st.spinner("กำลังดึงและวิเคราะห์ทุกสินทรัพย์..."):
        rankings = fetch_watchlist_scores()

    if not rankings:
        st.warning("ไม่สามารถดึงข้อมูลได้")
    else:
        medals = ["🥇","🥈","🥉"] + [""] * 20
        verdict_icon = {"Strong Buy":"🚀","Buy":"📈","Hold/Watch":"⏳","Underweight":"⚠️","Avoid":"🚫"}
        score_bg = lambda s: "rgba(46,230,160,0.18)" if s>=75 else "rgba(230,195,92,0.18)" if s>=50 else "rgba(255,93,108,0.18)"

        html_rows = ""
        for i, r in enumerate(rankings):
            sc_bg  = score_bg(r["score"])
            v_icon = verdict_icon.get(r["verdict"], "")
            cagr_c = "#2ee6a0" if r["cagr"]>=0 else "#ff5d6c"
            mom_c  = "#2ee6a0" if r["momentum"]>=0 else "#ff5d6c"
            reasons = []
            if r["sharpe"] >= 1.5:  reasons.append(f"Sharpe สูง ({r['sharpe']:.1f})")
            elif r["sharpe"] < 0.5: reasons.append(f"Sharpe ต่ำ ({r['sharpe']:.1f})")
            if r["cagr"] >= 15:     reasons.append(f"CAGR ดีเยี่ยม ({r['cagr']:.0f}%)")
            elif r["cagr"] < 5:     reasons.append(f"CAGR ต่ำ ({r['cagr']:.0f}%)")
            if r["mdd"] > -20:      reasons.append("Drawdown ต่ำ")
            elif r["mdd"] < -50:    reasons.append(f"MDD สูงมาก ({r['mdd']:.0f}%)")
            if r["momentum"] >= 15: reasons.append("Momentum แรง")
            elif r["momentum"] < -10: reasons.append("Momentum ติดลบ")
            if r["winrate"] >= 60:  reasons.append(f"Win Rate {r['winrate']:.0f}%")
            reason_str = " · ".join(reasons[:3]) if reasons else "ตัวชี้วัดปานกลาง"

            html_rows += f"""
            <tr>
              <td><span class="rank-num">{medals[i] or str(i+1)}</span></td>
              <td>
                <div class="rank-ticker">{r['sym']}</div>
                <div style="font-size:11px;color:var(--muted)">{r['name']}</div>
              </td>
              <td style="text-align:center">
                <span style="background:{sc_bg};padding:3px 11px;border-radius:20px;
                             font-family:'JetBrains Mono',monospace;font-weight:600;font-size:13px;color:#fff">
                  {r['score']}
                </span>
              </td>
              <td style="font-family:'JetBrains Mono',monospace;color:{cagr_c}">{r['cagr']:+.1f}%</td>
              <td style="font-family:'JetBrains Mono',monospace">{r['sharpe']:.2f}</td>
              <td style="font-family:'JetBrains Mono',monospace;color:#ff5d6c">{r['mdd']:.1f}%</td>
              <td style="font-family:'JetBrains Mono',monospace;color:{mom_c}">{r['momentum']:+.1f}%</td>
              <td style="font-family:'JetBrains Mono',monospace">{r['winrate']:.0f}%</td>
              <td>{v_icon} {r['verdict']}</td>
              <td style="font-size:11px;color:var(--muted);max-width:200px">{reason_str}</td>
            </tr>"""

        st.markdown(f"""
        <table class="rank-table">
          <thead><tr>
            <th>#</th><th>สินทรัพย์</th><th>SCORE</th>
            <th>CAGR</th><th>SHARPE</th><th>MAX DD</th>
            <th>MOMENTUM</th><th>WIN RATE</th><th>สัญญาณ</th><th>เหตุผล</th>
          </tr></thead>
          <tbody>{html_rows}</tbody>
        </table>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.info("📌 หมายเหตุ: อันดับนี้ใช้ข้อมูลราคาย้อนหลัง 10 ปีเท่านั้น ไม่รวมปัจจัยพื้นฐานหรือข่าว")

# ══════════════════════════════════════════════════════════════
#  TAB 4 — INCOME CALCULATOR
# ══════════════════════════════════════════════════════════════
with tab_income:
    st.markdown('<div class="section-title">💰 เครื่องคำนวณรายได้การลงทุน</div>', unsafe_allow_html=True)

    col_calc1, col_calc2 = st.columns(2)

    with col_calc1:
        st.markdown("#### 📊 คำนวณผลตอบแทนตามสถานการณ์")
        capital     = st.number_input("เงินลงทุนเริ่มต้น (฿ หรือ $)", min_value=1000,
                                       max_value=100_000_000, value=100_000, step=10_000)
        monthly_add = st.number_input("เงินเพิ่มต่อเดือน", min_value=0,
                                       max_value=1_000_000, value=5_000, step=1_000)
        years_inv   = st.slider("ระยะเวลาลงทุน (ปี)", 1, 30, 10)
        use_cagr    = st.checkbox(f"ใช้ CAGR จริงของ {symbol} ({m['cagr']:.1f}%/ปี)", value=True)
        rate_input  = m["cagr"] if use_cagr else st.slider(
            "อัตราผลตอบแทนต่อปี (%)", -20.0, 50.0, 10.0, step=0.5)

        rate_annual  = rate_input / 100
        rate_monthly = (1 + rate_annual) ** (1/12) - 1

        total = capital
        values = [total]
        contributions = [0]
        for mo in range(1, years_inv * 12 + 1):
            total = total * (1 + rate_monthly) + monthly_add
            values.append(total)
            contributions.append(capital + monthly_add * mo)

        final_val      = values[-1]
        total_contrib  = capital + monthly_add * years_inv * 12
        total_gain     = final_val - total_contrib
        total_return_pct = (final_val / total_contrib - 1) * 100
        ann_income     = final_val * (rate_annual if rate_annual > 0 else 0.05)

        scenarios = {}
        for label, r in [("แย่ (CAGR-5%)", rate_input-5),
                         ("ฐาน (CAGR)", rate_input),
                         ("ดี (CAGR+5%)", rate_input+5)]:
            rm = (1 + r/100) ** (1/12) - 1
            v  = capital
            for _ in range(years_inv * 12):
                v = v * (1 + rm) + monthly_add
            scenarios[label] = v

        st.markdown(f"""
        <div class="calc-result">
          <div style="font-size:11px;letter-spacing:2px;text-transform:uppercase;
                      color:#9aa6b8;margin-bottom:10px">ผลการคำนวณ · {years_inv} ปี</div>
          <div class="calc-row"><span>มูลค่าสุดท้าย</span><span>{final_val:,.0f}</span></div>
          <div class="calc-row"><span>เงินลงทุนรวม</span><span>{total_contrib:,.0f}</span></div>
          <div class="calc-row"><span>กำไรสะสม</span><span>{total_gain:,.0f}</span></div>
          <div class="calc-row"><span>ผลตอบแทนรวม</span><span>{total_return_pct:+.1f}%</span></div>
          <div class="calc-row"><span>รายได้ต่อปี</span><span>{ann_income:,.0f}</span></div>
          <div class="calc-row"><span>รายได้ต่อเดือน</span><span>{ann_income/12:,.0f}</span></div>
          <div style="margin-top:12px;padding-top:10px;border-top:1px solid rgba(255,255,255,0.12)">
            <div style="font-size:10px;color:#9aa6b8;margin-bottom:6px">SCENARIOS ({years_inv} ปี)</div>
        """, unsafe_allow_html=True)
        for label, sv in scenarios.items():
            col_s = "#2ee6a0" if sv > total_contrib else "#ff5d6c"
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;font-size:12px;padding:3px 0">
              <span style="color:#c3cbd9">{label}</span>
              <span style="font-family:'JetBrains Mono',monospace;color:{col_s}">{sv:,.0f}</span>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div></div>", unsafe_allow_html=True)

    with col_calc2:
        fig_grow = go.Figure()
        years_x = [i/12 for i in range(len(values))]
        fig_grow.add_trace(go.Scatter(
            x=years_x, y=contributions, mode="lines", name="เงินลงทุนสะสม",
            fill="tozeroy", fillcolor="rgba(230,195,92,0.10)",
            line=dict(color="#e6c35c", width=1.5, dash="dash")
        ))
        fig_grow.add_trace(go.Scatter(
            x=years_x, y=values, mode="lines", name="มูลค่าพอร์ต",
            fill="tonexty", fillcolor="rgba(46,230,160,0.12)",
            line=dict(color="#2ee6a0", width=2.5)
        ))
        dark_layout(fig_grow, height=320, title=f"การเติบโตของพอร์ต {years_inv} ปี")
        fig_grow.update_layout(xaxis_title="ปี", yaxis_title="มูลค่า")
        st.plotly_chart(fig_grow, use_container_width=True, config={"displayModeBar": False})

        st.markdown("#### ⚠️ คำนวณความเสี่ยง")
        invest_amt  = st.number_input("เงินลงทุน (สำหรับคำนวณ VaR)", min_value=1000,
                                       max_value=10_000_000, value=100_000, step=10_000)
        conf_level  = st.select_slider("Confidence Level", [90, 95, 99], value=95)
        returns_full = m["df"]["Close"].pct_change().dropna()
        var_pct  = np.percentile(returns_full, (1 - conf_level/100) * 100) * 100
        es_pct   = returns_full[returns_full <= var_pct/100].mean() * 100
        var_thb  = invest_amt * abs(var_pct) / 100
        es_thb   = invest_amt * abs(es_pct)  / 100

        st.markdown(f"""
        <div class="calc-result" style="margin-top:0">
          <div style="font-size:11px;letter-spacing:2px;text-transform:uppercase;
                      color:#9aa6b8;margin-bottom:10px">RISK METRICS · {conf_level}% Confidence</div>
          <div class="calc-row"><span>VaR/วัน ({conf_level}%)</span><span>{var_pct:.2f}%</span></div>
          <div class="calc-row"><span>VaR เงิน</span><span>{var_thb:,.0f}</span></div>
          <div class="calc-row"><span>Expected Shortfall</span><span>{es_pct:.2f}%</span></div>
          <div class="calc-row"><span>ES เงิน</span><span>{es_thb:,.0f}</span></div>
          <div class="calc-row"><span>Max Drawdown</span><span>{m['mdd']:.1f}%</span></div>
          <div class="calc-row"><span>Max Loss เงิน (DD)</span>
            <span>{invest_amt * abs(m['mdd'])/100:,.0f}</span></div>
          <div class="calc-row"><span>Kelly Criterion</span>
            <span>{max(0, (bt['winrate']/100 - (1-bt['winrate']/100))*100):.1f}% ของพอร์ต</span></div>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  TAB 5 — AI CHAT  (Claude)
# ══════════════════════════════════════════════════════════════
with tab_chat:
    col_ch, _ = st.columns([3, 2])
    with col_ch:
        st.markdown('<div class="section-title">🤖 AI Investment Assistant (Claude)</div>',
                    unsafe_allow_html=True)
        st.caption("วิเคราะห์จากตัวเลขคณิตศาสตร์ของ DGV · ขับเคลื่อนโดย Claude (Anthropic) · ไม่ใช้ข่าวสาร")

        rt_ctx = ""
        if rt_quote:
            rt_ctx = f"""
• ราคา Real-time (Finnhub): {fmt_p(rt_quote['c'])} (เปลี่ยน {price_chg:+.2f} / {price_chg_pct:+.2f}%)
• High วันนี้: {fmt_p(rt_quote['h'])} · Low: {fmt_p(rt_quote['l'])} · Open: {fmt_p(rt_quote['o'])}"""

        sys_ctx = f"""คุณคือ DGV Investment Analyst ผู้เชี่ยวชาญด้านคณิตศาสตร์การเงิน
วิเคราะห์เฉพาะข้อมูลเชิงปริมาณ ไม่ใช้ข่าว

ข้อมูลปัจจุบัน ({symbol}):{rt_ctx}
• CAGR: {m['cagr']:+.1f}%/ปี | Sharpe: {m['sharpe']:.2f} | Sortino: {m['sortino']:.2f} | Calmar: {m['calmar']:.2f}
• Max Drawdown: {m['mdd']:.1f}% | VaR 95%: {m['var95']:.2f}%/วัน
• Win Rate Backtest: {bt['winrate']}% ({bt['wins']}W/{bt['losses']}L)
• Momentum Score: {m['momentum']:+.1f}% | Z-Score: {m['zscore']:+.2f}
• RSI: {m['rsi']:.1f} | MACD: {'Bullish' if m['macd']>m['macd_sig'] else 'Bearish'}
• Linear Trend: {m['trend_slope']:+.1f}%/ปี | R²={m['r2']:.2f}
• Volatility: Short={m['vol_s']:.1f}% Long={m['vol_l']:.1f}%
• Composite Score: {m['score']}/100 → {m['verdict']}

ตอบภาษาไทย กระชับ ใช้ตัวเลขที่ให้ไว้ ระบุว่าเป็นการวิเคราะห์เพื่อประกอบการตัดสินใจ ไม่ใช่คำแนะนำการลงทุน"""

        chat_html = '<div class="chat-wrap">'
        for msg in st.session_state.chat:
            if msg["role"] == "assistant":
                chat_html += f'<div class="msg-row"><div class="av ai">C</div><div class="bub ai-b">{msg["content"].replace(chr(10),"<br>")}</div></div>'
            else:
                chat_html += f'<div class="msg-row u"><div class="av usr">คุณ</div><div class="bub u-b">{msg["content"].replace(chr(10),"<br>")}</div></div>'
        chat_html += '</div>'
        st.markdown(chat_html, unsafe_allow_html=True)

        if q := st.chat_input("ถามเรื่องตัวเลข, ความเสี่ยง, Sharpe, ผลตอบแทน...", key="main_chat"):
            st.session_state.chat.append({"role": "user", "content": q})
            try:
                client = get_claude_client()
                # ประวัติสนทนา: ข้าม greeting ตัวแรก และข้อความ q ที่เพิ่งเพิ่ม (จะต่อท้ายเอง)
                hist = [
                    {"role": m_["role"], "content": m_["content"]}
                    for m_ in st.session_state.chat[1:-1]
                ]
                resp = client.messages.create(
                    model=CLAUDE_MODEL,
                    max_tokens=1024,
                    system=sys_ctx,
                    messages=hist + [{"role": "user", "content": q}],
                )
                reply = "".join(
                    block.text for block in resp.content if block.type == "text"
                )
            except Exception as e:
                reply = f"ขออภัย: {e}"
            st.session_state.chat.append({"role": "assistant", "content": reply})
            st.rerun()

# ─────────────────────────────────────────────────────────────
#  AUTO REFRESH (30s)
# ─────────────────────────────────────────────────────────────
time.sleep(30)
st.rerun()
