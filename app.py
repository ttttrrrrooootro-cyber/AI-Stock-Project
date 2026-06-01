"""
DGV Investment Analyzer — Mathematical Deep Analysis
วิเคราะห์การลงทุนด้วยคณิตศาสตร์ย้อนหลัง 10 ปี
"""

import time
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import yfinance as yf
from scipy import stats
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
#  GLOBAL CSS
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
  --ink: #0d0d0d;
  --paper: #f8f6f1;
  --cream: #ede9e0;
  --gold: #c8a84b;
  --gold-light: #f0d98a;
  --green: #2d7a4f;
  --red: #c0392b;
  --blue: #1a3a5c;
  --muted: #8a8478;
  --border: #d8d2c5;
  --card: #ffffff;
}

html, body, [class*="css"] {
  font-family: 'DM Sans', sans-serif !important;
  background-color: var(--paper) !important;
  color: var(--ink) !important;
}

/* Header */
.dgv-masthead {
  background: var(--ink);
  color: #fff;
  padding: 22px 32px 18px;
  margin: -16px -16px 24px;
  display: flex;
  align-items: baseline;
  gap: 16px;
  border-bottom: 3px solid var(--gold);
}
.dgv-wordmark {
  font-family: 'DM Serif Display', serif;
  font-size: 32px;
  letter-spacing: -1px;
  color: var(--gold);
}
.dgv-tagline {
  font-size: 12px;
  color: #aaa;
  letter-spacing: 3px;
  text-transform: uppercase;
}

/* Section headers */
.section-title {
  font-family: 'DM Serif Display', serif;
  font-size: 20px;
  color: var(--ink);
  border-bottom: 1.5px solid var(--border);
  padding-bottom: 6px;
  margin-bottom: 14px;
}

/* Metric cards */
.metric-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 10px;
  margin-bottom: 16px;
}
.mcard {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 12px 14px;
  position: relative;
}
.mcard::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
  background: var(--gold);
  border-radius: 8px 8px 0 0;
}
.mcard-label {
  font-size: 10px;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  color: var(--muted);
  margin-bottom: 4px;
}
.mcard-value {
  font-family: 'DM Mono', monospace;
  font-size: 20px;
  font-weight: 500;
  color: var(--ink);
}
.mcard-sub {
  font-size: 11px;
  color: var(--muted);
  margin-top: 2px;
}
.mcard.pos .mcard-value { color: var(--green); }
.mcard.neg .mcard-value { color: var(--red); }
.mcard.gold .mcard-value { color: var(--gold); }
.mcard.gold::before { background: var(--gold); }
.mcard.pos::before  { background: var(--green); }
.mcard.neg::before  { background: var(--red); }
.mcard.blue::before { background: var(--blue); }

/* Score dial */
.score-ring {
  display: flex;
  align-items: center;
  gap: 20px;
  background: var(--ink);
  border-radius: 10px;
  padding: 18px 22px;
  margin-bottom: 16px;
  color: #fff;
}
.score-num {
  font-family: 'DM Serif Display', serif;
  font-size: 52px;
  color: var(--gold);
  line-height: 1;
}
.score-label { font-size: 11px; color: #aaa; letter-spacing: 2px; text-transform: uppercase; }
.score-verdict { font-size: 18px; font-weight: 600; color: #fff; margin-top: 4px; }

/* Signal rows */
.sig-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 7px 0;
  border-bottom: 1px solid var(--cream);
  font-size: 13px;
}
.sig-icon { font-size: 16px; width: 22px; text-align: center; }
.sig-text { flex: 1; color: var(--ink); }
.sig-badge {
  font-family: 'DM Mono', monospace;
  font-size: 11px;
  padding: 2px 7px;
  border-radius: 4px;
  background: var(--cream);
  color: var(--muted);
}

/* Chat */
.chat-wrap {
  max-height: 340px;
  overflow-y: auto;
  padding: 4px 0;
  border: 1px solid var(--border);
  border-radius: 10px;
  background: var(--card);
  padding: 10px;
  margin-bottom: 8px;
}
.msg-row { display: flex; gap: 8px; margin-bottom: 10px; align-items: flex-start; }
.msg-row.u { flex-direction: row-reverse; }
.av { width: 26px; height: 26px; border-radius: 50%; display: flex; align-items: center;
      justify-content: center; font-size: 9px; font-weight: 700; flex-shrink: 0; margin-top: 2px; }
.av.ai { background: var(--ink); color: var(--gold); font-family: 'DM Serif Display', serif; font-size: 12px; }
.av.usr { background: var(--blue); color: #fff; }
.bub { max-width: 82%; padding: 9px 13px; border-radius: 14px; font-size: 13px; line-height: 1.6; }
.bub.ai-b { background: var(--cream); color: var(--ink); border-bottom-left-radius: 3px; }
.bub.u-b  { background: var(--ink);  color: #fff;       border-bottom-right-radius: 3px; }

/* Income calculator */
.calc-box {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 18px 20px;
}
.calc-result {
  background: var(--ink);
  color: #fff;
  border-radius: 8px;
  padding: 14px 18px;
  margin-top: 12px;
}
.calc-row { display: flex; justify-content: space-between; padding: 5px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1); font-size: 13px; }
.calc-row:last-child { border-bottom: none; }
.calc-row span:last-child { font-family: 'DM Mono', monospace; color: var(--gold-light); font-weight: 500; }

/* Progress bar */
.pb-bg { background: var(--cream); border-radius: 6px; height: 10px; width: 100%; }
.pb-fill { height: 10px; border-radius: 6px; transition: width .5s ease; }

/* Rank table */
.rank-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.rank-table th { background: var(--ink); color: var(--gold); padding: 9px 12px;
                  text-align: left; font-family: 'DM Mono', monospace; font-weight: 500;
                  font-size: 11px; letter-spacing: 1px; }
.rank-table td { padding: 9px 12px; border-bottom: 1px solid var(--border); vertical-align: middle; }
.rank-table tr:hover td { background: var(--cream); }
.rank-num { font-family: 'DM Serif Display', serif; font-size: 20px; color: var(--gold); }
.rank-ticker { font-family: 'DM Mono', monospace; font-weight: 500; font-size: 14px; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
  gap: 0;
  border-bottom: 2px solid var(--border);
}
.stTabs [data-baseweb="tab"] {
  font-family: 'DM Sans', sans-serif !important;
  font-size: 13px !important;
  font-weight: 500 !important;
  padding: 10px 20px !important;
  border-radius: 0 !important;
}
.stTabs [aria-selected="true"] {
  background: var(--ink) !important;
  color: var(--gold) !important;
}
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
    <div style="font-size:12px;color:#ccc;margin-top:3px">วิเคราะห์การลงทุนด้วยคณิตศาสตร์ · ย้อนหลัง 10 ปี · ไม่ผสมข่าว</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────────────────────
for k, v in [
    ("history", {}),
    ("chat", [{"role": "assistant", "content":
               "สวัสดีครับ! 📊 ผมวิเคราะห์จากคณิตศาสตร์ล้วน ๆ\nถามได้เลย: Sharpe, Drawdown, ผลตอบแทน, ความเสี่ยง, ขนาด Position..."}]),
    ("last_refresh", 0),
]:
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────────────────────
#  WATCHLIST (อันดับหุ้น default)
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
    """Annualized Sharpe (rf = 5% ต่อปี)"""
    rf_daily = rf / 252
    excess = returns - rf_daily
    if excess.std() == 0:
        return 0.0
    return round((excess.mean() / excess.std()) * np.sqrt(252), 3)

def sortino_ratio(returns, rf=0.05):
    """Sortino — ใช้เฉพาะ downside std"""
    rf_daily = rf / 252
    excess = returns - rf_daily
    downside = returns[returns < 0].std()
    if downside == 0:
        return 0.0
    return round((excess.mean() / downside) * np.sqrt(252), 3)

def max_drawdown(prices):
    """Max Drawdown เป็น %"""
    roll_max = prices.cummax()
    drawdown = (prices - roll_max) / (roll_max + 1e-9)
    return round(drawdown.min() * 100, 2)

def calmar_ratio(returns, prices):
    """Calmar = CAGR / |MaxDD|"""
    cagr = ((prices.iloc[-1] / prices.iloc[0]) ** (252 / len(prices)) - 1) * 100
    mdd  = abs(max_drawdown(prices))
    if mdd == 0:
        return 0.0
    return round(cagr / mdd, 3)

def cagr(prices):
    years = len(prices) / 252
    if years == 0 or prices.iloc[0] == 0:
        return 0.0
    return round(((prices.iloc[-1] / prices.iloc[0]) ** (1 / years) - 1) * 100, 2)

def zscore(series, window=60):
    """Z-score เพื่อระบุ overbought/oversold"""
    roll_mean = series.rolling(window).mean()
    roll_std  = series.rolling(window).std()
    return (series - roll_mean) / (roll_std + 1e-9)

def linear_trend(prices):
    """Linear regression slope (annualized %)"""
    x = np.arange(len(prices))
    slope, intercept, r_val, p_val, _ = stats.linregress(x, prices.values)
    annual_slope = slope * 252 / prices.mean() * 100
    return round(annual_slope, 2), round(r_val**2, 3), round(p_val, 4)

def momentum_score(prices):
    """Weighted momentum: 1M,3M,6M,12M"""
    weights = {22: 0.4, 66: 0.3, 126: 0.2, 252: 0.1}
    score = 0.0
    cur = prices.iloc[-1]
    for d, w in weights.items():
        if len(prices) > d:
            ret = (cur / prices.iloc[-d] - 1) * 100
            score += w * ret
    return round(score, 2)

def volatility_regime(returns, window=30):
    """Short vs Long vol เพื่อระบุ regime"""
    vol_s = returns.tail(window).std() * np.sqrt(252) * 100
    vol_l = returns.std() * np.sqrt(252) * 100
    ratio = vol_s / (vol_l + 1e-9)
    return round(vol_s, 2), round(vol_l, 2), round(ratio, 2)

def value_at_risk(returns, confidence=0.95):
    """Historical VaR"""
    return round(np.percentile(returns.dropna(), (1 - confidence) * 100) * 100, 3)

def expected_shortfall(returns, confidence=0.95):
    """CVaR/ES"""
    var = np.percentile(returns.dropna(), (1 - confidence) * 100)
    es  = returns[returns <= var].mean()
    return round(es * 100, 3)

def winrate_backtest(df, strategy="ma_cross"):
    """
    Backtest Win Rate:
    Signal: MA50 cross + RSI filter
    Win: +1.5% ใน 5 วัน | Lose: -1.5%
    """
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
    """คืน dict วิเคราะห์ทางคณิตศาสตร์ครบถ้วน"""
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

    # MA
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

    # Returns
    ret_1m  = (cur / prices.iloc[-22]  - 1) * 100 if len(prices) >= 22  else 0
    ret_3m  = (cur / prices.iloc[-66]  - 1) * 100 if len(prices) >= 66  else 0
    ret_6m  = (cur / prices.iloc[-126] - 1) * 100 if len(prices) >= 126 else 0
    ret_1y  = (cur / prices.iloc[-252] - 1) * 100 if len(prices) >= 252 else 0
    ret_3y  = (cur / prices.iloc[-756] - 1) * 100 if len(prices) >= 756 else 0

    # ── Composite Score (0-100) ─────────────────────────────
    score = 0
    signals = []

    # Sharpe
    if sh >= 1.5:
        score += 20
        signals.append(("✅", f"Sharpe Ratio {sh:.2f}", "ดีเยี่ยม (≥1.5)", "pos"))
    elif sh >= 0.8:
        score += 12
        signals.append(("⚠️", f"Sharpe Ratio {sh:.2f}", "พอใช้ (0.8–1.5)", "neu"))
    else:
        signals.append(("❌", f"Sharpe Ratio {sh:.2f}", "ต่ำ (<0.8)", "neg"))

    # Sortino
    if so >= 2.0:
        score += 15
        signals.append(("✅", f"Sortino Ratio {so:.2f}", "Downside risk ต่ำ", "pos"))
    elif so >= 1.0:
        score += 8
        signals.append(("⚠️", f"Sortino Ratio {so:.2f}", "ปานกลาง", "neu"))
    else:
        signals.append(("❌", f"Sortino Ratio {so:.2f}", "ความเสี่ยงขาลงสูง", "neg"))

    # MDD
    if mdd > -20:
        score += 15
        signals.append(("✅", f"Max Drawdown {mdd:.1f}%", "ทนทานต่อวิกฤต", "pos"))
    elif mdd > -40:
        score += 8
        signals.append(("⚠️", f"Max Drawdown {mdd:.1f}%", "ปานกลาง", "neu"))
    else:
        signals.append(("❌", f"Max Drawdown {mdd:.1f}%", "ความเสี่ยงสูงมาก", "neg"))

    # CAGR
    if ag >= 15:
        score += 15
        signals.append(("✅", f"CAGR {ag:.1f}%/ปี", "ผลตอบแทนดีเยี่ยม", "pos"))
    elif ag >= 7:
        score += 8
        signals.append(("⚠️", f"CAGR {ag:.1f}%/ปี", "ดีกว่าพันธบัตร", "neu"))
    else:
        signals.append(("❌", f"CAGR {ag:.1f}%/ปี", "ต่ำกว่าเงินเฟ้อ", "neg"))

    # Momentum
    if mom >= 10:
        score += 10
        signals.append(("✅", f"Momentum Score {mom:.1f}%", "แรงโมเมนตัมสูง", "pos"))
    elif mom >= 0:
        score += 5
        signals.append(("⚠️", f"Momentum Score {mom:.1f}%", "โมเมนตัมอ่อน", "neu"))
    else:
        signals.append(("❌", f"Momentum Score {mom:.1f}%", "โมเมนตัมติดลบ", "neg"))

    # MA alignment
    if ma200v and cur > ma200v and cur > ma50 > ma20:
        score += 15
        signals.append(("✅", "MA Alignment", "Bullish (Price>MA200>MA50>MA20)", "pos"))
    elif cur > ma50:
        score += 7
        signals.append(("⚠️", "MA Alignment", "Partial Bullish", "neu"))
    else:
        signals.append(("❌", "MA Alignment", "ราคาต่ำกว่า MA50", "neg"))

    # Z-score
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

# ─────────────────────────────────────────────────────────────
#  FETCH DATA
# ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=30)
def fetch_data(symbol, period="10y"):
    try:
        t = yf.Ticker(symbol)
        d = t.history(period=period)
        return d if not d.empty else None
    except:
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
        except:
            continue
    return sorted(results, key=lambda x: x["score"], reverse=True)

# ─────────────────────────────────────────────────────────────
#  INPUT BAR
# ─────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns([2, 1, 1])
with c1:
    symbol = st.text_input(
        "🔍 กรอกสัญลักษณ์",
        "GC=F",
        placeholder="เช่น AAPL, BTC-USD, GC=F, EURUSD=X",
        label_visibility="collapsed",
    ).upper().replace("/", "").strip()

data = fetch_data(symbol)
is_fx = "=X" in symbol or symbol in ["EURUSD=X","GBPUSD=X","USDJPY=X"]

if data is None or len(data) < 100:
    st.error("⚠️ ไม่พบข้อมูล หรือข้อมูลไม่เพียงพอ กรุณาลองใหม่")
    st.stop()

cur_price = data["Close"].iloc[-1]
prev_price = data["Close"].iloc[-2]
price_chg  = cur_price - prev_price
price_chg_pct = price_chg / prev_price * 100

fmt_p = lambda v: f"{v:,.4f}" if is_fx else f"${v:,.2f}"

# ── Price header
with c2:
    st.metric(f"{symbol}", fmt_p(cur_price),
              delta=f"{price_chg:+.4f} ({price_chg_pct:+.2f}%)" if is_fx
                    else f"${price_chg:+.2f} ({price_chg_pct:+.2f}%)")
with c3:
    data_years = len(data) / 252
    st.caption(f"📅 ข้อมูล {data_years:.1f} ปี | {len(data):,} วัน\n🔄 Refresh ทุก 30 วินาที")

# ─────────────────────────────────────────────────────────────
#  COMPUTE
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
        # Score ring
        sc = m["score"]
        cls = score_color(sc)
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
            <div style="font-size:11px;color:#aaa;margin-top:6px">Win Rate Backtest: {bt['winrate']}%
            ({bt['wins']}W/{bt['losses']}L)</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Win rate bar
        wr = bt["winrate"]
        wr_col = "#2d7a4f" if wr>=60 else "#c8a84b" if wr>=45 else "#c0392b"
        st.markdown(f"""
        <div style="margin-bottom:8px">
          <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:4px">
            <span>Win Rate (MA Cross Strategy · ย้อนหลัง 10 ปี)</span>
            <span style="font-family:'DM Mono',monospace;font-weight:600;color:{wr_col}">{wr}%</span>
          </div>
          <div class="pb-bg"><div class="pb-fill" style="width:{min(wr,100)}%;background:{wr_col}"></div></div>
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

        # Returns table
        st.markdown('<div class="section-title" style="margin-top:16px">📅 ผลตอบแทนย้อนหลัง</div>',
                    unsafe_allow_html=True)
        for label, val in [("1 เดือน", m["ret_1m"]), ("3 เดือน", m["ret_3m"]),
                            ("6 เดือน", m["ret_6m"]), ("1 ปี", m["ret_1y"]),
                            ("3 ปี",    m["ret_3y"])]:
            col = "#2d7a4f" if val>=0 else "#c0392b"
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;padding:5px 0;
                        border-bottom:1px solid var(--border);font-size:13px">
              <span>{label}</span>
              <span style="font-family:'DM Mono',monospace;font-weight:600;color:{col}">{val:+.1f}%</span>
            </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  TAB 2 — CHART (Realtime-style with 10Y data)
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
                                            "RSI (14) — Relative Strength Index",
                                            "MACD (12,26,9) — Momentum"))
        fig.add_trace(go.Candlestick(
            x=df_c.index, open=df_c["Open"], high=df_c["High"],
            low=df_c["Low"], close=df_c["Close"], name="Price",
            increasing_line_color="#2d7a4f", decreasing_line_color="#c0392b"
        ), row=1, col=1)
        for col_ma, width, dash, name_ma in [
            ("MA20", 1.2, "dot", "MA20"),
            ("MA50", 1.5, "solid", "MA50"),
            ("MA200", 1.8, "dash", "MA200"),
        ]:
            if col_ma in df_c.columns and not df_c[col_ma].isna().all():
                colors = {"MA20":"#f39c12","MA50":"#9b59b6","MA200":"#e74c3c"}
                fig.add_trace(go.Scatter(
                    x=df_c.index, y=df_c[col_ma], mode="lines",
                    name=name_ma, line=dict(color=colors[col_ma], width=width, dash=dash)
                ), row=1, col=1)
        # Bollinger
        fig.add_trace(go.Scatter(
            x=df_c.index, y=df_c["BB_up"], name="BB Upper",
            line=dict(color="rgba(30,90,150,0.4)", width=1),
            fill=None, showlegend=False
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df_c.index, y=df_c["BB_dn"], name="BB Band",
            fill='tonexty', fillcolor='rgba(30,90,150,0.07)',
            line=dict(color="rgba(30,90,150,0.4)", width=1), showlegend=False
        ), row=1, col=1)
        # RSI
        fig.add_trace(go.Scatter(
            x=df_c.index, y=df_c["RSI"], mode="lines",
            name="RSI", line=dict(color="#7b1fa2", width=1.5)
        ), row=2, col=1)
        fig.add_hline(y=70, line_color="#c0392b", line_dash="dash", line_width=1, row=2, col=1)
        fig.add_hline(y=30, line_color="#2d7a4f", line_dash="dash", line_width=1, row=2, col=1)
        fig.add_hline(y=50, line_color="#aaa", line_dash="dot", line_width=0.8, row=2, col=1)
        # MACD
        hist_c = ["#2d7a4f" if v >= 0 else "#c0392b" for v in df_c["MACDhist"]]
        fig.add_trace(go.Bar(
            x=df_c.index, y=df_c["MACDhist"], name="Histogram",
            marker_color=hist_c, opacity=0.65
        ), row=3, col=1)
        fig.add_trace(go.Scatter(
            x=df_c.index, y=df_c["MACD"], mode="lines",
            name="MACD", line=dict(color="#1a3a5c", width=1.4)
        ), row=3, col=1)
        fig.add_trace(go.Scatter(
            x=df_c.index, y=df_c["MACDsig"], mode="lines",
            name="Signal", line=dict(color="#c8a84b", width=1.4)
        ), row=3, col=1)

    elif chart_type == "Line + BB":
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                            row_heights=[0.7, 0.3], vertical_spacing=0.03,
                            subplot_titles=("Price + Bollinger Bands", "Z-Score (60D)"))
        fig.add_trace(go.Scatter(
            x=df_c.index, y=df_c["Close"], mode="lines",
            name="ราคา", line=dict(color="#1a3a5c", width=2)
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df_c.index, y=df_c["BB_up"], name="BB+2σ",
            line=dict(color="#c8a84b", width=1, dash="dash"), fill=None
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df_c.index, y=df_c["BB_dn"], name="BB-2σ",
            fill='tonexty', fillcolor='rgba(200,168,75,0.08)',
            line=dict(color="#c8a84b", width=1, dash="dash")
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df_c.index, y=df_c["BB_mid"], name="BB Mid",
            line=dict(color="#aaa", width=1, dash="dot")
        ), row=1, col=1)
        # Z-Score
        zs = df_c["ZScore"]
        z_col = ["#2d7a4f" if v < -1 else "#c0392b" if v > 1 else "#888" for v in zs]
        fig.add_trace(go.Bar(x=df_c.index, y=zs, name="Z-Score",
                             marker_color=z_col, opacity=0.7), row=2, col=1)
        fig.add_hline(y=2,  line_color="#c0392b", line_dash="dash", row=2, col=1)
        fig.add_hline(y=-2, line_color="#2d7a4f", line_dash="dash", row=2, col=1)
        fig.add_hline(y=0,  line_color="#aaa", row=2, col=1)

    elif chart_type == "Z-Score":
        fig = go.Figure()
        zs = df_c["ZScore"]
        z_col = ["#2d7a4f" if v < -1.5 else "#c0392b" if v > 1.5 else "#1a3a5c" for v in zs]
        fig.add_trace(go.Bar(x=df_c.index, y=zs, name="Z-Score 60D",
                             marker_color=z_col, opacity=0.8))
        fig.add_hline(y=2,   line_color="#c0392b", line_dash="dash",
                      annotation_text="Overbought +2σ")
        fig.add_hline(y=-2,  line_color="#2d7a4f", line_dash="dash",
                      annotation_text="Oversold -2σ")
        fig.add_hline(y=0,   line_color="#888", line_width=0.8)
        fig.update_layout(title="Z-Score (60-Day Rolling) — ระบุโซน Extreme")

    else:  # Drawdown
        prices_c = df_c["Close"]
        roll_max  = prices_c.cummax()
        dd        = (prices_c - roll_max) / (roll_max + 1e-9) * 100
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_c.index, y=dd, mode="lines", name="Drawdown",
            fill="tozeroy", fillcolor="rgba(192,57,43,0.15)",
            line=dict(color="#c0392b", width=1.5)
        ))
        fig.add_hline(y=-20, line_color="#c8a84b", line_dash="dash",
                      annotation_text="-20% Threshold")
        fig.add_hline(y=-40, line_color="#c0392b", line_dash="dash",
                      annotation_text="-40% Severe")
        fig.update_layout(title="Drawdown Curve — ความเสียหายจาก Peak")

    fig.update_layout(
        height=580,
        xaxis_rangeslider_visible=False,
        margin=dict(l=10, r=10, t=36, b=10),
        plot_bgcolor="#fff",
        paper_bgcolor="#f8f6f1",
        legend=dict(bgcolor="rgba(255,255,255,0.85)", bordercolor=var if (var:="#d8d2c5") else "#d8d2c5",
                    borderwidth=1, font=dict(size=11)),
        font=dict(family="DM Sans"),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # Backtest entry markers
    if bt["entries"]:
        st.markdown(f"**🔬 Backtest Entries** — {bt['total']} สัญญาณ | {bt['wins']}✅ {bt['losses']}❌")
        fig_bt = go.Figure()
        prices_full = m["df"]["Close"]
        fig_bt.add_trace(go.Scatter(
            x=prices_full.index, y=prices_full,
            mode="lines", name="ราคา", line=dict(color="#1a3a5c", width=1.5)
        ))
        w_d = [(e[0], e[1]) for e in bt["entries"] if e[2]=="win"  and e[0] in prices_full.index]
        l_d = [(e[0], e[1]) for e in bt["entries"] if e[2]=="lose" and e[0] in prices_full.index]
        if w_d:
            fig_bt.add_trace(go.Scatter(
                x=[x[0] for x in w_d], y=[x[1] for x in w_d], mode="markers",
                name="Win Entry", marker=dict(symbol="triangle-up", size=9, color="#2d7a4f")
            ))
        if l_d:
            fig_bt.add_trace(go.Scatter(
                x=[x[0] for x in l_d], y=[x[1] for x in l_d], mode="markers",
                name="Lose Entry", marker=dict(symbol="triangle-down", size=9, color="#c0392b")
            ))
        fig_bt.update_layout(height=280, margin=dict(l=10,r=10,t=20,b=10),
                              plot_bgcolor="#fff", paper_bgcolor="#f8f6f1",
                              xaxis_rangeslider_visible=False)
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
        score_bg = lambda s: "#d4edda" if s>=75 else "#fff3cd" if s>=50 else "#f8d7da"

        html_rows = ""
        for i, r in enumerate(rankings):
            sc_bg  = score_bg(r["score"])
            v_icon = verdict_icon.get(r["verdict"], "")
            cagr_c = "#2d7a4f" if r["cagr"]>=0 else "#c0392b"
            mom_c  = "#2d7a4f" if r["momentum"]>=0 else "#c0392b"

            # เหตุผล
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
                <span style="background:{sc_bg};padding:3px 10px;border-radius:20px;
                             font-family:'DM Mono',monospace;font-weight:600;font-size:13px">
                  {r['score']}
                </span>
              </td>
              <td style="font-family:'DM Mono',monospace;color:{cagr_c}">{r['cagr']:+.1f}%</td>
              <td style="font-family:'DM Mono',monospace">{r['sharpe']:.2f}</td>
              <td style="font-family:'DM Mono',monospace;color:#c0392b">{r['mdd']:.1f}%</td>
              <td style="font-family:'DM Mono',monospace;color:{mom_c}">{r['momentum']:+.1f}%</td>
              <td style="font-family:'DM Mono',monospace">{r['winrate']:.0f}%</td>
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
        if use_cagr:
            rate_input = m["cagr"]
        else:
            rate_input = st.slider("อัตราผลตอบแทนต่อปี (%)", -20.0, 50.0, 10.0, step=0.5)

        rate_annual = rate_input / 100
        rate_monthly = (1 + rate_annual) ** (1/12) - 1

        # Compound calculation
        total = capital
        values = [total]
        contributions = [0]
        interest_acc = [0]
        for mo in range(1, years_inv * 12 + 1):
            total = total * (1 + rate_monthly) + monthly_add
            values.append(total)
            contributions.append(capital + monthly_add * mo)
            interest_acc.append(total - (capital + monthly_add * mo))

        final_val = values[-1]
        total_contrib = capital + monthly_add * years_inv * 12
        total_gain = final_val - total_contrib
        total_return_pct = (final_val / total_contrib - 1) * 100
        ann_income = final_val * (rate_annual if rate_annual > 0 else 0.05)

        # Scenarios
        scenarios = {}
        for label, r in [("แย่ (CAGR-5%)", rate_input-5),
                         ("ฐาน (CAGR)", rate_input),
                         ("ดี (CAGR+5%)", rate_input+5)]:
            rm  = (1 + r/100) ** (1/12) - 1
            v   = capital
            for _ in range(years_inv * 12):
                v = v * (1 + rm) + monthly_add
            scenarios[label] = v

        st.markdown(f"""
        <div class="calc-result">
          <div style="font-size:11px;letter-spacing:2px;text-transform:uppercase;
                      color:#aaa;margin-bottom:10px">ผลการคำนวณ · {years_inv} ปี</div>
          <div class="calc-row"><span>มูลค่าสุดท้าย</span>
            <span>{final_val:,.0f}</span></div>
          <div class="calc-row"><span>เงินลงทุนรวม</span>
            <span>{total_contrib:,.0f}</span></div>
          <div class="calc-row"><span>กำไรสะสม</span>
            <span>{total_gain:,.0f}</span></div>
          <div class="calc-row"><span>ผลตอบแทนรวม</span>
            <span>{total_return_pct:+.1f}%</span></div>
          <div class="calc-row"><span>รายได้ต่อปี (ที่ CAGR)</span>
            <span>{ann_income:,.0f}</span></div>
          <div class="calc-row"><span>รายได้ต่อเดือน</span>
            <span>{ann_income/12:,.0f}</span></div>
          <div style="margin-top:12px;padding-top:10px;border-top:1px solid rgba(255,255,255,0.15)">
            <div style="font-size:10px;color:#aaa;margin-bottom:6px">SCENARIOS ({years_inv} ปี)</div>
        """, unsafe_allow_html=True)
        for label, sv in scenarios.items():
            col_s = "#2d7a4f" if sv > total_contrib else "#c0392b"
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;font-size:12px;padding:3px 0">
              <span style="color:#ccc">{label}</span>
              <span style="font-family:'DM Mono',monospace;color:{col_s}">{sv:,.0f}</span>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div></div>", unsafe_allow_html=True)

    with col_calc2:
        # Growth chart
        fig_grow = go.Figure()
        years_x = [i/12 for i in range(len(values))]
        fig_grow.add_trace(go.Scatter(
            x=years_x, y=contributions, mode="lines", name="เงินลงทุนสะสม",
            fill="tozeroy", fillcolor="rgba(200,168,75,0.1)",
            line=dict(color="#c8a84b", width=1.5, dash="dash")
        ))
        fig_grow.add_trace(go.Scatter(
            x=years_x, y=values, mode="lines", name="มูลค่าพอร์ต",
            fill="tonexty", fillcolor="rgba(45,122,79,0.12)",
            line=dict(color="#2d7a4f", width=2.5)
        ))
        fig_grow.update_layout(
            title=f"การเติบโตของพอร์ต {years_inv} ปี",
            height=320, margin=dict(l=10,r=10,t=36,b=10),
            plot_bgcolor="#fff", paper_bgcolor="#f8f6f1",
            xaxis_title="ปี", yaxis_title="มูลค่า",
            legend=dict(bgcolor="rgba(255,255,255,0.8)"),
        )
        st.plotly_chart(fig_grow, use_container_width=True, config={"displayModeBar": False})

        # VaR/Risk calculator
        st.markdown("#### ⚠️ คำนวณความเสี่ยง")
        invest_amt = st.number_input("เงินลงทุน (สำหรับคำนวณ VaR)", min_value=1000,
                                      max_value=10_000_000, value=100_000, step=10_000)
        conf_level = st.select_slider("Confidence Level", [90, 95, 99], value=95)
        returns_full = m["df"]["Close"].pct_change().dropna()
        var_pct  = np.percentile(returns_full, (1 - conf_level/100) * 100) * 100
        es_pct   = returns_full[returns_full <= var_pct/100].mean() * 100
        var_thb  = invest_amt * abs(var_pct) / 100
        es_thb   = invest_amt * abs(es_pct)  / 100

        st.markdown(f"""
        <div class="calc-result" style="margin-top:0">
          <div style="font-size:11px;letter-spacing:2px;text-transform:uppercase;
                      color:#aaa;margin-bottom:10px">RISK METRICS · {conf_level}% Confidence</div>
          <div class="calc-row"><span>VaR/วัน ({conf_level}%)</span>
            <span>{var_pct:.2f}%</span></div>
          <div class="calc-row"><span>VaR เงิน</span>
            <span>{var_thb:,.0f}</span></div>
          <div class="calc-row"><span>Expected Shortfall</span>
            <span>{es_pct:.2f}%</span></div>
          <div class="calc-row"><span>ES เงิน</span>
            <span>{es_thb:,.0f}</span></div>
          <div class="calc-row"><span>Max Drawdown</span>
            <span>{m['mdd']:.1f}%</span></div>
          <div class="calc-row"><span>Max Loss เงิน (DD)</span>
            <span>{invest_amt * abs(m['mdd'])/100:,.0f}</span></div>
          <div class="calc-row"><span>Kelly Criterion (แนะนำ)</span>
            <span>{max(0, (bt['winrate']/100 - (1-bt['winrate']/100))*100):.1f}% ของพอร์ต</span></div>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  TAB 5 — AI CHAT
# ══════════════════════════════════════════════════════════════
with tab_chat:
    col_ch, _ = st.columns([3, 2])
    with col_ch:
        st.markdown('<div class="section-title">🤖 AI Investment Assistant (Gemini)</div>',
                    unsafe_allow_html=True)
        st.caption("วิเคราะห์จากตัวเลขคณิตศาสตร์ของ DGV · ไม่ใช้ข่าวสาร")

        # System context
        sys_ctx = f"""คุณคือ DGV Investment Analyst ผู้เชี่ยวชาญด้านคณิตศาสตร์การเงิน
วิเคราะห์เฉพาะข้อมูลเชิงปริมาณ ไม่ใช้ข่าว

ข้อมูลปัจจุบัน ({symbol}):
• ราคา: {fmt_p(m['cur'])} | CAGR: {m['cagr']:+.1f}%/ปี
• Sharpe: {m['sharpe']:.2f} | Sortino: {m['sortino']:.2f} | Calmar: {m['calmar']:.2f}
• Max Drawdown: {m['mdd']:.1f}% | VaR 95%: {m['var95']:.2f}%/วัน
• Win Rate Backtest: {bt['winrate']}% ({bt['wins']}W/{bt['losses']}L)
• Momentum Score: {m['momentum']:+.1f}% | Z-Score: {m['zscore']:+.2f}
• RSI: {m['rsi']:.1f} | MACD: {'Bullish' if m['macd']>m['macd_sig'] else 'Bearish'}
• Linear Trend: {m['trend_slope']:+.1f}%/ปี | R²={m['r2']:.2f}
• Volatility: Short={m['vol_s']:.1f}% Long={m['vol_l']:.1f}%
• Composite Score: {m['score']}/100 → {m['verdict']}

ตอบภาษาไทย กระชับ ใช้ตัวเลขที่ให้ไว้ ระบุว่าเป็นการวิเคราะห์เพื่อประกอบการตัดสินใจ"""

        # Render chat
        chat_html = '<div class="chat-wrap">'
        for msg in st.session_state.chat:
            if msg["role"] == "assistant":
                chat_html += f'<div class="msg-row"><div class="av ai">D</div><div class="bub ai-b">{msg["content"].replace(chr(10),"<br>")}</div></div>'
            else:
                chat_html += f'<div class="msg-row u"><div class="av usr">คุณ</div><div class="bub u-b">{msg["content"].replace(chr(10),"<br>")}</div></div>'
        chat_html += '</div>'
        st.markdown(chat_html, unsafe_allow_html=True)

        if q := st.chat_input("ถามเรื่องตัวเลข, ความเสี่ยง, Sharpe, ผลตอบแทน...", key="main_chat"):
            st.session_state.chat.append({"role": "user", "content": q})
            try:
                api_key = st.secrets["GOOGLE_API_KEY"]
                client  = genai.Client(api_key=api_key)
                hist = [
                    {"role": "user" if m_["role"] == "user" else "model",
                     "parts": [{"text": m_["content"]}]}
                    for m_ in st.session_state.chat[1:-1]
                ]
                resp = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=hist + [{"role": "user", "parts": [{"text": sys_ctx + "\n\n---\n" + q}]}]
                )
                reply = resp.text
            except Exception as e:
                reply = f"ขออภัย: {e}"
            st.session_state.chat.append({"role": "assistant", "content": reply})
            st.rerun()

# ─────────────────────────────────────────────────────────────
#  AUTO REFRESH (30s)
# ─────────────────────────────────────────────────────────────
time.sleep(30)
st.rerun()
