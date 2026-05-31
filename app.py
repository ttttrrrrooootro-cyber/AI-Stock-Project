import time
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf
from google import genai

st.set_page_config(page_title="OpenAI DGV", layout="wide")

# ───────────────────────── HEADER ─────────────────────────
OPENAI_SVG = """<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg"><path d="M22.2819 9.8211a5.9847 5.9847 0 0 0-.5157-4.9108 6.0462 6.0462 0 0 0-6.5098-2.9A6.0651 6.0651 0 0 0 4.9807 4.1818a5.9847 5.9847 0 0 0-3.9977 2.9 6.0462 6.0462 0 0 0 .7427 7.0966 5.98 5.98 0 0 0 .511 4.9107 6.051 6.051 0 0 0 6.5146 2.9001A5.9847 5.9847 0 0 0 13.2599 24a6.0557 6.0557 0 0 0 5.7718-4.2058 5.9894 5.9894 0 0 0 3.9977-2.9001 6.0557 6.0557 0 0 0-.7475-7.0729zm-9.022 12.6081a4.4755 4.4755 0 0 1-2.8764-1.0408l.1419-.0804 4.7783-2.7582a.7948.7948 0 0 0 .3927-.6813v-6.7369l2.02 1.1686a.071.071 0 0 1 .038.052v5.5826a4.504 4.504 0 0 1-4.4945 4.4944zm-9.6607-4.1254a4.4708 4.4708 0 0 1-.5346-3.0137l.142.0852 4.783 2.7582a.7712.7712 0 0 0 .7806 0l5.8428-3.3685v2.3324a.0804.0804 0 0 1-.0332.0615L9.74 19.9502a4.4992 4.4992 0 0 1-6.1408-1.6464zM2.3408 7.8956a4.485 4.485 0 0 1 2.3655-1.9728V11.6a.7664.7664 0 0 0 .3879.6765l5.8144 3.3543-2.0201 1.1685a.0757.0757 0 0 1-.071 0l-4.8303-2.7865A4.504 4.504 0 0 1 2.3408 7.872zm16.5963 3.8558L13.1038 8.364 15.1192 7.2a.0757.0757 0 0 1 .071 0l4.8303 2.7913a4.4944 4.4944 0 0 1-.6765 8.1042v-5.6772a.79.79 0 0 0-.407-.667zm2.0107-3.0231l-.142-.0852-4.7735-2.7818a.7759.7759 0 0 0-.7854 0L9.409 9.2297V6.8974a.0662.0662 0 0 1 .0284-.0615l4.8303-2.7866a4.4992 4.4992 0 0 1 6.6802 4.66zM8.3065 12.863l-2.02-1.1638a.0804.0804 0 0 1-.038-.0567V6.0742a4.4992 4.4992 0 0 1 7.3757-3.4537l-.142.0805L8.704 5.459a.7948.7948 0 0 0-.3927.6813zm1.0976-2.3654l2.602-1.4998 2.6069 1.4998v2.9994l-2.5974 1.4997-2.6067-1.4997Z"/></svg>"""

st.markdown(f"""
<style>
.dgv-header{{display:flex;align-items:center;gap:12px;padding:6px 0 2px 0;margin-bottom:6px}}
.dgv-logo{{width:34px;height:34px;background:#000;border-radius:8px;display:flex;align-items:center;justify-content:center;color:#fff;flex-shrink:0}}
.dgv-title{{font-size:21px;font-weight:700;color:#111;letter-spacing:-.5px}}
.dgv-title span{{color:#777;font-weight:400}}
.dgv-sub{{font-size:12px;color:#999;margin-top:1px}}
.tab-badge{{display:inline-block;padding:2px 8px;border-radius:20px;font-size:11px;font-weight:600;margin-left:6px}}
.trade-badge{{background:#fff3cd;color:#856404}}
.invest-badge{{background:#d1e7dd;color:#0a5132}}
/* chat */
.chat-wrapper{{max-height:360px;overflow-y:auto;padding:6px 0}}
.msg-row{{display:flex;gap:9px;margin-bottom:12px;align-items:flex-start}}
.msg-row.user-row{{flex-direction:row-reverse}}
.av{{width:28px;height:28px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:700;flex-shrink:0;margin-top:2px}}
.av.ai-av{{background:#000;color:#fff}}
.av.u-av{{background:#e8f0fe;color:#1a56db}}
.bub{{max-width:80%;padding:9px 13px;border-radius:15px;font-size:13px;line-height:1.6}}
.bub.ai-b{{background:#f4f4f4;color:#111;border-bottom-left-radius:3px}}
.bub.u-b{{background:#000;color:#fff;border-bottom-right-radius:3px}}
.dsc{{font-size:11px;color:#ccc;text-align:center;margin-top:5px}}
/* win rate bar */
.wr-bar-bg{{background:#e9ecef;border-radius:8px;height:14px;width:100%;margin-top:4px}}
.wr-bar-fill{{height:14px;border-radius:8px;transition:width .4s}}
</style>
<div class="dgv-header">
  <div class="dgv-logo">{OPENAI_SVG}</div>
  <div>
    <div class="dgv-title">OpenAI <span>DGV</span></div>
    <div class="dgv-sub">วิเคราะห์การลงทุน · หุ้น · Forex · ทองคำ · คริปโต · สินทรัพย์ที่คุณสนใจ</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ───────────────────────── SESSION STATE ─────────────────────────
for key, val in [
    ("search_history", []),
    ("trade_chat", [{"role":"assistant","content":"สวัสดีครับ! 📊 โซนเทรด SMC พร้อมแล้ว\nถามได้เลย: Entry point, SL/TP, FVG, OB, BOS, Liquidity sweep..."}]),
    ("invest_chat", [{"role":"assistant","content":"สวัสดีครับ! 📈 โซนลงทุนพร้อมแล้ว\nถามได้เลย: แนวโน้มระยะยาว, win rate, fundamental, portfolio..."}]),
]:
    if key not in st.session_state:
        st.session_state[key] = val

# ───────────────────────── HELPER FUNCTIONS ─────────────────────────
def fetch_price(sym):
    try:
        t = yf.Ticker(sym)
        d = t.history(period="5d")
        if not d.empty:
            return {
                "price": round(d["Close"].iloc[-1], 4),
                "change": round(d["Close"].iloc[-1] - d["Close"].iloc[-2], 4),
                "change_pct": round(((d["Close"].iloc[-1] - d["Close"].iloc[-2]) / d["Close"].iloc[-2]) * 100, 2),
            }
    except:
        pass
    return None

MARKET_SYMBOLS = {
    "gold":"GC=F","ทอง":"GC=F","xauusd":"GC=F","silver":"SI=F","xagusd":"SI=F",
    "platinum":"PL=F","แพลทินัม":"PL=F","btc":"BTC-USD","bitcoin":"BTC-USD",
    "บิทคอยน์":"BTC-USD","eth":"ETH-USD","ethereum":"ETH-USD","อีเธอเรียม":"ETH-USD",
    "eurusd":"EURUSD=X","gbpusd":"GBPUSD=X","usdjpy":"USDJPY=X",
    "audusd":"AUDUSD=X","usdthb":"USDTHB=X","oil":"CL=F","น้ำมัน":"CL=F",
    "sp500":"^GSPC","nasdaq":"^IXIC","dow":"^DJI",
    "aapl":"AAPL","tsla":"TSLA","nvda":"NVDA","msft":"MSFT",
    "google":"GOOGL","meta":"META","amazon":"AMZN",
}

def detect_symbols(q):
    ql = q.lower(); found = []
    for k,v in MARKET_SYMBOLS.items():
        if k in ql and v not in found: found.append(v)
    return found[:3]

def get_market_ctx(query):
    syms = detect_symbols(query)
    if not syms: return ""
    rows = []
    for s in syms:
        info = fetch_price(s)
        if info:
            sign = "+" if info["change"] >= 0 else ""
            rows.append(f"{s}: {info['price']:,} ({sign}{info['change_pct']}%)")
    return ("\n\n[ราคาตลาดปัจจุบัน]\n" + "\n".join(rows)) if rows else ""

def calc_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# ───────────────────────── SMC DETECTION ─────────────────────────
def detect_swing_highs(highs, order=5):
    idxs = []
    for i in range(order, len(highs) - order):
        if highs[i] == max(highs[i-order:i+order+1]):
            idxs.append(i)
    return idxs

def detect_swing_lows(lows, order=5):
    idxs = []
    for i in range(order, len(lows) - order):
        if lows[i] == min(lows[i-order:i+order+1]):
            idxs.append(i)
    return idxs

def detect_fvg(df, lookback=80):
    """Fair Value Gaps (3-candle pattern): bullish & bearish"""
    bullish, bearish = [], []
    d = df.tail(lookback).reset_index()
    for i in range(2, len(d)):
        # Bullish FVG: low[i] > high[i-2]
        if d["Low"].iloc[i] > d["High"].iloc[i-2]:
            bullish.append({"top": d["Low"].iloc[i], "bot": d["High"].iloc[i-2],
                            "date": d["Datetime"].iloc[i] if "Datetime" in d.columns else d["Date"].iloc[i] if "Date" in d.columns else d.index[i]})
        # Bearish FVG: high[i] < low[i-2]
        if d["High"].iloc[i] < d["Low"].iloc[i-2]:
            bearish.append({"top": d["Low"].iloc[i-2], "bot": d["High"].iloc[i],
                            "date": d["Datetime"].iloc[i] if "Datetime" in d.columns else d["Date"].iloc[i] if "Date" in d.columns else d.index[i]})
    return bullish[-3:], bearish[-3:]

def detect_ob(df, swing_highs_idx, swing_lows_idx, order=5):
    """Order Blocks: candle just before swing high/low"""
    bullish_ob, bearish_ob = [], []
    closes = df["Close"].values
    highs  = df["High"].values
    lows   = df["Low"].values
    opens  = df["Open"].values
    idx_arr = df.index

    for i in swing_lows_idx:
        if i > 0:
            # Bearish candle before swing low → Bullish OB
            j = i - 1
            if closes[j] < opens[j]:
                bullish_ob.append({"top": opens[j], "bot": lows[j], "date": idx_arr[j]})

    for i in swing_highs_idx:
        if i > 0:
            # Bullish candle before swing high → Bearish OB
            j = i - 1
            if closes[j] > opens[j]:
                bearish_ob.append({"top": highs[j], "bot": opens[j], "date": idx_arr[j]})

    return bullish_ob[-3:], bearish_ob[-3:]

def detect_bos_choch(df, swing_highs_idx, swing_lows_idx):
    """Break of Structure (BOS) & Change of Character (CHoCH)"""
    events = []
    closes = df["Close"].values
    highs  = df["High"].values
    lows   = df["Low"].values
    idx_arr = df.index

    # BOS Bullish: price breaks above previous swing high
    for k, i in enumerate(swing_highs_idx[:-1]):
        next_i = swing_highs_idx[k+1]
        level = highs[i]
        for j in range(i+1, min(next_i+1, len(closes))):
            if closes[j] > level:
                events.append({"type":"BOS Bull","price":level,"date":idx_arr[j],"color":"#26a69a"})
                break

    # BOS Bearish: price breaks below previous swing low
    for k, i in enumerate(swing_lows_idx[:-1]):
        next_i = swing_lows_idx[k+1]
        level = lows[i]
        for j in range(i+1, min(next_i+1, len(closes))):
            if closes[j] < level:
                events.append({"type":"BOS Bear","price":level,"date":idx_arr[j],"color":"#ef5350"})
                break

    return events[-6:]

# ───────────────────────── WIN RATE BACKTEST ─────────────────────────
def backtest_winrate(df):
    """
    Simple backtest: ทดสอบ Signal ย้อนหลัง 1 ปี
    - Signal: ราคาต่ำกว่า MA50 แล้ว bounce ขึ้น (entry = close วันนั้น)
    - Win: ราคาขึ้น >1% ใน 5 วันถัดไป
    - Lose: ราคาลง >1% ใน 5 วันถัดไป
    คืน dict: wins, losses, total, winrate
    """
    d = df.copy()
    d["MA50"] = d["Close"].rolling(50).mean()
    d["RSI"]  = calc_rsi(d["Close"], 14)

    wins = losses = 0
    entries = []

    for i in range(50, len(d) - 5):
        prev_below = d["Close"].iloc[i-1] < d["MA50"].iloc[i-1]
        curr_above = d["Close"].iloc[i]   >= d["MA50"].iloc[i]
        rsi_ok     = d["RSI"].iloc[i] < 55

        if prev_below and curr_above and rsi_ok:
            entry = d["Close"].iloc[i]
            future_max = d["Close"].iloc[i+1:i+6].max()
            future_min = d["Close"].iloc[i+1:i+6].min()
            chg_max = (future_max - entry) / entry * 100
            chg_min = (future_min - entry) / entry * 100

            if chg_max >= 1.0:
                wins += 1
                entries.append({"date": d.index[i], "result":"win"})
            elif chg_min <= -1.0:
                losses += 1
                entries.append({"date": d.index[i], "result":"lose"})

    total = wins + losses
    winrate = round((wins / total * 100), 1) if total > 0 else 0
    return {"wins": wins, "losses": losses, "total": total, "winrate": winrate, "entries": entries}

# ───────────────────────── INVEST ANALYSIS ─────────────────────────
def full_invest_analysis(df, symbol):
    """คืน dict ที่มีตัวชี้วัดการลงทุนครบถ้วน"""
    d = df.copy()
    d["MA20"]  = d["Close"].rolling(20).mean()
    d["MA50"]  = d["Close"].rolling(50).mean()
    d["MA200"] = d["Close"].rolling(200).mean()
    d["RSI"]   = calc_rsi(d["Close"], 14)

    # MACD
    ema12 = d["Close"].ewm(span=12).mean()
    ema26 = d["Close"].ewm(span=26).mean()
    d["MACD"] = ema12 - ema26
    d["Signal"] = d["MACD"].ewm(span=9).mean()

    cur   = d["Close"].iloc[-1]
    ma20  = d["MA20"].iloc[-1]
    ma50  = d["MA50"].iloc[-1]
    ma200 = d["MA200"].iloc[-1] if len(d) >= 200 else None
    rsi   = d["RSI"].iloc[-1]
    macd  = d["MACD"].iloc[-1]
    sig   = d["Signal"].iloc[-1]

    ret_1m = (cur / d["Close"].iloc[-22] - 1) * 100  if len(d) >= 22  else 0
    ret_3m = (cur / d["Close"].iloc[-66] - 1) * 100  if len(d) >= 66  else 0
    ret_6m = (cur / d["Close"].iloc[-126]- 1) * 100  if len(d) >= 126 else 0
    vol_30 = d["Close"].pct_change().tail(30).std() * 100

    score = 0
    signals = []
    if cur > ma50:  score += 20; signals.append(("✅","ราคาอยู่เหนือ MA50"))
    else:           signals.append(("❌","ราคาต่ำกว่า MA50"))
    if ma200 and cur > ma200: score += 20; signals.append(("✅","ราคาอยู่เหนือ MA200 (Bullish)"))
    elif ma200:               signals.append(("❌","ราคาต่ำกว่า MA200 (Bearish)"))
    if rsi < 70 and rsi > 40: score += 15; signals.append(("✅",f"RSI {rsi:.1f} อยู่ในโซนสมดุล"))
    elif rsi <= 40:            score += 10; signals.append(("⚠️",f"RSI {rsi:.1f} Oversold (อาจ Bounce)"))
    else:                                   signals.append(("❌",f"RSI {rsi:.1f} Overbought"))
    if macd > sig:  score += 15; signals.append(("✅","MACD อยู่เหนือ Signal line (Bullish)"))
    else:           signals.append(("❌","MACD ต่ำกว่า Signal line (Bearish)"))
    if ret_6m > 0:  score += 15; signals.append(("✅",f"ผลตอบแทน 6 เดือน +{ret_6m:.1f}%"))
    else:           signals.append(("❌",f"ผลตอบแทน 6 เดือน {ret_6m:.1f}%"))
    if vol_30 < 2.5:score += 15; signals.append(("✅",f"ความผันผวน {vol_30:.1f}% (ต่ำ)"))
    else:           signals.append(("⚠️",f"ความผันผวน {vol_30:.1f}% (สูง)"))

    return {
        "score": score, "signals": signals, "rsi": rsi, "macd": macd, "sig": sig,
        "ma20": ma20, "ma50": ma50, "ma200": ma200, "cur": cur,
        "ret_1m": ret_1m, "ret_3m": ret_3m, "ret_6m": ret_6m, "vol_30": vol_30,
        "df": d
    }

# ───────────────────────── DATA FETCH ─────────────────────────
col_input, col_info = st.columns([1, 2])
with col_input:
    symbol = (
        st.text_input("🔍 กรอกสัญลักษณ์ (เช่น AAPL, EURUSD=X, GC=F, BTC-USD)", "GC=F")
        .upper().replace("/", "")
    )

try:
    ticker = yf.Ticker(symbol)
    data   = ticker.history(period="1y")
    if not data.empty:
        current_price   = data["Close"].iloc[-1]
        previous_close  = data["Close"].iloc[-2] if len(data) > 1 else current_price
        price_change    = current_price - previous_close
        price_change_pct= (price_change / previous_close) * 100
    else:
        current_price = 0
except Exception as e:
    st.error(f"เกิดข้อผิดพลาด: {e}")
    data = pd.DataFrame()

if not data.empty:
    # ── Price header
    st.markdown("### 🔴 ราคาตลาดปัจจุบัน")
    mc1, mc2 = st.columns([1, 3])
    with mc1:
        is_fx = "=X" in symbol
        st.metric(
            label=f"ราคาล่าสุด {symbol}",
            value=f"{current_price:,.4f}" if is_fx else f"${current_price:,.2f}",
            delta=f"{price_change:+.4f} ({price_change_pct:+.2f}%)" if is_fx
                  else f"${price_change:+.2f} ({price_change_pct:+.2f}%)"
        )
    with col_info:
        st.caption("🔄 อัปเดตอัตโนมัติทุก 10 วินาที")

    # ── Compute invest analysis & backtest (shared)
    inv = full_invest_analysis(data, symbol)
    bt  = backtest_winrate(data)

    # ── Search history
    hist_dict = {x["Ticker"]: x for x in st.session_state.search_history}
    hist_dict[symbol] = {
        "Ticker": symbol,
        "Invest Score": inv["score"],
        "Win Rate": f"{bt['winrate']}%",
        "ราคา": f"{current_price:,.4f}" if is_fx else f"{current_price:,.2f}",
        "สัญญาณ": "Strong Buy" if inv["score"]>=80 else "Hold/Watch" if inv["score"]>=50 else "Avoid",
    }
    st.session_state.search_history = list(hist_dict.values())

    # ════════════════════════════════════════════════
    #  TAB: โซนเทรด vs โซนลงทุน
    # ════════════════════════════════════════════════
    tab_trade, tab_invest = st.tabs(["⚡ โซนเทรด (SMC)", "📊 โซนลงทุน (Investment)"])

    # ──────────────────────────────────────────────
    #  TAB 1 : โซนเทรด — SMC Chart + Chat
    # ──────────────────────────────────────────────
    with tab_trade:
        col_chart, col_tchat = st.columns([3, 2])

        with col_chart:
            st.subheader(f"📈 SMC Chart — {symbol}")

            tf_opts = {"3 เดือน": 63, "6 เดือน": 126, "1 ปี": 252}
            tf_sel  = st.radio("Timeframe:", list(tf_opts.keys()), horizontal=True, key="tf_smc")
            n_bars  = tf_opts[tf_sel]
            d_smc   = data.tail(n_bars).copy()

            show_fvg = st.checkbox("แสดง FVG (Fair Value Gap)", value=True, key="cb_fvg")
            show_ob  = st.checkbox("แสดง OB (Order Block)",     value=True, key="cb_ob")
            show_bos = st.checkbox("แสดง BOS / CHoCH",          value=True, key="cb_bos")
            show_liq = st.checkbox("แสดง Liquidity Levels",     value=True, key="cb_liq")

            # Detect SMC structures
            highs_arr = d_smc["High"].values
            lows_arr  = d_smc["Low"].values
            sh_idx = detect_swing_highs(highs_arr, order=4)
            sl_idx = detect_swing_lows(lows_arr,  order=4)

            bull_fvg, bear_fvg = detect_fvg(d_smc)
            bull_ob,  bear_ob  = detect_ob(d_smc, sh_idx, sl_idx)
            bos_events          = detect_bos_choch(d_smc, sh_idx, sl_idx)

            fig_smc = go.Figure()

            # Candlestick
            fig_smc.add_trace(go.Candlestick(
                x=d_smc.index,
                open=d_smc["Open"], high=d_smc["High"],
                low=d_smc["Low"],   close=d_smc["Close"],
                name="Price", increasing_line_color="#26a69a", decreasing_line_color="#ef5350"
            ))

            # MA50
            d_smc["MA50"] = d_smc["Close"].rolling(50).mean()
            fig_smc.add_trace(go.Scatter(
                x=d_smc.index, y=d_smc["MA50"],
                mode="lines", name="MA50",
                line=dict(color="#ff9800", width=1.2, dash="dot")
            ))

            # Swing Highs / Lows (Liquidity)
            if show_liq and sh_idx:
                sh_dates = [d_smc.index[i] for i in sh_idx]
                sh_vals  = [highs_arr[i]   for i in sh_idx]
                fig_smc.add_trace(go.Scatter(
                    x=sh_dates, y=sh_vals, mode="markers",
                    marker=dict(symbol="triangle-down", size=9, color="#ef5350"),
                    name="Swing High (Liq.)"
                ))
                sl_dates = [d_smc.index[i] for i in sl_idx]
                sl_vals  = [lows_arr[i]    for i in sl_idx]
                fig_smc.add_trace(go.Scatter(
                    x=sl_dates, y=sl_vals, mode="markers",
                    marker=dict(symbol="triangle-up", size=9, color="#26a69a"),
                    name="Swing Low (Liq.)"
                ))

            x_start = d_smc.index[0]
            x_end   = d_smc.index[-1]

            # FVG zones
            if show_fvg:
                shapes_fvg = []
                for fvg in bull_fvg:
                    shapes_fvg.append(dict(
                        type="rect", xref="x", yref="y",
                        x0=fvg["date"], x1=x_end,
                        y0=fvg["bot"],  y1=fvg["top"],
                        fillcolor="rgba(38,166,154,0.15)",
                        line=dict(color="rgba(38,166,154,0.5)", width=1),
                    ))
                for fvg in bear_fvg:
                    shapes_fvg.append(dict(
                        type="rect", xref="x", yref="y",
                        x0=fvg["date"], x1=x_end,
                        y0=fvg["bot"],  y1=fvg["top"],
                        fillcolor="rgba(239,83,80,0.15)",
                        line=dict(color="rgba(239,83,80,0.5)", width=1),
                    ))
                # แนบ annotation label FVG
                annots_fvg = []
                for fvg in bull_fvg:
                    annots_fvg.append(dict(
                        x=x_end, y=(fvg["top"]+fvg["bot"])/2,
                        xref="x", yref="y", text="FVG🟢", showarrow=False,
                        font=dict(size=10, color="#26a69a"), xanchor="right"
                    ))
                for fvg in bear_fvg:
                    annots_fvg.append(dict(
                        x=x_end, y=(fvg["top"]+fvg["bot"])/2,
                        xref="x", yref="y", text="FVG🔴", showarrow=False,
                        font=dict(size=10, color="#ef5350"), xanchor="right"
                    ))
            else:
                shapes_fvg, annots_fvg = [], []

            # OB zones
            if show_ob:
                shapes_ob = []
                annots_ob = []
                for ob in bull_ob:
                    shapes_ob.append(dict(
                        type="rect", xref="x", yref="y",
                        x0=ob["date"], x1=x_end,
                        y0=ob["bot"],  y1=ob["top"],
                        fillcolor="rgba(38,166,154,0.22)",
                        line=dict(color="#26a69a", width=1.5, dash="dash"),
                    ))
                    annots_ob.append(dict(
                        x=x_end, y=(ob["top"]+ob["bot"])/2,
                        xref="x", yref="y", text="Bull OB", showarrow=False,
                        font=dict(size=10, color="#26a69a"), xanchor="right"
                    ))
                for ob in bear_ob:
                    shapes_ob.append(dict(
                        type="rect", xref="x", yref="y",
                        x0=ob["date"], x1=x_end,
                        y0=ob["bot"],  y1=ob["top"],
                        fillcolor="rgba(239,83,80,0.22)",
                        line=dict(color="#ef5350", width=1.5, dash="dash"),
                    ))
                    annots_ob.append(dict(
                        x=x_end, y=(ob["top"]+ob["bot"])/2,
                        xref="x", yref="y", text="Bear OB", showarrow=False,
                        font=dict(size=10, color="#ef5350"), xanchor="right"
                    ))
            else:
                shapes_ob, annots_ob = [], []

            # BOS lines
            if show_bos:
                shapes_bos = []
                annots_bos = []
                for ev in bos_events:
                    shapes_bos.append(dict(
                        type="line", xref="x", yref="y",
                        x0=x_start, x1=x_end,
                        y0=ev["price"], y1=ev["price"],
                        line=dict(color=ev["color"], width=1.2, dash="dot"),
                    ))
                    annots_bos.append(dict(
                        x=x_start, y=ev["price"],
                        xref="x", yref="y",
                        text=ev["type"], showarrow=False,
                        font=dict(size=10, color=ev["color"]), xanchor="left"
                    ))
            else:
                shapes_bos, annots_bos = [], []

            fig_smc.update_layout(
                shapes=shapes_fvg + shapes_ob + shapes_bos,
                annotations=annots_fvg + annots_ob + annots_bos,
                xaxis_rangeslider_visible=False,
                height=500,
                margin=dict(l=10, r=10, t=10, b=10),
                legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor="rgba(255,255,255,0.7)"),
                plot_bgcolor="white",
                paper_bgcolor="white",
            )
            st.plotly_chart(fig_smc, use_container_width=True)

            # SMC Summary
            st.markdown("**📋 สรุป SMC Zones ที่ตรวจพบ**")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Bullish FVG", len(bull_fvg))
            c2.metric("Bearish FVG", len(bear_fvg))
            c3.metric("Bull OB",     len(bull_ob))
            c4.metric("Bear OB",     len(bear_ob))

        with col_tchat:
            # ── Trade Chat (SMC Assistant)
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">
              <div style="width:22px;height:22px;background:#000;border-radius:5px;display:flex;align-items:center;justify-content:center;color:#fff">{OPENAI_SVG.replace('width="18" height="18"','width="13" height="13"')}</div>
              <span style="font-size:14px;font-weight:700">OpenAI DGV</span>
              <span style="font-size:11px;color:#999">SMC Trade Assistant</span>
            </div>
            """, unsafe_allow_html=True)

            # SMC context for prompt
            price_str = f"{current_price:,.4f}" if is_fx else f"{current_price:,.2f}"
            smc_ctx = (
                f"Symbol: {symbol} | ราคา: {price_str}\n"
                f"Bullish FVG: {len(bull_fvg)} | Bearish FVG: {len(bear_fvg)}\n"
                f"Bull OB: {len(bull_ob)} | Bear OB: {len(bear_ob)}\n"
                f"BOS Events: {len(bos_events)}\n"
                f"Swing Highs: {len(sh_idx)} | Swing Lows: {len(sl_idx)}\n"
            )
            if bull_fvg:
                smc_ctx += f"Bullish FVG ล่าสุด: {bull_fvg[-1]['bot']:.4f} - {bull_fvg[-1]['top']:.4f}\n"
            if bear_fvg:
                smc_ctx += f"Bearish FVG ล่าสุด: {bear_fvg[-1]['bot']:.4f} - {bear_fvg[-1]['top']:.4f}\n"
            if bull_ob:
                smc_ctx += f"Bull OB ล่าสุด: {bull_ob[-1]['bot']:.4f} - {bull_ob[-1]['top']:.4f}\n"
            if bear_ob:
                smc_ctx += f"Bear OB ล่าสุด: {bear_ob[-1]['bot']:.4f} - {bear_ob[-1]['top']:.4f}\n"

            trade_system = (
                "คุณคือ OpenAI DGV SMC Trade Assistant ผู้เชี่ยวชาญ Smart Money Concept\n\n"
                f"ข้อมูล SMC ที่วิเคราะห์ได้:\n{smc_ctx}\n"
                "ตอบภาษาไทย กระชับ ระบุ Entry/SL/TP เป็นตัวเลขเสมอถ้าถาม\n"
                "ใช้ FVG/OB/BOS/Liquidity ในการวิเคราะห์ ระบุว่าเป็นการวิเคราะห์เท่านั้น"
            )

            # Render bubbles
            trade_html = '<div class="chat-wrapper">'
            for m in st.session_state.trade_chat:
                if m["role"] == "assistant":
                    trade_html += f'<div class="msg-row"><div class="av ai-av">AI</div><div class="bub ai-b">{m["content"].replace(chr(10),"<br>")}</div></div>'
                else:
                    trade_html += f'<div class="msg-row user-row"><div class="av u-av">คุณ</div><div class="bub u-b">{m["content"].replace(chr(10),"<br>")}</div></div>'
            trade_html += '</div><div class="dsc">วิเคราะห์เพื่อประกอบการตัดสินใจเท่านั้น</div>'
            st.markdown(trade_html, unsafe_allow_html=True)

            if q := st.chat_input("ถามเรื่อง Entry, SL/TP, FVG, OB...", key="trade_input"):
                st.session_state.trade_chat.append({"role":"user","content":q})
                mkt = get_market_ctx(q)
                full_q = q + mkt
                try:
                    api_key = st.secrets["GOOGLE_API_KEY"]
                    client  = genai.Client(api_key=api_key)
                    hist = [{"role":"user" if m["role"]=="user" else "model",
                             "parts":[{"text":m["content"]}]}
                            for m in st.session_state.trade_chat[1:-1]]
                    resp = client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=hist + [{"role":"user","parts":[{"text": trade_system+"\n\n---\n"+full_q}]}]
                    )
                    reply = resp.text
                except Exception as e:
                    reply = f"ขออภัย: {e}"
                st.session_state.trade_chat.append({"role":"assistant","content":reply})
                st.rerun()

    # ──────────────────────────────────────────────
    #  TAB 2 : โซนลงทุน — Full Analysis + Win Rate + Chat
    # ──────────────────────────────────────────────
    with tab_invest:
        col_inv, col_ichat = st.columns([3, 2])

        with col_inv:
            st.subheader(f"📊 การวิเคราะห์การลงทุน — {symbol}")

            # ── Invest Score + Win Rate metrics
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Invest Score",   f"{inv['score']} / 100")
            m2.metric("Win Rate (Backtest)", f"{bt['winrate']}%")
            m3.metric("สัญญาณ (1 เดือน)",  f"{inv['ret_1m']:+.1f}%")
            m4.metric("ความผันผวน 30วัน",  f"{inv['vol_30']:.1f}%")

            # Signal label
            if inv["score"] >= 80:
                st.success("🔥 Strong Buy — น่าลงทุนสูงมาก")
            elif inv["score"] >= 55:
                st.warning("⏳ Hold/Watch — รอจังหวะหรือทยอยสะสม")
            else:
                st.error("🚨 Avoid — ความเสี่ยงสูง ชะลอการลงทุน")

            # Win rate bar
            wr = bt["winrate"]
            wr_color = "#198754" if wr >= 60 else "#ffc107" if wr >= 45 else "#dc3545"
            st.markdown(f"""
            <div style="margin:10px 0 4px">
              <span style="font-size:13px;font-weight:600">Win Rate จาก Backtest ย้อนหลัง 1 ปี</span>
              <span style="font-size:12px;color:#888;margin-left:8px">({bt['wins']}W / {bt['losses']}L จาก {bt['total']} Signals)</span>
            </div>
            <div class="wr-bar-bg">
              <div class="wr-bar-fill" style="width:{min(wr,100)}%;background:{wr_color}"></div>
            </div>
            <div style="font-size:13px;font-weight:700;color:{wr_color};margin-top:4px">{wr}% โอกาสที่การวิเคราะห์จะถูกต้อง</div>
            """, unsafe_allow_html=True)

            st.markdown("---")

            # ── Signal checklist
            st.markdown("**🔍 ผลการวิเคราะห์ตัวชี้วัด**")
            for icon, txt in inv["signals"]:
                st.markdown(f"{icon} {txt}")

            st.markdown("---")

            # ── Return summary
            st.markdown("**📅 ผลตอบแทนย้อนหลัง**")
            r1, r2, r3 = st.columns(3)
            r1.metric("1 เดือน",  f"{inv['ret_1m']:+.1f}%")
            r2.metric("3 เดือน",  f"{inv['ret_3m']:+.1f}%")
            r3.metric("6 เดือน",  f"{inv['ret_6m']:+.1f}%")

            # ── Invest chart (Line + MA20 + MA50 + MA200)
            fig_inv = go.Figure()
            fig_inv.add_trace(go.Scatter(
                x=inv["df"].index, y=inv["df"]["Close"],
                mode="lines", name="ราคาปิด", line=dict(color="#1976d2", width=2)
            ))
            fig_inv.add_trace(go.Scatter(
                x=inv["df"].index, y=inv["df"]["MA20"],
                mode="lines", name="MA20", line=dict(color="#ff9800", width=1, dash="dot")
            ))
            fig_inv.add_trace(go.Scatter(
                x=inv["df"].index, y=inv["df"]["MA50"],
                mode="lines", name="MA50", line=dict(color="#9c27b0", width=1.2)
            ))
            if inv["ma200"]:
                fig_inv.add_trace(go.Scatter(
                    x=inv["df"].index, y=inv["df"]["MA200"],
                    mode="lines", name="MA200", line=dict(color="#f44336", width=1.5, dash="dash")
                ))

            # Mark backtest entries
            if bt["entries"]:
                win_dates  = [e["date"] for e in bt["entries"] if e["result"]=="win"]
                lose_dates = [e["date"] for e in bt["entries"] if e["result"]=="lose"]
                win_prices = [inv["df"]["Close"].get(d, None) for d in win_dates if d in inv["df"].index]
                lose_prices= [inv["df"]["Close"].get(d, None) for d in lose_dates if d in inv["df"].index]
                if win_prices:
                    fig_inv.add_trace(go.Scatter(
                        x=[d for d in win_dates if d in inv["df"].index],
                        y=win_prices, mode="markers", name="Entry Win",
                        marker=dict(symbol="triangle-up", size=10, color="#26a69a")
                    ))
                if lose_prices:
                    fig_inv.add_trace(go.Scatter(
                        x=[d for d in lose_dates if d in inv["df"].index],
                        y=lose_prices, mode="markers", name="Entry Lose",
                        marker=dict(symbol="triangle-down", size=10, color="#ef5350")
                    ))

            fig_inv.update_layout(
                height=380,
                xaxis_rangeslider_visible=False,
                margin=dict(l=10, r=10, t=10, b=10),
                legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor="rgba(255,255,255,0.8)"),
                plot_bgcolor="white", paper_bgcolor="white"
            )
            st.plotly_chart(fig_inv, use_container_width=True)

            # ── Asset ranking table
            st.subheader("🏆 อันดับสินทรัพย์ทั้งหมด")
            df_rank = pd.DataFrame(st.session_state.search_history)
            if not df_rank.empty:
                df_rank = df_rank.sort_values("Invest Score", ascending=False).reset_index(drop=True)
                st.dataframe(df_rank, use_container_width=True)

        with col_ichat:
            # ── Invest Chat
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">
              <div style="width:22px;height:22px;background:#000;border-radius:5px;display:flex;align-items:center;justify-content:center;color:#fff">{OPENAI_SVG.replace('width="18" height="18"','width="13" height="13"')}</div>
              <span style="font-size:14px;font-weight:700">OpenAI DGV</span>
              <span style="font-size:11px;color:#999">Investment Assistant</span>
            </div>
            """, unsafe_allow_html=True)

            inv_system = (
                "คุณคือ OpenAI DGV Investment Assistant ผู้เชี่ยวชาญการลงทุนระยะยาว\n\n"
                f"ข้อมูลการวิเคราะห์ {symbol}:\n"
                f"- Invest Score: {inv['score']}/100\n"
                f"- Win Rate (Backtest): {bt['winrate']}% ({bt['wins']}W/{bt['losses']}L จาก {bt['total']} signals)\n"
                f"- RSI: {inv['rsi']:.1f} | MACD: {'Bullish' if inv['macd']>inv['sig'] else 'Bearish'}\n"
                f"- MA50: {inv['ma50']:.4f} | MA200: {inv['ma200']:.4f if inv['ma200'] else 'N/A'}\n"
                f"- ผลตอบแทน 1M: {inv['ret_1m']:+.1f}% | 3M: {inv['ret_3m']:+.1f}% | 6M: {inv['ret_6m']:+.1f}%\n"
                f"- ความผันผวน: {inv['vol_30']:.1f}%\n\n"
                "ตอบภาษาไทย กระชับ ให้ข้อมูลเชิงลึก พร้อมแนะนำ position sizing และ risk management\n"
                "ระบุเสมอว่าเป็นการวิเคราะห์เพื่อประกอบการตัดสินใจเท่านั้น"
            )

            invest_html = '<div class="chat-wrapper">'
            for m in st.session_state.invest_chat:
                if m["role"] == "assistant":
                    invest_html += f'<div class="msg-row"><div class="av ai-av">AI</div><div class="bub ai-b">{m["content"].replace(chr(10),"<br>")}</div></div>'
                else:
                    invest_html += f'<div class="msg-row user-row"><div class="av u-av">คุณ</div><div class="bub u-b">{m["content"].replace(chr(10),"<br>")}</div></div>'
            invest_html += '</div><div class="dsc">วิเคราะห์เพื่อประกอบการตัดสินใจเท่านั้น</div>'
            st.markdown(invest_html, unsafe_allow_html=True)

            if q2 := st.chat_input("ถามเรื่องแนวโน้ม win rate การลงทุน...", key="invest_input"):
                st.session_state.invest_chat.append({"role":"user","content":q2})
                mkt2 = get_market_ctx(q2)
                full_q2 = q2 + mkt2
                try:
                    api_key = st.secrets["GOOGLE_API_KEY"]
                    client  = genai.Client(api_key=api_key)
                    hist2 = [{"role":"user" if m["role"]=="user" else "model",
                              "parts":[{"text":m["content"]}]}
                             for m in st.session_state.invest_chat[1:-1]]
                    resp2 = client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=hist2 + [{"role":"user","parts":[{"text": inv_system+"\n\n---\n"+full_q2}]}]
                    )
                    reply2 = resp2.text
                except Exception as e:
                    reply2 = f"ขออภัย: {e}"
                st.session_state.invest_chat.append({"role":"assistant","content":reply2})
                st.rerun()

    time.sleep(10)
    st.rerun()
