"""
DGV Investment Analyzer — Mathematical Deep Analysis
วิเคราะห์การลงทุนด้วยคณิตศาสตร์ย้อนหลัง 10 ปี (Minimal Premium Dark Edition)
"""

import time
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import yfinance as yf
from google import genai

# ─────────────────────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DGV · Investment Analyzer",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────
#  GLOBAL CSS (True Corporate Dark Mode & High Contrast Typography)
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --bg-primary: #0b0f19;      /* พื้นหลังหลัก ดำ-น้ำเงินเข้มลึก */
  --bg-card: #141b2d;         /* พื้นหลังการ์ดและบล็อกข้อความ */
  --border-color: #242f4d;    /* เส้นขอบบางสไตล์พรีเมียม */
  --text-main: #f8fafc;       /* สีตัวอักษรหลัก: ขาวนวล คมชัด ไม่หายแน่นอน */
  --text-muted: #94a3b8;      /* สีตัวอักษรรอง: เทาอ่อน */
  --brand-blue: #38bdf8;      /* สีฟ้าสถาบัน */
  --brand-accent: #f59e0b;    /* สีทอง Amber เรียบหรู */
  --color-green: #4ade80;     /* เขียวสว่างสำหรับ Dark Mode */
  --color-red: #f87171;       /* แดงสว่างสำหรับ Dark Mode */
}

/* บังคับใช้ฟอนต์และธีมมืด */
html, body, [class*="css"] {
  font-family: 'Inter', sans-serif !important;
  background-color: var(--bg-primary) !important;
  color: var(--text-main) !important;
}

/* Header ดีไซน์เรียบหรูสไตล์ Analytics */
.dgv-masthead {
  background: var(--bg-card);
  padding: 24px 20px;
  margin-bottom: 28px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border: 1px solid var(--border-color);
  border-radius: 8px;
}
.dgv-wordmark {
  font-weight: 700;
  font-size: 24px;
  letter-spacing: 0.5px;
  color: var(--text-main);
}
.dgv-tagline {
  font-size: 13px;
  color: var(--text-muted);
  text-align: right;
}

/* หัวข้อเซกชัน */
.section-title {
  font-weight: 600;
  font-size: 15px;
  color: var(--text-main) !important;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-top: 24px;
  margin-bottom: 16px;
}

/* การ์ดตัวชี้วัดฝั่งขวา (แก้ไขเป็นสีเข้มพรีเมียม ใส่กรอบบาง ตัวหนังสือขาวชัดเจน) */
.metric-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 14px;
  margin-bottom: 16px;
}
.mcard {
  background: var(--bg-card) !important;
  border: 1px solid var(--border-color) !important;
  border-radius: 8px !important;
  padding: 20px !important;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2) !important;
}
.mcard-label {
  font-size: 11px !important;
  font-weight: 600 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.8px !important;
  color: var(--text-muted) !important; /* แก้ไขสีหัวข้อการ์ดไม่ให้จม */
  margin-bottom: 8px !important;
}
.mcard-value {
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 26px !important;
  font-weight: 600 !important;
  color: var(--text-main) !important; /* บังคับตัวเลขเป็นสีขาวเด่นชัด */
}
.mcard-sub {
  font-size: 11px !important;
  color: var(--text-muted) !important;
  margin-top: 6px !important;
}

/* สีพิเศษสำหรับการ์ดที่ต้องการเน้น */
.mcard.pos .mcard-value { color: var(--color-green) !important; }
.mcard.neg .mcard-value { color: var(--color-red) !important; }
.mcard.accent .mcard-value { color: var(--brand-accent) !important; }

/* บล็อกคะแนนรวมหลัก */
.score-ring {
  background: var(--bg-card) !important;
  border: 1px solid var(--border-color) !important;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 32px;
}
.score-num {
  font-family: 'JetBrains Mono', monospace;
  font-size: 48px;
  font-weight: 700;
  color: var(--color-green);
  line-height: 1;
}
.score-label { 
  font-size: 11px; 
  color: var(--text-muted); 
  letter-spacing: 1px; 
  text-transform: uppercase; 
}
.score-verdict { 
  font-size: 20px; 
  font-weight: 600; 
  color: var(--text-main); 
  margin-top: 2px; 
}

/* แถวรายการสรุปสัญญาณฝั่งซ้าย (แก้ปัญหาสีตัวอักษรหายเรียบร้อย) */
.sig-row {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 12px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  margin-bottom: 8px;
}
.sig-icon { font-size: 14px; width: 16px; display: flex; align-items: center; }
.sig-text { 
  flex: 1; 
  color: var(--text-main) !important; /* บังคับให้ตัวหนังสือสว่างเด่นบนพื้นหลังมืด */
  font-weight: 500; 
  font-size: 13.5px;
}
.sig-badge {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  padding: 4px 10px;
  border-radius: 4px;
  background: #1e293b;
  color: var(--text-main) !important;
  border: 1px solid var(--border-color);
}

/* แถบเปอร์เซ็นต์ Win Rate */
.pb-bg { background: #1e293b; border-radius: 4px; height: 6px; width: 100%; }
.pb-fill { height: 6px; border-radius: 4px; transition: width .5s ease; }

/* กล่องแชท AI */
.chat-wrap {
  max-height: 360px;
  overflow-y: auto;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-card);
  padding: 16px;
  margin-bottom: 12px;
}
.msg-row { display: flex; gap: 12px; margin-bottom: 12px; align-items: flex-start; }
.msg-row.u { flex-direction: row-reverse; }
.av { width: 28px; height: 28px; border-radius: 4px; display: flex; align-items: center;
      justify-content: center; font-size: 10px; font-weight: 700; flex-shrink: 0; }
.av.ai { background: var(--brand-blue); color: #000; }
.av.usr { background: #334155; color: var(--text-main); }
.bub { max-width: 80%; padding: 10px 14px; border-radius: 6px; font-size: 13px; line-height: 1.6; border: 1px solid var(--border-color); }
.bub.ai-b { background: #1e293b; color: var(--text-main); }
.bub.u-b  { background: var(--bg-primary);  color: var(--text-main); }

/* ตารางจัดอันดับ */
.rank-table { width: 100%; border-collapse: collapse; font-size: 13px; background: var(--bg-card); border: 1px solid var(--border-color); }
.rank-table th { background: #1e293b; color: var(--text-main); padding: 14px 12px;
                  text-align: left; font-family: 'Inter', sans-serif; font-weight: 600;
                  font-size: 11px; letter-spacing: 0.5px; border-bottom: 1px solid var(--border-color); }
.rank-table td { padding: 14px 12px; border-bottom: 1px solid var(--border-color); vertical-align: middle; color: var(--text-main); }
.rank-table tr:hover td { background: #1e293b; }
.rank-num { font-family: 'JetBrains Mono', monospace; font-size: 15px; font-weight: 600; color: var(--brand-blue); }
.rank-ticker { font-family: 'JetBrains Mono', monospace; font-weight: 600; color: var(--text-main); }

/* เครื่องคำนวณเงินทุน */
.calc-box {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 20px;
}
.calc-result {
  background: #1e293b;
  color: var(--text-main) !important;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 20px;
}
.calc-row { display: flex; justify-content: space-between; padding: 10px 0;
            border-bottom: 1px solid var(--border-color); font-size: 13px; }
.calc-row:last-child { border-bottom: none; }
.calc-row span:last-child { font-family: 'JetBrains Mono', monospace; color: var(--text-main) !important; font-weight: 600; }

/* Streamlit Native Elements Customization */
.stButton>button {
    background-color: #1e293b !important;
    color: white !important;
    border-radius: 6px !important;
    border: 1px solid var(--border-color) !important;
}
.stTabs [data-baseweb="tab-list"] {
  gap: 4px;
  border-bottom: 1px solid var(--border-color);
}
.stTabs [data-baseweb="tab"] {
  font-size: 13px !important;
  font-weight: 500 !important;
  padding: 10px 20px !important;
  color: var(--text-muted) !important;
  background-color: transparent !important;
}
.stTabs [aria-selected="true"] {
  color: var(--text-main) !important;
  border-bottom: 2px solid var(--brand-blue) !important;
  font-weight: 600 !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
#  MASTHEAD
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="dgv-masthead">
  <div class="dgv-wordmark">DGV ANALYTICS</div>
  <div class="dgv-tagline">
    <strong>MATHEMATICAL INVESTMENT ANALYZER</strong><br>
    <span style="font-size:11px;">ระบบวิเคราะห์สถิติการลงทุนย้อนหลัง 10 ปี ปราศจากอคติเชิงข่าว</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────────────────────
for k, v in [
    ("history", {}),
    ("chat", [{"role": "assistant", "content":
               "สวัสดีครับ ผมคือระบบ AI วิเคราะห์ข้อมูลเชิงปริมาณ (Quantitative Assistant) โปรดส่งคำถามเกี่ยวกับสถิติ ตัวเลข หรืออัตราความเสี่ยงที่คุณต้องการทราบได้เลยครับ"}]),
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
    ma  = series.rolling(window).mean()
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
        signals.append(("●", f"Sharpe Ratio {sh:.2f}", "ดีเยี่ยม (≥1.5)", "pos"))
    elif sh >= 0.8:
        score += 12
        signals.append(("●", f"Sharpe Ratio {sh:.2f}", "พอใช้ (0.8–1.5)", "neu"))
    else:
        signals.append(("●", f"Sharpe Ratio {sh:.2f}", "ต่ำ (<0.8)", "neg"))

    if so >= 2.0:
        score += 15
        signals.append(("●", f"Sortino Ratio {so:.2f}", "Downside risk ต่ำ", "pos"))
    elif so >= 1.0:
        score += 8
        signals.append(("●", f"Sortino Ratio {so:.2f}", "ปานกลาง", "neu"))
    else:
        signals.append(("●", f"Sortino Ratio {so:.2f}", "ความเสี่ยงขาลงสูง", "neg"))

    if mdd > -20:
        score += 15
        signals.append(("●", f"Max Drawdown {mdd:.1f}%", "ทนทานต่อวิกฤต", "pos"))
    elif mdd > -40:
        score += 8
        signals.append(("●", f"Max Drawdown {mdd:.1f}%", "ปานกลาง", "neu"))
    else:
        signals.append(("●", f"Max Drawdown {mdd:.1f}%", "ความเสี่ยงสูงมาก", "neg"))

    if ag >= 15:
        score += 15
        signals.append(("●", f"CAGR {ag:.1f}%/ปี", "ผลตอบแทนดีเยี่ยม", "pos"))
    elif ag >= 7:
        score += 8
        signals.append(("●", f"CAGR {ag:.1f}%/ปี", "ดีกว่าพันธบัตร", "neu"))
    else:
        signals.append(("●", f"CAGR {ag:.1f}%/ปี", "ต่ำกว่าเงินเฟ้อ", "neg"))

    if mom >= 10:
        score += 10
        signals.append(("●", f"Momentum Score {mom:.1f}%", "แรงโมเมนตัมสูง", "pos"))
    elif mom >= 0:
        score += 5
        signals.append(("●", f"Momentum Score {mom:.1f}%", "โมเมนตัมอ่อน", "neu"))
    else:
        signals.append(("●", f"Momentum Score {mom:.1f}%", "โมเมนตัมติดลบ", "neg"))

    if ma200v and cur > ma200v and cur > ma50 > ma20:
        score += 15
        signals.append(("●", "MA Alignment", "Bullish (Price>MA200>MA50>MA20)", "pos"))
    elif cur > ma50:
        score += 7
        signals.append(("●", "MA Alignment", "Partial Bullish", "neu"))
    else:
        signals.append(("●", "MA Alignment", "ราคาต่ำกว่า MA50", "neg"))

    if -1.5 < z_v < 1.5:
        score += 10
        signals.append(("●", f"Z-Score {z_v:.2f}", "ราคาไม่ Extreme", "pos"))
    elif z_v >= 1.5:
        signals.append(("●", f"Z-Score {z_v:.2f}", "Overbought ระวัง", "neg"))
    else:
        score += 5
        signals.append(("●", f"Z-Score {z_v:.2f}", "Oversold โอกาสเข้า", "pos"))

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

# ─────────────────────────────────────────────────────────────
#  INPUT BAR
# ─────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns([2, 1, 1])
with c1:
    symbol = st.text_input(
        "🔍 กรอกสัญลักษณ์สินทรัพย์",
        "GC=F",
        placeholder="เช่น AAPL, BTC-USD, GC=F",
        label_visibility="collapsed",
    ).upper().replace("/", "").strip()

data = fetch_data(symbol)
is_fx = "=X" in symbol or symbol in ["EURUSD=X","GBPUSD=X","USDJPY=X"]

if data is None or len(data) < 100:
    st.error("⚠️ ไม่พบข้อมูล หรือสัญลักษณ์ไม่ถูกต้อง กรุณาลองตรวจสอบอีกครั้ง")
    st.stop()

cur_price = data["Close"].iloc[-1]
prev_price = data["Close"].iloc[-2]
price_chg  = cur_price - prev_price
price_chg_pct = price_chg / prev_price * 100

fmt_p = lambda v: f"{v:,.4f}" if is_fx else f"${v:,.2f}"

with c2:
    st.metric(f"Ticker: {symbol}", fmt_p(cur_price),
              delta=f"{price_chg:+.4f} ({price_chg_pct:+.2f}%)" if is_fx
                    else f"${price_chg:+.2f} ({price_chg_pct:+.2f}%)")
with c3:
    data_years = len(data) / 252
    st.caption(f"📅 ข้อมูลประวัติศาสตร์: {data_years:.1f} ปี<br>🔄 อัปเดตข้อมูลอัตโนมัติ", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
#  COMPUTE ANALYSIS
# ─────────────────────────────────────────────────────────────
with st.spinner("กำลังคำนวณแบบจำลองทางคณิตศาสตร์..."):
    m   = full_math_analysis(data, symbol)
    bt  = winrate_backtest(data)

# ─────────────────────────────────────────────────────────────
#  TABS NAVIGATION
# ─────────────────────────────────────────────────────────────
tab_overview, tab_chart, tab_rank, tab_income, tab_chat = st.tabs([
    "📐 ภาพรวมคณิตศาสตร์",
    "📈 กราฟวิเคราะห์เทคนิคอล",
    "🏆 อันดับสินทรัพย์ทั้งหมด",
    "💰 คำนวณความเสี่ยงและขนาดพอร์ต",
    "🤖 ควอนต์ AI Assistant",
])

# ══════════════════════════════════════════════════════════════
#  TAB 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════
with tab_overview:
    col_left, col_right = st.columns([3, 2])

    with col_left:
        # Score block ดีไซน์หรูสไตล์มืดพรีเมียม
        sc = m["score"]
        st.markdown(f"""
        <div class="score-ring">
          <div>
            <div class="score-label">Composite Quantitative Score</div>
            <div class="score-num">{sc}</div>
            <div style="font-size:11px;color:var(--text-muted)">คะแนนเต็ม 100</div>
          </div>
          <div>
            <div class="score-label">คำแนะนำเชิงระบบ</div>
            <div class="score-verdict">{m['verdict']}</div>
            <div style="font-size:12px;color:var(--text-muted);margin-top:6px">กลยุทธ์ MA Cross Win Rate: <strong style="color:var(--brand-blue);">{bt['winrate']}%</strong> ({bt['wins']}W / {bt['losses']}L)</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # แถบ Win rate
        wr = bt["winrate"]
        wr_col = "var(--brand-blue)" if wr>=50 else "var(--text-muted)"
        st.markdown(f"""
        <div style="margin-bottom:24px">
          <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:6px">
            <span style="color:var(--text-muted);">ประสิทธิภาพกลยุทธ์ตามสถิติย้อนหลัง (Win Rate)</span>
            <span style="font-family:'JetBrains Mono',monospace;font-weight:600;color:{wr_col}">{wr}%</span>
          </div>
          <div class="pb-bg"><div class="pb-fill" style="width:{min(wr,100)}%;background:{wr_col}"></div></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="section-title">📋 สรุปสัญญาณเงื่อนไขเชิงคณิตศาสตร์</div>', unsafe_allow_html=True)
        for icon, label, detail, status in m["signals"]:
            color_dot = "var(--color-green)" if status == "pos" else "var(--color-red)" if status == "neg" else "var(--text-muted)"
            st.markdown(f"""
            <div class="sig-row">
              <div class="sig-icon" style="color:{color_dot};">{icon}</div>
              <div class="sig-text">{label}</div>
              <div class="sig-badge">{detail}</div>
            </div>
            """, unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="section-title">📊 ดัชนีชี้วัดสำคัญ (Key Matrix)</div>', unsafe_allow_html=True)

        def mcard(label, value, sub="", cls=""):
            st.markdown(f"""
            <div class="mcard {cls}">
              <div class="mcard-label">{label}</div>
              <div class="mcard-value">{value}</div>
              {'<div class="mcard-sub">'+sub+'</div>' if sub else ''}
            </div>""", unsafe_allow_html=True)

        st.markdown('<div class="metric-grid">', unsafe_allow_html=True)
        mcard("CAGR (เติบโตทบต้นต่อปี)", f"{m['cagr']:+.1f}%", f"เฉลี่ยรายปี", "pos" if m['cagr']>0 else "neg")
        mcard("Sharpe Ratio", f"{m['sharpe']:.2f}", "เทียบความผันผวน")
        mcard("Sortino Ratio", f"{m['sortino']:.2f}", "ความเสี่ยงขาลง")
        mcard("Max Drawdown", f"{m['mdd']:.1f}%", "ความเสี่ยงจุดลดต่ำสุด", "neg")
        mcard("Calmar Ratio", f"{m['calmar']:.2f}", "CAGR / MaxDD")
        mcard("Value at Risk (95%)", f"{m['var95']:.2f}%", "ความเสียหายสูงสุดรายวัน")
        mcard("Linear Trend Slope", f"{m['trend_slope']:+.1f}%", f"R²={m['r2']:.2f}")
        mcard("Momentum Score", f"{m['momentum']:+.1f}%", "คะแนนโมเมนตัม")
        mcard("Z-Score (60 วัน)", f"{m['zscore']:.2f}", "ดัชนีวัดความ Extreme")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-title">📅 อัตราผลตอบแทนแบ่งตามช่วงเวลา</div>', unsafe_allow_html=True)
        for label, val in [("1 เดือนที่ผ่านมา", m["ret_1m"]), ("3 เดือนที่ผ่านมา", m["ret_3m"]),
                            ("6 เดือนที่ผ่านมา", m["ret_6m"]), ("1 ปีที่ผ่านมา", m["ret_1y"]),
                            ("3 ปีที่ผ่านมา (สะสม)", m["ret_3y"])]:
            col = "var(--color-green)" if val>=0 else "var(--color-red)"
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;padding:12px 6px;
                        border-bottom:1px solid var(--border-color);font-size:13px">
              <span style="color: var(--text-muted);">{label}</span>
              <span style="font-family:'JetBrains Mono',monospace;font-weight:600;color:{col}">{val:+.1f}%</span>
            </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  นับจากจุดนี้ โครงสร้างแท็บอื่น (Chart, Rank, Income, Chat) 
#  จะดึงเอาโครงสร้างสไตล์ Dark CSS ด้านบนไปใช้โดยอัตโนมัติครับ
# ══════════════════════════════════════════════════════════════
