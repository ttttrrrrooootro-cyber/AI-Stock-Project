"""
DGV Investment Analyzer — Mathematical Deep Analysis (Enhanced Edition)
วิเคราะห์การลงทุนด้วยคณิตศาสตร์ย้อนหลัง 10 ปี
ราคา Real-time จาก Finnhub | ข้อมูลย้อนหลังจาก yfinance + Stooq | AI โดย Claude (Anthropic)

✨ Enhanced: อนิเมชั่นลื่นไหล · UI สวยขึ้น · ระบบเสถียรขึ้น ·
   กราฟ Real-time จริง (intraday) · 5 เส้นแนวโน้มที่ดีที่สุด (Advanced Models) ·
   กองทุน/ETF/คริปโตเพิ่มเติม · ข่าว + วิเคราะห์อนาคตด้วย AI · AI ที่ปรึกษาเป็นกันเอง
"""

import time
import datetime as dt
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
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────
#  GLOBAL CSS  —  Dark "Terminal" theme + Rich Animations
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
  --border-hi: rgba(255,255,255,0.14);
  --glow-gold: rgba(230,195,92,0.18);
  --ink:       #e9eef7;
  --muted:     #79859a;
  --gold:      #e6c35c;
  --gold-dim:  #c8a84b;
  --green:     #2ee6a0;
  --cyan:      #34e3c4;
  --red:       #ff5d6c;
  --blue:      #5b8def;
  --purple:    #a877e6;
}

/* ═══════════════ KEYFRAMES (Animations) ═══════════════ */
@keyframes fadeInUp {
  from { opacity:0; transform: translateY(18px); }
  to   { opacity:1; transform: translateY(0); }
}
@keyframes fadeIn {
  from { opacity:0; } to { opacity:1; }
}
@keyframes slideInLeft {
  from { opacity:0; transform: translateX(-16px); }
  to   { opacity:1; transform: translateX(0); }
}
@keyframes scaleIn {
  from { opacity:0; transform: scale(.92); }
  to   { opacity:1; transform: scale(1); }
}
@keyframes pulse {
  0%,100% { opacity:1; transform: scale(1); }
  50%     { opacity:.35; transform: scale(.7); }
}
@keyframes glowPulse {
  0%,100% { box-shadow: 0 0 14px var(--glow-gold); }
  50%     { box-shadow: 0 0 28px rgba(230,195,92,.45); }
}
@keyframes shimmer {
  0%   { background-position: -200% 0; }
  100% { background-position:  200% 0; }
}
@keyframes float {
  0%,100% { transform: translateY(0); }
  50%     { transform: translateY(-6px); }
}
@keyframes bgShift {
  0%   { background-position: 0% 50%, 100% 50%, 0 0; }
  50%  { background-position: 40% 60%, 60% 40%, 0 0; }
  100% { background-position: 0% 50%, 100% 50%, 0 0; }
}
@keyframes ringSweep {
  from { stroke-dashoffset: var(--dash-full); }
  to   { stroke-dashoffset: var(--dash-target); }
}
@keyframes gradientText {
  0%,100% { background-position: 0% 50%; }
  50%     { background-position: 100% 50%; }
}
@keyframes blink {
  0%,100% { opacity:1; } 50% { opacity:.2; }
}

/* App background — animated radial glow */
html, body, [class*="css"], .stApp {
  font-family: 'Space Grotesk','DM Sans', sans-serif !important;
  color: var(--ink) !important;
}
.stApp {
  background:
    radial-gradient(1100px 520px at 18% -8%, rgba(230,195,92,0.08), transparent 60%),
    radial-gradient(900px 520px at 95% 8%, rgba(52,227,196,0.06), transparent 55%),
    var(--bg) !important;
  background-size: 200% 200%, 200% 200%, 100% 100% !important;
  animation: bgShift 22s ease-in-out infinite;
}
.block-container { padding-top: 1rem; animation: fadeIn .6s ease both; }

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
  animation: fadeInUp .7s cubic-bezier(.21,.6,.35,1) both;
}
.dgv-masthead::before {
  content:''; position:absolute; inset:0;
  background: linear-gradient(110deg, transparent 30%, rgba(255,255,255,0.05) 50%, transparent 70%);
  background-size: 200% 100%;
  animation: shimmer 6s linear infinite;
  pointer-events:none;
}
.dgv-masthead::after {
  content:''; position:absolute; left:0; right:0; bottom:0; height:2px;
  background: linear-gradient(90deg, transparent, var(--gold), var(--cyan), transparent);
  background-size: 200% 100%;
  animation: shimmer 4s linear infinite;
  opacity:.85;
}
.dgv-wordmark {
  font-family:'DM Serif Display',serif;
  font-size: 40px; line-height:1; letter-spacing:-2px;
  background: linear-gradient(120deg, var(--gold) 0%, #fff4cf 45%, var(--gold-dim) 90%);
  background-size: 200% auto;
  -webkit-background-clip:text; background-clip:text; color:transparent;
  filter: drop-shadow(0 2px 14px var(--glow-gold));
  animation: gradientText 5s ease infinite, float 6s ease-in-out infinite;
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

/* ── Finnhub price panel (glass) ────────────────────── */
.rt-panel {
  background: linear-gradient(160deg, rgba(255,255,255,0.04), rgba(255,255,255,0.01));
  backdrop-filter: blur(14px);
  border: 1px solid var(--border);
  border-radius: 14px; padding: 16px 20px; margin-bottom: 18px;
  display: grid; grid-template-columns: repeat(auto-fit, minmax(112px,1fr)); gap: 14px;
  box-shadow: 0 6px 30px rgba(0,0,0,0.35);
  animation: fadeInUp .6s ease both;
}
.rt-item { animation: scaleIn .5s ease both; }
.rt-item-label { font-size:10px; letter-spacing:1.5px; text-transform:uppercase;
  color: var(--muted); margin-bottom:4px; font-family:'JetBrains Mono',monospace; }
.rt-item-val { font-family:'JetBrains Mono',monospace; font-size:17px; font-weight:600; color:#fff;
  transition: color .3s ease; }
.rt-item-val.pos { color: var(--green); text-shadow:0 0 12px rgba(46,230,160,.4); }
.rt-item-val.neg { color: var(--red);   text-shadow:0 0 12px rgba(255,93,108,.35); }
.rt-item-val.gold{ color: var(--gold);  text-shadow:0 0 14px var(--glow-gold); }

/* ── Section headers ────────────────────────────────── */
.section-title {
  font-family:'DM Serif Display',serif; font-size: 21px; color: var(--ink);
  margin-bottom: 14px; display:flex; align-items:center; gap:10px;
  animation: slideInLeft .5s ease both;
}
.section-title::before {
  content:''; width:4px; height:20px; border-radius:3px;
  background: linear-gradient(var(--gold), var(--cyan));
  box-shadow: 0 0 10px var(--glow-gold);
}

/* ── Metric cards (glass + glow rail) ───────────────── */
.mcard {
  background: linear-gradient(160deg, rgba(255,255,255,0.045), rgba(255,255,255,0.012));
  border: 1px solid var(--border); border-radius: 12px;
  padding: 13px 15px; position: relative; overflow:hidden;
  transition: transform .2s cubic-bezier(.2,.8,.2,1), box-shadow .2s ease, border-color .2s ease;
  animation: fadeInUp .5s ease both;
}
.mcard:hover { transform: translateY(-3px) scale(1.012);
  box-shadow:0 12px 30px rgba(0,0,0,.45); border-color: var(--border-hi); }
.mcard::before { content:''; position:absolute; top:0; left:0; bottom:0; width:3px;
  background: var(--gold); box-shadow: 0 0 14px var(--glow-gold); }
.mcard::after { content:''; position:absolute; inset:0;
  background: linear-gradient(110deg, transparent 40%, rgba(255,255,255,0.04) 50%, transparent 60%);
  background-size: 220% 100%; opacity:0; transition: opacity .3s ease; }
.mcard:hover::after { opacity:1; animation: shimmer 1.2s linear; }
.mcard-label { font-size:10px; letter-spacing:1.5px; text-transform:uppercase;
  color: var(--muted); margin-bottom:5px; }
.mcard-value { font-family:'JetBrains Mono',monospace; font-size:21px; font-weight:600; color: var(--ink); }
.mcard-sub { font-size:11px; color: var(--muted); margin-top:3px; }
.mcard.pos .mcard-value { color: var(--green); }
.mcard.neg .mcard-value { color: var(--red); }
.mcard.gold .mcard-value{ color: var(--gold); }
.mcard.pos::before  { background: var(--green); box-shadow:0 0 14px rgba(46,230,160,.5); }
.mcard.neg::before  { background: var(--red);   box-shadow:0 0 14px rgba(255,93,108,.45); }
.mcard.blue::before { background: var(--blue); box-shadow:0 0 14px rgba(91,141,239,.45); }

/* ── Score ring / verdict ───────────────────────────── */
.score-ring {
  display:flex; align-items:center; gap:26px;
  background: linear-gradient(135deg, #0d1322, #15203a);
  border: 1px solid var(--border); border-radius: 16px;
  padding: 20px 26px; margin-bottom: 18px; position:relative; overflow:hidden;
  box-shadow: inset 0 1px 0 rgba(255,255,255,.05);
  animation: scaleIn .6s cubic-bezier(.2,.8,.2,1) both;
}
.score-ring::after { content:''; position:absolute; right:-40px; top:-40px;
  width:180px; height:180px; border-radius:50%;
  background: radial-gradient(var(--glow-gold), transparent 70%);
  animation: glowPulse 4s ease-in-out infinite; }

/* circular gauge svg */
.gauge-wrap { position:relative; width:120px; height:120px; flex-shrink:0; }
.gauge-svg { transform: rotate(-90deg); }
.gauge-track { fill:none; stroke: rgba(255,255,255,0.07); stroke-width:11; }
.gauge-prog  { fill:none; stroke-width:11; stroke-linecap:round;
  stroke-dasharray: var(--circ);
  animation: ringSweep 1.4s cubic-bezier(.2,.8,.2,1) forwards;
  filter: drop-shadow(0 0 8px currentColor); }
.gauge-center { position:absolute; inset:0; display:flex; flex-direction:column;
  align-items:center; justify-content:center; }
.gauge-num { font-family:'DM Serif Display',serif; font-size:38px; line-height:1;
  background: linear-gradient(120deg,var(--gold),#fff4cf,var(--gold-dim));
  -webkit-background-clip:text; background-clip:text; color:transparent;
  filter: drop-shadow(0 0 12px var(--glow-gold)); }
.gauge-max { font-size:10px; color:#7d8799; margin-top:-2px; }

.score-label { font-size:11px; color: var(--muted); letter-spacing:2px; text-transform:uppercase; }
.score-verdict { font-size:22px; font-weight:700; color:#fff; margin-top:4px;
  animation: fadeInUp .8s ease both; }

/* ── Signal rows ────────────────────────────────────── */
.sig-row { display:flex; align-items:center; gap:11px; padding:8px 0;
  border-bottom:1px solid var(--border); font-size:13px;
  animation: slideInLeft .45s ease both; transition: background .2s ease; }
.sig-row:hover { background: rgba(255,255,255,0.02); }
.sig-icon { font-size:16px; width:22px; text-align:center; }
.sig-text { flex:1; color: var(--ink); }
.sig-badge { font-family:'JetBrains Mono',monospace; font-size:11px; padding:2px 8px;
  border-radius:6px; background: rgba(255,255,255,0.05); color: var(--muted);
  border:1px solid var(--border); }

/* ── Chat ───────────────────────────────────────────── */
.chat-wrap { max-height:380px; overflow-y:auto; padding:14px;
  border:1px solid var(--border); border-radius:14px;
  background: linear-gradient(160deg, rgba(255,255,255,0.03), rgba(255,255,255,0.008));
  margin-bottom:8px; scroll-behavior:smooth; }
.chat-wrap::-webkit-scrollbar { width:7px; }
.chat-wrap::-webkit-scrollbar-thumb { background: rgba(230,195,92,0.25); border-radius:6px; }
.msg-row { display:flex; gap:8px; margin-bottom:12px; align-items:flex-start;
  animation: fadeInUp .4s ease both; }
.msg-row.u { flex-direction: row-reverse; }
.av { width:30px; height:30px; border-radius:9px; display:flex; align-items:center;
  justify-content:center; font-size:11px; font-weight:700; flex-shrink:0; margin-top:2px; }
.av.ai { background: linear-gradient(135deg,#1a2236,#0e1320); color: var(--gold);
  font-family:'DM Serif Display',serif; border:1px solid var(--border);
  box-shadow:0 0 12px var(--glow-gold); }
.av.usr { background: linear-gradient(135deg, var(--blue), #3a63b8); color:#fff; }
.bub { max-width:82%; padding:11px 15px; border-radius:14px; font-size:13px; line-height:1.7; }
.bub.ai-b { background: rgba(255,255,255,0.05); color: var(--ink);
  border:1px solid var(--border); border-bottom-left-radius:4px; }
.bub.u-b  { background: linear-gradient(135deg,#1d2940,#16203a); color:#fff;
  border:1px solid var(--border); border-bottom-right-radius:4px; }
.typing { display:inline-flex; gap:4px; }
.typing span { width:6px; height:6px; border-radius:50%; background:var(--gold);
  animation: blink 1.2s infinite; }
.typing span:nth-child(2){ animation-delay:.2s; }
.typing span:nth-child(3){ animation-delay:.4s; }

/* ── Calc result ────────────────────────────────────── */
.calc-result { background: linear-gradient(135deg,#0d1322,#15203a);
  border:1px solid var(--border); color:#fff; border-radius:14px; padding:16px 20px;
  animation: fadeInUp .5s ease both; }
.calc-row { display:flex; justify-content:space-between; padding:6px 0;
  border-bottom:1px solid var(--border); font-size:13px; }
.calc-row:last-child { border-bottom:none; }
.calc-row span:last-child { font-family:'JetBrains Mono',monospace; color: var(--gold); font-weight:600; }

/* ── Progress bar ───────────────────────────────────── */
.pb-bg { background: rgba(255,255,255,0.07); border-radius:6px; height:10px; width:100%; overflow:hidden; }
.pb-fill { height:10px; border-radius:6px; transition: width 1s cubic-bezier(.2,.8,.2,1);
  box-shadow:0 0 12px currentColor;
  background-image: linear-gradient(90deg, transparent, rgba(255,255,255,0.25), transparent);
  background-size: 200% 100%; animation: shimmer 2.4s linear infinite; }

/* ── Rank table ─────────────────────────────────────── */
.rank-table { width:100%; border-collapse: collapse; font-size:13px;
  background: rgba(255,255,255,0.02); border-radius:12px; overflow:hidden;
  animation: fadeInUp .6s ease both; }
.rank-table th { background: rgba(255,255,255,0.04); color: var(--gold); padding:11px 12px;
  text-align:left; font-family:'JetBrains Mono',monospace; font-weight:600;
  font-size:11px; letter-spacing:1px; border-bottom:1px solid var(--border); }
.rank-table td { padding:11px 12px; border-bottom:1px solid var(--border); vertical-align:middle; color:var(--ink); }
.rank-table tr { transition: background .2s ease; }
.rank-table tr:hover td { background: rgba(255,255,255,0.05); }
.rank-num { font-family:'DM Serif Display',serif; font-size:21px; color: var(--gold); }
.rank-ticker { font-family:'JetBrains Mono',monospace; font-weight:600; font-size:14px; color:var(--ink); }

/* ── Info pill / forecast box ───────────────────────── */
.fc-banner { background: linear-gradient(135deg, rgba(91,141,239,0.10), rgba(168,119,230,0.06));
  border:1px solid var(--border); border-radius:14px; padding:14px 18px; margin-bottom:14px;
  font-size:13px; color:var(--ink); animation: fadeInUp .5s ease both; }
.fc-banner b { color: var(--gold); }

/* ── Streamlit widgets (dark) ───────────────────────── */
.stTextInput input, .stNumberInput input {
  background: rgba(255,255,255,0.04) !important; color: var(--ink) !important;
  border:1px solid var(--border) !important; border-radius:10px !important;
  transition: border-color .25s ease, box-shadow .25s ease; }
.stTextInput input:focus, .stNumberInput input:focus {
  border-color: var(--gold) !important; box-shadow:0 0 0 2px var(--glow-gold) !important; }
[data-testid="stMetricValue"] { font-family:'JetBrains Mono',monospace; color: var(--ink); }
[data-testid="stMetricLabel"] { color: var(--muted); }
.stCaption, .stMarkdown small { color: var(--muted) !important; }
.stChatInput textarea { background: rgba(255,255,255,0.04) !important; color: var(--ink) !important; }
[data-testid="stChatInput"], .stChatInput, .stChatInput > div {
  border-color: var(--border) !important; }
.stChatInput { border:1px solid var(--border) !important; border-radius:14px !important;
  background: rgba(255,255,255,0.03) !important; transition: border-color .25s ease, box-shadow .25s ease; }
.stChatInput:focus-within {
  border-color: var(--gold) !important; box-shadow:0 0 0 2px var(--glow-gold) !important; }

/* buttons */
.stButton button {
  border:1px solid var(--border) !important; border-radius:10px !important;
  background: linear-gradient(160deg, rgba(255,255,255,0.05), rgba(255,255,255,0.01)) !important;
  color: var(--ink) !important; transition: all .2s ease !important; }
.stButton button:hover {
  border-color: var(--gold) !important; transform: translateY(-1px);
  box-shadow: 0 6px 18px rgba(0,0,0,.4), 0 0 14px var(--glow-gold) !important; color: var(--gold) !important; }

/* ── Tabs ───────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] { gap:6px; border-bottom:1px solid var(--border); }
.stTabs [data-baseweb="tab"] {
  font-family:'Space Grotesk',sans-serif !important; font-size:13px !important; font-weight:600 !important;
  padding:9px 18px !important; border-radius:10px 10px 0 0 !important; color: var(--muted) !important;
  transition: all .2s ease; }
.stTabs [data-baseweb="tab"]:hover { color: var(--ink) !important; background: rgba(255,255,255,0.03) !important; }
.stTabs [aria-selected="true"] {
  background: linear-gradient(160deg, rgba(230,195,92,0.14), rgba(255,255,255,0.02)) !important;
  color: var(--gold) !important; border-bottom:2px solid var(--gold) !important; }

/* alerts */
.stAlert { background: rgba(255,255,255,0.04) !important; border:1px solid var(--border) !important;
  border-radius:12px !important; color: var(--ink) !important; }

/* expander */
.streamlit-expanderHeader, [data-testid="stExpander"] summary {
  background: rgba(255,255,255,0.03) !important; border-radius:10px !important; color: var(--ink) !important; }
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
      วิเคราะห์การลงทุนด้วยคณิตศาสตร์ · ย้อนหลัง 10 ปี · ราคา Real-time จาก Finnhub ·
      พยากรณ์อนาคต Monte Carlo · AI โดย Claude
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

try:
    finnhub_client = get_finnhub_client()
except Exception:
    finnhub_client = None

# โมเดล Claude — เปลี่ยนได้ตามต้องการ (เช่น claude-opus-4-6 / claude-haiku-4-5-20251001)
CLAUDE_MODEL = "claude-sonnet-4-6"

# ─────────────────────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────────────────────
for k, v in [
    ("history", {}),
    ("chat", [{"role": "assistant", "content":
               "สวัสดี ผมคือ DGV ผู้ช่วยวิเคราะห์การลงทุนเชิงปริมาณ\n\n"
               "ผมวิเคราะห์จากตัวเลขและสถิติย้อนหลังล้วน ๆ เช่น Sharpe Ratio, ความผันผวน, "
               "Max Drawdown, โมเมนตัม และผลตอบแทนย้อนหลัง — ไม่อิงข่าวลือหรืออารมณ์ตลาด\n\n"
               "ถามได้เลยว่าต้องการทราบอะไร เช่น สินทรัพย์นี้เสี่ยงแค่ไหน "
               "ผลตอบแทนย้อนหลังเป็นอย่างไร หรือควรจัดสรรเงินลงทุนอย่างไร"}]),
    ("last_refresh", 0),
]:
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────────────────────
#  ASSET GROUPS (กองทุน/ETF/คริปโต/หุ้น/ดัชนี เพิ่มเติม)
# ─────────────────────────────────────────────────────────────
ASSET_GROUPS = {
    "หุ้นเทคใหญ่ (Mega-cap Tech)": {
        "NVDA":  "NVIDIA",
        "AAPL":  "Apple",
        "MSFT":  "Microsoft",
        "GOOGL": "Alphabet (Google)",
        "AMZN":  "Amazon",
        "META":  "Meta Platforms",
        "TSLA":  "Tesla",
        "AMD":   "AMD",
        "NFLX":  "Netflix",
        "AVGO":  "Broadcom",
    },
    "ETF & กองทุน (Funds/ETFs)": {
        "SPY":  "SPDR S&P 500 ETF",
        "QQQ":  "Invesco Nasdaq-100 ETF",
        "VOO":  "Vanguard S&P 500 ETF",
        "VTI":  "Vanguard Total Market ETF",
        "SCHD": "Schwab US Dividend ETF",
        "ARKK": "ARK Innovation ETF",
        "GLD":  "SPDR Gold Shares (ทองคำ)",
        "TLT":  "iShares 20Y Treasury (พันธบัตร)",
        "SMH":  "VanEck Semiconductor ETF",
        "VWO":  "Vanguard Emerging Markets ETF",
    },
    "คริปโต (Crypto)": {
        "BTC-USD": "Bitcoin",
        "ETH-USD": "Ethereum",
        "SOL-USD": "Solana",
        "BNB-USD": "BNB",
        "XRP-USD": "XRP",
    },
    "ดัชนี · ทอง · น้ำมัน": {
        "^GSPC": "S&P 500 Index",
        "^IXIC": "Nasdaq Composite",
        "^DJI":  "Dow Jones",
        "GC=F":  "ทองคำ (Gold Futures)",
        "SI=F":  "เงิน (Silver Futures)",
        "CL=F":  "น้ำมันดิบ (Crude Oil)",
    },
    "Forex": {
        "EURUSD=X": "EUR/USD",
        "GBPUSD=X": "GBP/USD",
        "USDJPY=X": "USD/JPY",
        "USDTHB=X": "USD/THB (เงินบาท)",
    },
}

# รวมทุกกลุ่มเป็น dict เดียวสำหรับ lookup ชื่อ
WATCHLIST = {sym: name for grp in ASSET_GROUPS.values() for sym, name in grp.items()}

FINNHUB_SYMBOL_MAP = {
    # commodities / indices ที่ Finnhub free ไม่รองรับ → None (ใช้ราคาปิดจาก yfinance)
    "GC=F": None, "SI=F": None, "CL=F": None,
    "^GSPC": None, "^IXIC": None, "^DJI": None,
    # crypto → Binance
    "BTC-USD": "BINANCE:BTCUSDT",
    "ETH-USD": "BINANCE:ETHUSDT",
    "SOL-USD": "BINANCE:SOLUSDT",
    "BNB-USD": "BINANCE:BNBUSDT",
    "XRP-USD": "BINANCE:XRPUSDT",
    # forex → OANDA
    "EURUSD=X": "OANDA:EUR_USD",
    "GBPUSD=X": "OANDA:GBP_USD",
    "USDJPY=X": "OANDA:USD_JPY",
    "USDTHB=X": "OANDA:USD_THB",
}

def get_finnhub_symbol(yf_symbol: str) -> str | None:
    if yf_symbol in FINNHUB_SYMBOL_MAP:
        return FINNHUB_SYMBOL_MAP[yf_symbol]
    if "=" not in yf_symbol and "-" not in yf_symbol and "^" not in yf_symbol:
        return yf_symbol   # หุ้น/ETF สหรัฐ → ใช้ ticker ตรง ๆ
    return None

# ─────────────────────────────────────────────────────────────
#  REAL-TIME QUOTE (Finnhub) — เสถียรขึ้น
# ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=2)   # cache 2 วินาที — อัปเดตถี่สำหรับ live ticker
def fetch_realtime_quote(yf_symbol: str) -> dict | None:
    if finnhub_client is None:
        return None
    fh_sym = get_finnhub_symbol(yf_symbol)
    if fh_sym is None:
        return None
    try:
        q = finnhub_client.quote(fh_sym)
        if not q or q.get("c", 0) in (0, None):
            return None
        pc = q.get("pc") or q["c"]
        q["d"]  = q["c"] - pc
        q["dp"] = (q["d"] / pc * 100) if pc else 0
        q["symbol"] = fh_sym
        return q
    except Exception:
        return None

# ─────────────────────────────────────────────────────────────
#  INTRADAY (Real-time จริง) — yfinance 1m/5m/15m/1h
# ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=45, show_spinner=False)
def fetch_intraday(yf_symbol: str, interval: str = "5m", period: str = "5d"):
    """ดึงแท่งราคา intraday จริงของวันนี้/ช่วงล่าสุด (ไม่ใช่การจำลอง)"""
    try:
        d = yf.Ticker(yf_symbol).history(period=period, interval=interval)
        if d is not None and not d.empty and "Close" in d.columns:
            return d.dropna(subset=["Close"])
    except Exception:
        pass
    try:
        d = yf.download(yf_symbol, period=period, interval=interval,
                        progress=False, threads=False)
        if d is not None and not d.empty:
            if isinstance(d.columns, pd.MultiIndex):
                d.columns = d.columns.get_level_values(0)
            return d.dropna(subset=["Close"])
    except Exception:
        pass
    return None

# ─────────────────────────────────────────────────────────────
#  NEWS (Finnhub) — ข่าวบริษัท + ข่าวตลาด/สงคราม/มหภาค
# ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=600, show_spinner=False)
def fetch_company_news(yf_symbol: str, days: int = 21):
    """ข่าวเฉพาะหุ้น/ETF (ต้องเป็น ticker สหรัฐ — คริปโต/forex/ดัชนีจะไม่มี)"""
    if finnhub_client is None:
        return []
    fh = get_finnhub_symbol(yf_symbol)
    if fh is None or ":" in fh:   # crypto/forex mapped → company_news ใช้ไม่ได้
        return []
    try:
        to_d  = dt.date.today()
        frm_d = to_d - dt.timedelta(days=days)
        news = finnhub_client.company_news(fh, _from=frm_d.isoformat(), to=to_d.isoformat())
        news = [n for n in (news or []) if n.get("headline")]
        news.sort(key=lambda n: n.get("datetime", 0), reverse=True)
        return news[:25]
    except Exception:
        return []

@st.cache_data(ttl=900, show_spinner=False)
def fetch_general_news(category: str = "general"):
    """ข่าวตลาด/เศรษฐกิจ/ภูมิรัฐศาสตร์ทั่วไป (รวมสงคราม นโยบาย ฯลฯ)"""
    if finnhub_client is None:
        return []
    try:
        news = finnhub_client.general_news(category) or []
        news = [n for n in news if n.get("headline")]
        news.sort(key=lambda n: n.get("datetime", 0), reverse=True)
        return news[:20]
    except Exception:
        return []

# คำสำคัญสำหรับประเมิน sentiment แบบ heuristic (โปร่งใส ตรวจสอบได้)
_POS_WORDS = ["surge","beat","record","rally","upgrade","growth","profit","gain","soar",
              "strong","boost","jump","outperform","bullish","expansion","win","high",
              "raise","positive","optimis"]
_NEG_WORDS = ["war","conflict","attack","sanction","crash","plunge","fall","drop","loss",
              "downgrade","recession","fear","cut","weak","miss","lawsuit","probe","ban",
              "tariff","inflation","slump","bearish","risk","decline","tension","strike",
              "shortage","default","layoff","slow"]

def news_sentiment(news_items):
    """นับคำบวก/ลบจากพาดหัว+สรุป → คะแนน -100..+100 (heuristic)"""
    if not news_items:
        return 0, 0, 0
    pos = neg = 0
    for n in news_items:
        text = (n.get("headline", "") + " " + n.get("summary", "")).lower()
        pos += sum(text.count(w) for w in _POS_WORDS)
        neg += sum(text.count(w) for w in _NEG_WORDS)
    total = pos + neg
    score = round((pos - neg) / total * 100) if total else 0
    return score, pos, neg

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
    if excess.std() == 0 or np.isnan(excess.std()):
        return 0.0
    return round((excess.mean() / excess.std()) * np.sqrt(252), 3)

def sortino_ratio(returns, rf=0.05):
    rf_daily = rf / 252
    excess = returns - rf_daily
    downside = returns[returns < 0].std()
    if downside == 0 or np.isnan(downside):
        return 0.0
    return round((excess.mean() / downside) * np.sqrt(252), 3)

def max_drawdown(prices):
    roll_max = prices.cummax()
    drawdown = (prices - roll_max) / (roll_max + 1e-9)
    return round(drawdown.min() * 100, 2)

def calmar_ratio(returns, prices):
    if len(prices) == 0:
        return 0.0
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
    r = returns.dropna()
    if len(r) == 0:
        return 0.0
    return round(np.percentile(r, (1 - confidence) * 100) * 100, 3)

def expected_shortfall(returns, confidence=0.95):
    r = returns.dropna()
    if len(r) == 0:
        return 0.0
    var = np.percentile(r, (1 - confidence) * 100)
    tail = r[r <= var]
    if len(tail) == 0:
        return round(var * 100, 3)
    return round(tail.mean() * 100, 3)

# ─────────────────────────────────────────────────────────────
#  FORECAST — Monte Carlo (GBM) + Linear extrapolation  [NEW]
# ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def monte_carlo_forecast(price_list, days=252, n_sims=300, seed=42):
    """
    จำลองเส้นทางราคาในอนาคตด้วย Geometric Brownian Motion + หางอ้วน (Student-t)
    ปรับองศาอิสระ (ν) จาก kurtosis จริงของผลตอบแทน → จำลองวันที่ตลาดร่วงแรง/วิกฤตได้สมจริงกว่า normal
    คืนค่าเปอร์เซ็นไทล์ (5/25/50/75/95) + ตัวอย่างเส้นทาง
    """
    prices = pd.Series(price_list).dropna()
    if len(prices) < 30:
        return None
    returns = prices.pct_change().dropna()
    mu    = returns.mean()
    sigma = returns.std()
    last  = float(prices.iloc[-1])

    # ── ประมาณความอ้วนของหาง (fat tail) จาก excess kurtosis ──
    # Student-t: excess kurtosis = 6/(ν-4) สำหรับ ν>4  →  ν = 4 + 6/exk
    exk = float(returns.kurtosis())   # Fisher excess kurtosis
    if exk > 0.5:
        nu = float(min(max(4.0 + 6.0 / exk, 3.0), 30.0))
    else:
        nu = 30.0                      # หางบาง ≈ normal
    t_scale = np.sqrt((nu - 2.0) / nu) if nu > 2 else 1.0   # ปรับให้ variance = 1

    rng = np.random.default_rng(seed)
    sims = np.zeros((n_sims, days + 1))
    sims[:, 0] = last
    drift = (mu - 0.5 * sigma ** 2)
    for t in range(1, days + 1):
        z = rng.standard_t(nu, size=n_sims) * t_scale   # shock หางอ้วน variance≈1
        sims[:, t] = sims[:, t - 1] * np.exp(drift + sigma * z)

    pct = lambda p: np.percentile(sims, p, axis=0)
    sample_idx = rng.choice(n_sims, size=min(40, n_sims), replace=False)

    final_prices = sims[:, -1]
    return {
        "p5":  pct(5),  "p25": pct(25), "p50": pct(50),
        "p75": pct(75), "p95": pct(95),
        "samples": sims[sample_idx],
        "mu": float(mu), "sigma": float(sigma), "last": last, "days": days,
        "nu": round(nu, 1), "exkurt": round(exk, 2),
        "final_median": float(np.median(final_prices)),
        "final_p5":  float(np.percentile(final_prices, 5)),
        "final_p95": float(np.percentile(final_prices, 95)),
        "prob_up": float((final_prices > last).mean() * 100),
        "exp_return": float((np.median(final_prices) / last - 1) * 100),
    }

def linear_extrapolation(price_list, days=252):
    prices = pd.Series(price_list).dropna()
    if len(prices) < 30:
        return None
    x = np.arange(len(prices), dtype=float)
    y = prices.values.astype(float)
    coeffs = np.polyfit(x, y, 1)
    future_x = np.arange(len(prices), len(prices) + days)
    return np.polyval(coeffs, future_x)

# ─────────────────────────────────────────────────────────────
#  ADVANCED FORECAST — 5 เส้นแนวโน้มที่ดีที่สุด (คณิตศาสตร์ขั้นสูง)
#  Deterministic (ไม่ใช่การสุ่ม) — จัดอันดับด้วย out-of-sample error
# ─────────────────────────────────────────────────────────────
def _m_linear(y, n):
    x = np.arange(len(y)); c = np.polyfit(x, y, 1)
    return np.polyval(c, np.arange(len(y), len(y) + n))

def _m_loglinear(y, n):
    x = np.arange(len(y)); ly = np.log(np.maximum(y, 1e-9))
    c = np.polyfit(x, ly, 1)
    return np.exp(np.polyval(c, np.arange(len(y), len(y) + n)))

def _m_poly2(y, n):
    x = np.arange(len(y)); c = np.polyfit(x, y, 2)
    return np.polyval(c, np.arange(len(y), len(y) + n))

def _m_poly3(y, n):
    x = np.arange(len(y)); c = np.polyfit(x, y, 3)
    return np.polyval(c, np.arange(len(y), len(y) + n))

def _m_theilsen(y, n):
    L = len(y); x = np.arange(L)
    idx = np.unique(np.linspace(0, L - 1, min(L, 160)).astype(int))
    xs, ys = x[idx].astype(float), y[idx]
    sl = []
    for i in range(len(xs)):
        dx = xs[i + 1:] - xs[i]
        dy = ys[i + 1:] - ys[i]
        msk = dx != 0
        sl.extend((dy[msk] / dx[msk]).tolist())
    slope = np.median(sl) if sl else 0.0
    inter = np.median(ys - slope * xs)
    return slope * np.arange(L, L + n) + inter

def _m_holt(y, n, alpha=0.25, beta=0.12):
    level = y[0]; trend = y[1] - y[0]
    for t in range(1, len(y)):
        prev = level
        level = alpha * y[t] + (1 - alpha) * (level + trend)
        trend = beta * (level - prev) + (1 - beta) * trend
    return np.array([level + h * trend for h in range(1, n + 1)])

def _m_holt_damped(y, n, alpha=0.25, beta=0.12, phi=0.97):
    level = y[0]; trend = y[1] - y[0]
    for t in range(1, len(y)):
        prev = level
        level = alpha * y[t] + (1 - alpha) * (level + phi * trend)
        trend = beta * (level - prev) + (1 - beta) * phi * trend
    out, s = [], 0.0
    for h in range(1, n + 1):
        s += phi ** h
        out.append(level + s * trend)
    return np.array(out)

_FORECAST_MODELS = {
    "Linear Regression":       (_m_linear,      "#5b8def"),
    "Log-Linear (Exp Growth)": (_m_loglinear,   "#2ee6a0"),
    "Polynomial (deg-2)":      (_m_poly2,       "#e6c35c"),
    "Polynomial (deg-3)":      (_m_poly3,       "#ff9f43"),
    "Theil-Sen (Robust)":      (_m_theilsen,    "#34e3c4"),
    "Holt Exp Smoothing":      (_m_holt,        "#a877e6"),
    "Holt Damped Trend":       (_m_holt_damped, "#ff5d6c"),
}

@st.cache_data(ttl=300, show_spinner=False)
def advanced_forecast(price_list, horizon=252, top_k=5, test_frac=0.2):
    """
    ฟิตหลายโมเดลคณิตศาสตร์ → วัดความแม่นแบบ out-of-sample (เทรน 80% เทสต์ 20%)
    → จัดอันดับด้วย MAPE → คืน top_k โมเดลที่ดีที่สุด พร้อมเส้นพยากรณ์อนาคต
    """
    y = np.asarray(pd.Series(price_list).dropna(), dtype=float)
    if len(y) < 60:
        return None
    split = int(len(y) * (1 - test_frac))
    y_tr, y_te = y[:split], y[split:]
    last_y = float(y[-1])

    # ── กรอบความผันผวน 3-sigma (diffusion cone) — กันโมเดลเหวี่ยงหลุดจริง ──
    # ขอบกว้างขึ้นตาม sqrt(เวลา) เหมือนความไม่แน่นอนจริง · poly deg-2/3 ที่ระเบิดจะถูกจำกัดที่นี่
    dret = pd.Series(y).pct_change().dropna()
    dsig = float(dret.std()) if len(dret) > 2 and dret.std() > 0 else 0.02
    steps = np.arange(1, horizon + 1)
    cone = 3.0 * dsig * np.sqrt(steps)
    lo_arr = last_y * np.exp(-cone)
    hi_arr = last_y * np.exp(+cone)

    results = []
    for name, (fn, color) in _FORECAST_MODELS.items():
        try:
            pred_te = fn(y_tr, len(y_te))
            if not np.isfinite(pred_te).all():
                continue
            mape = float(np.mean(np.abs((y_te - pred_te) / (y_te + 1e-9))) * 100)
            rmse = float(np.sqrt(np.mean((y_te - pred_te) ** 2)))
            raw_fut = fn(y, horizon)
            if not np.isfinite(raw_fut).all():
                continue
            fut = np.clip(raw_fut, lo_arr, hi_arr)
            # โดนกรอบจำกัดเกิน 10% ของจุด = โมเดลพยายามเหวี่ยงเกินจริง
            clipped = bool(np.mean(np.abs(raw_fut - fut) > 1e-6) > 0.10)
            results.append({
                "name": name, "color": color, "mape": mape, "rmse": rmse,
                "forecast": fut, "end": float(fut[-1]), "clipped": clipped,
                "ret": float((fut[-1] / y[-1] - 1) * 100),
            })
        except Exception:
            continue
    if not results:
        return None
    results.sort(key=lambda r: r["mape"])
    top = results[:top_k]
    # consensus (ค่าเฉลี่ยของ top) — มุมมองรวม
    consensus = np.mean([r["forecast"] for r in top], axis=0)
    return {
        "last": float(y[-1]), "horizon": horizon, "top": top, "all": results,
        "consensus": consensus,
        "consensus_end": float(consensus[-1]),
        "consensus_ret": float((consensus[-1] / y[-1] - 1) * 100),
        "best_name": top[0]["name"], "best_mape": top[0]["mape"],
    }

# ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
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

@st.cache_data(ttl=300, show_spinner=False)
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
    if score >= 75: return "#2ee6a0"
    if score >= 50: return "#e6c35c"
    return "#ff5d6c"

# Plotly dark theme helper — สวยขึ้น (hover, spike, unified)
def dark_layout(fig, height=580, title=None):
    fig.update_layout(
        height=height,
        title=dict(text=title, font=dict(size=15, color="#e9eef7")) if title else None,
        xaxis_rangeslider_visible=False,
        margin=dict(l=10, r=10, t=46, b=10),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Space Grotesk", color="#c3cbd9", size=12),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="rgba(15,20,32,0.95)", bordercolor="rgba(230,195,92,0.4)",
                        font=dict(family="JetBrains Mono", size=11, color="#e9eef7")),
        legend=dict(bgcolor="rgba(20,26,40,0.7)", bordercolor="rgba(255,255,255,0.1)",
                    borderwidth=1, font=dict(size=11, color="#c3cbd9"),
                    orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        transition=dict(duration=400, easing="cubic-in-out"),
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.08)",
                     linecolor="rgba(255,255,255,0.12)", showspikes=True,
                     spikecolor="rgba(230,195,92,0.4)", spikethickness=1, spikemode="across", spikedash="dot")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.08)",
                     linecolor="rgba(255,255,255,0.12)")
    return fig

# ─────────────────────────────────────────────────────────────
#  FETCH DATA (historical) — yfinance + Stooq fallback (เสถียร)
# ─────────────────────────────────────────────────────────────
def _from_yfinance(symbol, period):
    try:
        d = yf.Ticker(symbol).history(period=period, auto_adjust=True)
        if d is not None and not d.empty:
            return d
    except Exception:
        pass
    try:
        d = yf.download(symbol, period=period, auto_adjust=True,
                        progress=False, threads=False)
        if d is not None and not d.empty:
            if isinstance(d.columns, pd.MultiIndex):
                d.columns = d.columns.get_level_values(0)
            return d
    except Exception:
        pass
    return None

def _stooq_symbol(yf_sym: str) -> str | None:
    m = {
        "BTC-USD": "btcusd", "^GSPC": "^spx", "GC=F": "xauusd",
        "EURUSD=X": "eurusd", "GBPUSD=X": "gbpusd", "USDJPY=X": "usdjpy",
    }
    if yf_sym in m:
        return m[yf_sym]
    if all(c not in yf_sym for c in ["=", "-", "^"]):
        return f"{yf_sym.lower()}.us"
    return None

def _from_stooq(symbol):
    s = _stooq_symbol(symbol)
    if not s:
        return None
    try:
        url = f"https://stooq.com/q/d/l/?s={s}&i=d"
        d = pd.read_csv(url)
        if d is None or d.empty or "Close" not in d.columns:
            return None
        d["Date"] = pd.to_datetime(d["Date"])
        d = d.set_index("Date").sort_index()
        return d if len(d) >= 100 else None
    except Exception:
        return None

@st.cache_data(ttl=300, show_spinner=False)
def fetch_data(symbol, period="10y"):
    # ลอง yfinance ก่อน (พร้อม retry เบา ๆ)
    for _ in range(2):
        d = _from_yfinance(symbol, period)
        if d is not None and len(d) >= 100:
            return d
        time.sleep(0.4)
    # fallback: Stooq
    d = _from_stooq(symbol)
    if d is not None and len(d) >= 100:
        return d
    return None

@st.cache_data(ttl=60, show_spinner=False)
def fetch_watchlist_scores(symbols=None):
    syms = symbols if symbols is not None else list(WATCHLIST.keys())
    results = []
    for sym in syms:
        name = WATCHLIST.get(sym, sym)
        df = fetch_data(sym)
        if df is None or len(df) < 252:
            continue
        try:
            mm = full_math_analysis(df, sym)
            bt2 = winrate_backtest(df)
            n_items = fetch_company_news(sym, days=14)
            n_sent, _n_pos, _n_neg = news_sentiment(n_items)
            results.append({
                "sym": sym, "name": name,
                "score": mm["score"], "verdict": mm["verdict"],
                "cagr": mm["cagr"], "sharpe": mm["sharpe"],
                "mdd": mm["mdd"], "winrate": bt2["winrate"],
                "momentum": mm["momentum"], "vol": mm["vol_l"],
                "cur": mm["cur"],
                "news_sent": n_sent, "news_count": len(n_items),
            })
        except Exception:
            continue
    return sorted(results, key=lambda x: x["score"], reverse=True)

# ─────────────────────────────────────────────────────────────
#  FUNDAMENTALS (Finnhub) — ปัจจัยพื้นฐาน
# ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_fundamentals(yf_symbol):
    """ดึงปัจจัยพื้นฐานจาก Finnhub (P/E, EPS, margin, ปันผล ฯลฯ) — เฉพาะหุ้น/ETF สหรัฐ"""
    if finnhub_client is None:
        return None
    fh = get_finnhub_symbol(yf_symbol)
    if fh is None or ":" in fh:   # crypto/forex/index/commodity → ไม่มีพื้นฐาน
        return None
    try:
        prof = finnhub_client.company_profile2(symbol=fh) or {}
        bf   = finnhub_client.company_basic_financials(fh, "all") or {}
        me   = (bf.get("metric") or {})
        g = lambda *keys: next((me[k] for k in keys if me.get(k) is not None), None)
        return {
            "name":         prof.get("name"),
            "industry":     prof.get("finnhubIndustry"),
            "exchange":     prof.get("exchange"),
            "currency":     prof.get("currency"),
            "market_cap":   prof.get("marketCapitalization"),   # ล้าน USD
            "pe":           g("peTTM", "peBasicExclExtraTTM", "peAnnual"),
            "pb":           g("pbQuarterly", "pbAnnual"),
            "ps":           g("psTTM", "psAnnual"),
            "eps":          g("epsTTM", "epsBasicExclExtraItemsTTM", "epsAnnual"),
            "roe":          g("roeTTM", "roeAnnual"),
            "roa":          g("roaTTM", "roaAnnual"),
            "gross_margin": g("grossMarginTTM", "grossMarginAnnual"),
            "net_margin":   g("netProfitMarginTTM", "netProfitMarginAnnual"),
            "debt_equity":  g("totalDebt/totalEquityQuarterly", "totalDebt/totalEquityAnnual",
                              "longTermDebt/equityQuarterly"),
            "current_ratio":g("currentRatioQuarterly", "currentRatioAnnual"),
            "div_yield":    g("dividendYieldIndicatedAnnual", "currentDividendYieldTTM"),
            "rev_growth":   g("revenueGrowthTTMYoy", "revenueGrowthQuarterlyYoy"),
            "eps_growth":   g("epsGrowthTTMYoy", "epsGrowthQuarterlyYoy"),
            "wk52_high":    g("52WeekHigh"),
            "wk52_low":     g("52WeekLow"),
            "beta_fh":      g("beta"),
        }
    except Exception:
        return None

# ─────────────────────────────────────────────────────────────
#  BETA / ALPHA vs BENCHMARK (เทียบดัชนีอ้างอิง เช่น S&P 500)
# ─────────────────────────────────────────────────────────────
def _naive_index(series):
    idx = pd.to_datetime(series.index)
    try:
        if idx.tz is not None:
            idx = idx.tz_localize(None)
    except (TypeError, AttributeError):
        pass
    return pd.Series(series.values, index=idx)

@st.cache_data(ttl=300, show_spinner=False)
def beta_alpha_vs_benchmark(yf_symbol, bench="^GSPC", rf=0.05):
    """คำนวณ Beta, Alpha (annualized %), correlation เทียบดัชนีอ้างอิง"""
    if yf_symbol == bench:
        return None
    asset_df = fetch_data(yf_symbol)
    bench_df = fetch_data(bench)
    if asset_df is None or bench_df is None:
        return None
    a = _naive_index(asset_df["Close"].pct_change().dropna())
    b = _naive_index(bench_df["Close"].pct_change().dropna())
    df = pd.concat([a, b], axis=1, keys=["a", "b"]).dropna()
    if len(df) < 60:
        return None
    cov = np.cov(df["a"].values, df["b"].values)
    var_b = cov[1, 1]
    if var_b <= 0:
        return None
    beta = cov[0, 1] / var_b
    rf_d = rf / 252
    alpha_d = (df["a"].mean() - rf_d) - beta * (df["b"].mean() - rf_d)
    alpha_ann = alpha_d * 252 * 100
    corr = float(df["a"].corr(df["b"]))
    # ผลตอบแทนช่วงเดียวกัน (เทียบ benchmark) ปีล่าสุด
    n1y = min(252, len(df))
    asset_1y = float((1 + df["a"].tail(n1y)).prod() - 1) * 100
    bench_1y = float((1 + df["b"].tail(n1y)).prod() - 1) * 100
    return {
        "beta": round(float(beta), 3),
        "alpha": round(float(alpha_ann), 2),
        "corr": round(corr, 3),
        "r2": round(corr ** 2, 3),
        "asset_1y": round(asset_1y, 1),
        "bench_1y": round(bench_1y, 1),
        "excess_1y": round(asset_1y - bench_1y, 1),
    }

# ─────────────────────────────────────────────────────────────
#  PORTFOLIO — correlation + efficient frontier (Markowitz, numpy)
# ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def portfolio_returns_frame(symbols):
    """รวมผลตอบแทนรายวันของหลายสินทรัพย์ จัดแนวตามวันที่ตรงกัน"""
    series = {}
    for s in symbols:
        d = fetch_data(s)
        if d is None or len(d) < 252:
            continue
        series[s] = _naive_index(d["Close"].pct_change().dropna())
    if len(series) < 2:
        return None
    df = pd.DataFrame(series).dropna()
    return df if len(df) >= 60 else None

@st.cache_data(ttl=300, show_spinner=False)
def efficient_frontier(symbols, n_port=4000, rf=0.05, seed=42):
    """สุ่มพอร์ตหลายพันแบบ → คืนจุด risk/return + พอร์ต Max-Sharpe และ Min-Vol"""
    rdf = portfolio_returns_frame(symbols)
    if rdf is None:
        return None
    cols = list(rdf.columns)
    mean = rdf.mean().values * 252
    cov = rdf.cov().values * 252
    n = len(cols)
    rng = np.random.default_rng(seed)
    W = rng.random((n_port, n))
    W = W / W.sum(axis=1, keepdims=True)
    rets = W @ mean
    vols = np.sqrt(np.einsum("ij,jk,ik->i", W, cov, W))
    sharpes = (rets - rf) / (vols + 1e-12)
    i_sharpe = int(np.argmax(sharpes))
    i_minvol = int(np.argmin(vols))
    pack = lambda i: {
        "ret": round(float(rets[i] * 100), 2),
        "vol": round(float(vols[i] * 100), 2),
        "sharpe": round(float(sharpes[i]), 3),
        "weights": {cols[j]: round(float(W[i, j] * 100), 1) for j in range(n)},
    }
    # correlation matrix
    corr = rdf.corr()
    return {
        "cols": cols,
        "rets": (rets * 100).tolist(),
        "vols": (vols * 100).tolist(),
        "sharpes": sharpes.tolist(),
        "max_sharpe": pack(i_sharpe),
        "min_vol": pack(i_minvol),
        "corr": corr.values.tolist(),
        "n_days": len(rdf),
    }

# ─────────────────────────────────────────────────────────────
#  STRATEGY vs BUY-AND-HOLD (เทียบกลยุทธ์กับการถือยาว สุทธิหลังค่าธรรมเนียม)
# ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def strategy_vs_buyhold(df, fee=0.001):
    """กลยุทธ์ MA20>MA50 = ถือ, ไม่งั้นถือเงินสด · หักค่าธรรมเนียมทุกครั้งที่สลับสถานะ"""
    d = df.copy()
    d["MA20"] = d["Close"].rolling(20).mean()
    d["MA50"] = d["Close"].rolling(50).mean()
    d = d.dropna(subset=["MA20", "MA50", "Close"])
    if len(d) < 60:
        return None
    ret = d["Close"].pct_change().fillna(0.0)
    signal = (d["MA20"] > d["MA50"]).astype(int).shift(1).fillna(0.0)   # เข้าตลาดวันถัดไป
    switches = signal.diff().abs().fillna(0.0)
    strat_ret = signal * ret - switches * fee
    strat_eq = (1 + strat_ret).cumprod()
    bh_eq = (1 + ret).cumprod()

    def _metrics(eq, r):
        yrs = len(eq) / 252
        cagr_v = (eq.iloc[-1] ** (1 / yrs) - 1) * 100 if yrs > 0 else 0.0
        sh = (r.mean() / (r.std() + 1e-12)) * np.sqrt(252) if r.std() > 0 else 0.0
        mdd = ((eq - eq.cummax()) / eq.cummax()).min() * 100
        return round(float(cagr_v), 1), round(float(sh), 2), round(float(mdd), 1)

    s_cagr, s_sh, s_mdd = _metrics(strat_eq, strat_ret)
    b_cagr, b_sh, b_mdd = _metrics(bh_eq, ret)
    n_trades = int(switches.sum())
    return {
        "index": list(d.index),
        "strat_eq": strat_eq.tolist(), "bh_eq": bh_eq.tolist(),
        "s_cagr": s_cagr, "s_sharpe": s_sh, "s_mdd": s_mdd,
        "b_cagr": b_cagr, "b_sharpe": b_sh, "b_mdd": b_mdd,
        "n_trades": n_trades,
        "strat_final": round(float(strat_eq.iloc[-1]), 2),
        "bh_final": round(float(bh_eq.iloc[-1]), 2),
        "beats": bool(strat_eq.iloc[-1] > bh_eq.iloc[-1]),
    }

# ─────────────────────────────────────────────────────────────
#  USD/THB rate (สำหรับมุมนักลงทุนไทย) — ค่าเริ่มต้นถ้าดึงไม่ได้
# ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=900, show_spinner=False)
def fetch_usdthb():
    q = fetch_realtime_quote("USDTHB=X")
    if q and q.get("c", 0) > 0:
        return float(q["c"])
    d = fetch_data("USDTHB=X")
    if d is not None and len(d):
        return float(d["Close"].iloc[-1])
    return 36.0

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
#  FETCH: Historical + Real-time
# ─────────────────────────────────────────────────────────────
with st.spinner("กำลังดึงข้อมูลย้อนหลัง..."):
    data = fetch_data(symbol)

is_fx = "=X" in symbol or symbol in ["EURUSD=X", "GBPUSD=X", "USDJPY=X"]

if data is None or len(data) < 100:
    st.error(
        f"⚠️ ดึงข้อมูล **{symbol}** ไม่สำเร็จ (ทั้ง yfinance และ Stooq)\n\n"
        "สาเหตุที่พบบ่อย: Yahoo Finance จำกัด/บล็อก IP ของ Streamlit Cloud ชั่วคราว "
        "(rate limit) — มักหายเองใน 1-2 นาที"
    )
    cretry, _ = st.columns([1, 3])
    with cretry:
        if st.button("🔄 ลองใหม่"):
            fetch_data.clear()
            st.rerun()
    st.caption("ถ้าลองหลายครั้งแล้วยังไม่ได้ ลองเปลี่ยน symbol อื่น หรือรอสักครู่แล้วรีเฟรช")
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
#  REAL-TIME PANEL + LIVE INTRADAY CHART (ข้อมูลจริง) — อัปเดตทุก 3 วินาที
# ─────────────────────────────────────────────────────────────
# ตัวเลือกช่วง/สไตล์กราฟ real-time (อยู่นอก fragment เพื่อไม่ให้รีเซ็ตทุกวินาที)
if get_finnhub_symbol(symbol) is not None or not is_fx:
    iv_col1, iv_col2 = st.columns([3, 1])
    with iv_col1:
        _iv_label = st.radio(
            "ช่วงกราฟ Real-time",
            ["1 นาที · วันนี้", "5 นาที · 5 วัน", "15 นาที · 5 วัน", "1 ชม. · 1 เดือน"],
            horizontal=True, label_visibility="collapsed", key="rt_interval_radio")
    with iv_col2:
        _rt_style = st.radio("สไตล์", ["เส้น", "แท่งเทียน"],
                             horizontal=True, label_visibility="collapsed", key="rt_style_radio")
    _IV_MAP = {
        "1 นาที · วันนี้":  ("1m", "1d"),
        "5 นาที · 5 วัน":   ("5m", "5d"),
        "15 นาที · 5 วัน":  ("15m", "5d"),
        "1 ชม. · 1 เดือน":  ("60m", "1mo"),
    }
    _RT_INTERVAL, _RT_PERIOD = _IV_MAP[_iv_label]
else:
    _RT_INTERVAL, _RT_PERIOD, _rt_style = "5m", "5d", "เส้น"


@st.fragment(run_every=3)
def realtime_panel():
    q = fetch_realtime_quote(symbol)
    if not q or q.get("c", 0) == 0:
        st.caption("⏳ กำลังรอข้อมูล real-time...")
        return

    chg       = q["d"]
    chgp      = q["dp"]
    chg_cls   = "pos" if chg >= 0 else "neg"
    chg_arrow = "▲" if chg >= 0 else "▼"
    ts        = time.strftime("%H:%M:%S")
    st.markdown(f"""
    <div class="rt-panel">
      <div class="rt-item">
        <div class="rt-item-label">REAL-TIME</div>
        <div class="rt-item-val gold">{fmt_p(q['c'])}</div>
      </div>
      <div class="rt-item">
        <div class="rt-item-label">เปลี่ยนแปลง</div>
        <div class="rt-item-val {chg_cls}">{chg_arrow} {chg:+.2f} ({chgp:+.2f}%)</div>
      </div>
      <div class="rt-item">
        <div class="rt-item-label">HIGH วันนี้</div>
        <div class="rt-item-val">{fmt_p(q['h'])}</div>
      </div>
      <div class="rt-item">
        <div class="rt-item-label">LOW วันนี้</div>
        <div class="rt-item-val">{fmt_p(q['l'])}</div>
      </div>
      <div class="rt-item">
        <div class="rt-item-label">เปิด (OPEN)</div>
        <div class="rt-item-val">{fmt_p(q['o'])}</div>
      </div>
      <div class="rt-item">
        <div class="rt-item-label">ปิดก่อนหน้า</div>
        <div class="rt-item-val">{fmt_p(q['pc'])}</div>
      </div>
      <div class="rt-item">
        <div class="rt-item-label">อัปเดตล่าสุด</div>
        <div class="rt-item-val" style="font-size:12px">
          <span class="rt-badge"><span class="rt-dot"></span>LIVE {ts}</span>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── กราฟ intraday จริง (yfinance) + จุดราคา live ล่าสุด (Finnhub) ──
    intra = fetch_intraday(symbol, interval=_RT_INTERVAL, period=_RT_PERIOD)
    if intra is None or intra.empty or len(intra) < 2:
        st.caption("⏳ กำลังโหลดกราฟ intraday จริง... (บางสินทรัพย์อาจไม่มีข้อมูลรายนาที)")
        return

    closes = intra["Close"]
    up = closes.iloc[-1] >= closes.iloc[0]
    line_c = "#2ee6a0" if up else "#ff5d6c"
    fill_c = "rgba(46,230,160,0.10)" if up else "rgba(255,93,108,0.09)"

    fig_live = go.Figure()
    if _rt_style == "แท่งเทียน" and {"Open", "High", "Low"}.issubset(intra.columns):
        fig_live.add_trace(go.Candlestick(
            x=intra.index, open=intra["Open"], high=intra["High"],
            low=intra["Low"], close=intra["Close"], name="ราคา",
            increasing_line_color="#2ee6a0", decreasing_line_color="#ff5d6c",
            increasing_fillcolor="rgba(46,230,160,0.6)",
            decreasing_fillcolor="rgba(255,93,108,0.6)",
        ))
    else:
        fig_live.add_trace(go.Scatter(
            x=intra.index, y=closes, mode="lines", name="ราคา",
            line=dict(color=line_c, width=2, shape="spline"),
            fill="tozeroy", fillcolor=fill_c,
        ))
    # จุด live ล่าสุดจาก Finnhub (real-time กว่า bar)
    fig_live.add_trace(go.Scatter(
        x=[intra.index[-1]], y=[q["c"]], mode="markers",
        marker=dict(size=11, color="#e6c35c", line=dict(color="#fff", width=1.5)),
        name="Live", showlegend=False,
    ))
    fig_live.add_hline(y=q["c"], line_color="#e6c35c", line_dash="dot", line_width=1,
                       annotation_text=f"Live {fmt_p(q['c'])}", annotation_font_color="#e6c35c",
                       annotation_position="left")
    if q.get("pc"):
        fig_live.add_hline(y=q["pc"], line_color="rgba(255,255,255,0.25)",
                           line_dash="dash", line_width=1)
    fig_live.update_layout(
        height=260, margin=dict(l=8, r=8, t=8, b=8),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False, xaxis_rangeslider_visible=False,
        font=dict(family="JetBrains Mono", color="#c3cbd9", size=10),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="rgba(15,20,32,0.95)", bordercolor="rgba(230,195,92,0.4)",
                        font=dict(family="JetBrains Mono", size=10, color="#e9eef7")),
    )
    fig_live.update_xaxes(showgrid=False, nticks=8)
    fig_live.update_yaxes(showgrid=False, side="right", gridcolor="rgba(255,255,255,0.04)")
    st.plotly_chart(fig_live, use_container_width=True,
                    config={"displayModeBar": False}, key=f"live_chart_{symbol}")
    st.caption(f"📡 กราฟ Real-time จริง · {_RT_INTERVAL} bars จาก yfinance ({len(intra)} แท่ง) · "
               f"จุดทอง = ราคา live ล่าสุดจาก Finnhub · เส้นประขาว = ราคาปิดก่อนหน้า")

# แสดงแผง live (Finnhub) หรืออย่างน้อยกราฟ intraday (yfinance) สำหรับหุ้น/ETF
if get_finnhub_symbol(symbol) is not None:
    realtime_panel()
else:
    # สินทรัพย์ที่ Finnhub free ไม่รองรับ → ยังโชว์กราฟ intraday จริงจาก yfinance ได้
    _intra0 = fetch_intraday(symbol, interval=_RT_INTERVAL, period=_RT_PERIOD)
    if _intra0 is not None and not _intra0.empty and len(_intra0) >= 2:
        _cl = _intra0["Close"]; _up = _cl.iloc[-1] >= _cl.iloc[0]
        _lc = "#2ee6a0" if _up else "#ff5d6c"
        _fig0 = go.Figure()
        _fig0.add_trace(go.Scatter(x=_intra0.index, y=_cl, mode="lines",
            line=dict(color=_lc, width=2, shape="spline"),
            fill="tozeroy", fillcolor=("rgba(46,230,160,0.10)" if _up else "rgba(255,93,108,0.09)")))
        _fig0.update_layout(height=240, margin=dict(l=8, r=8, t=8, b=8),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", showlegend=False,
            font=dict(family="JetBrains Mono", color="#c3cbd9", size=10))
        _fig0.update_xaxes(showgrid=False); _fig0.update_yaxes(showgrid=False, side="right")
        st.plotly_chart(_fig0, use_container_width=True, config={"displayModeBar": False},
                        key=f"intra0_{symbol}")
        st.caption(f"📊 กราฟ intraday จริง · {_RT_INTERVAL} bars จาก yfinance "
                   "(Finnhub free ไม่รองรับ live สำหรับสินทรัพย์นี้)")

# ─────────────────────────────────────────────────────────────
#  COMPUTE Math Analysis
# ─────────────────────────────────────────────────────────────
with st.spinner("กำลังวิเคราะห์คณิตศาสตร์..."):
    m   = full_math_analysis(data, symbol)
    bt  = winrate_backtest(data)

# ─────────────────────────────────────────────────────────────
#  TABS
# ─────────────────────────────────────────────────────────────
(tab_overview, tab_fund, tab_chart, tab_forecast, tab_news,
 tab_rank, tab_portfolio, tab_income, tab_chat) = st.tabs([
    "📐 ภาพรวมคณิตศาสตร์",
    "🏛️ ปัจจัยพื้นฐาน",
    "📈 กราฟวิเคราะห์",
    "🔮 พยากรณ์อนาคต",
    "📰 ข่าว & อนาคต",
    "🏆 อันดับสินทรัพย์",
    "🧺 พอร์ต & กระจายเสี่ยง",
    "💰 คำนวณรายได้",
    "🤖 AI ที่ปรึกษา",
])

# ══════════════════════════════════════════════════════════════
#  TAB 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════
with tab_overview:
    col_left, col_right = st.columns([3, 2])

    with col_left:
        sc = m["score"]
        verdict_emoji = {"Strong Buy":"🚀","Buy":"📈","Hold/Watch":"⏳","Underweight":"⚠️","Avoid":"🚫"}
        ring_c = score_color(sc)
        # SVG circular gauge (animated)
        R = 52
        circ = 2 * np.pi * R
        dash_target = circ * (1 - sc / 100)
        st.markdown(f"""
        <div class="score-ring">
          <div class="gauge-wrap">
            <svg class="gauge-svg" width="120" height="120" viewBox="0 0 120 120"
                 style="--circ:{circ:.1f};">
              <circle class="gauge-track" cx="60" cy="60" r="{R}"></circle>
              <circle class="gauge-prog" cx="60" cy="60" r="{R}"
                      stroke="{ring_c}"
                      style="--dash-full:{circ:.1f}; --dash-target:{dash_target:.1f}; color:{ring_c};">
              </circle>
            </svg>
            <div class="gauge-center">
              <div class="gauge-num">{sc}</div>
              <div class="gauge-max">/ 100</div>
            </div>
          </div>
          <div>
            <div class="score-label">COMPOSITE SCORE</div>
            <div class="score-verdict">{verdict_emoji.get(m['verdict'],'')} {m['verdict']}</div>
            <div style="font-size:12px;color:#9aa6b8;margin-top:8px">Win Rate Backtest:
              <b style="color:{ring_c}">{bt['winrate']}%</b>
              ({bt['wins']}W / {bt['losses']}L)</div>
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
        for idx, (icon, label, detail, _) in enumerate(m["signals"]):
            st.markdown(f"""
            <div class="sig-row" style="animation-delay:{idx*0.05:.2f}s">
              <div class="sig-icon">{icon}</div>
              <div class="sig-text"><strong>{label}</strong></div>
              <div class="sig-badge">{detail}</div>
            </div>
            """, unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="section-title">📊 ตัวเลขสำคัญ</div>', unsafe_allow_html=True)

        _delay = {"i": 0}
        def mcard(label, value, sub="", cls=""):
            d = _delay["i"] * 0.04
            _delay["i"] += 1
            st.markdown(f"""
            <div class="mcard {cls}" style="margin-bottom:10px;animation-delay:{d:.2f}s">
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

        # ── Beta / Alpha เทียบ S&P 500 ──
        ba = beta_alpha_vs_benchmark(symbol, bench="^GSPC")
        if ba:
            mcard("BETA (เทียบ S&P 500)", f"{ba['beta']:.2f}",
                  ">1 = ผันผวนกว่าตลาด · <1 = นิ่งกว่าตลาด",
                  "neg" if ba['beta'] > 1.3 else "pos")
            mcard("ALPHA (ส่วนเกินตลาด/ปี)", f"{ba['alpha']:+.1f}%",
                  f"Correlation {ba['corr']:.2f} · R²={ba['r2']:.2f}",
                  "pos" if ba['alpha'] > 0 else "neg")
            mcard("ชนะ/แพ้ตลาด (1 ปี)", f"{ba['excess_1y']:+.1f}%",
                  f"{symbol} {ba['asset_1y']:+.1f}% vs S&P {ba['bench_1y']:+.1f}%",
                  "pos" if ba['excess_1y'] >= 0 else "neg")

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
#  TAB — FUNDAMENTALS (ปัจจัยพื้นฐาน)
# ══════════════════════════════════════════════════════════════
with tab_fund:
    st.markdown('<div class="section-title">🏛️ ปัจจัยพื้นฐาน (Fundamentals)</div>',
                unsafe_allow_html=True)
    st.caption("ข้อมูลพื้นฐานจาก Finnhub — P/E, EPS, อัตรากำไร, ปันผล, หนี้สิน ฯลฯ "
               "(มีเฉพาะหุ้น/ETF สหรัฐ · คริปโต/forex/ดัชนี/ทองคำ จะไม่มี)")

    with st.spinner("กำลังดึงปัจจัยพื้นฐาน..."):
        fund = fetch_fundamentals(symbol)

    if not fund:
        st.info(f"ไม่มีข้อมูลปัจจัยพื้นฐานสำหรับ {symbol} — "
                "ลองหุ้น/ETF สหรัฐ เช่น AAPL, NVDA, MSFT (คริปโต/forex/ดัชนี/ทองคำ ไม่มีงบการเงิน)")
    else:
        head = f"{fund['name'] or symbol}"
        sub = " · ".join([x for x in [fund.get("industry"), fund.get("exchange")] if x])
        st.markdown(f"""<div class="fc-banner"><b>{head}</b>
          <span style="color:var(--muted);font-size:12px"> &nbsp; {sub}</span></div>""",
          unsafe_allow_html=True)

        def fcard(label, value, sub="", cls=""):
            st.markdown(f"""<div class="mcard {cls}" style="margin-bottom:10px">
              <div class="mcard-label">{label}</div>
              <div class="mcard-value">{value}</div>
              {'<div class="mcard-sub">'+sub+'</div>' if sub else ''}
            </div>""", unsafe_allow_html=True)

        def fnum(v, suf="", dec=2):
            return f"{v:,.{dec}f}{suf}" if isinstance(v, (int, float)) else "—"

        fc_a, fc_b, fc_c = st.columns(3)
        with fc_a:
            st.markdown('<div class="section-title" style="font-size:16px">💵 มูลค่า (Valuation)</div>',
                        unsafe_allow_html=True)
            mc = fund.get("market_cap")
            mc_str = f"${mc/1000:,.1f}B" if isinstance(mc, (int, float)) and mc else "—"
            fcard("MARKET CAP", mc_str, "มูลค่าตลาดรวม")
            pe = fund.get("pe")
            fcard("P/E (TTM)", fnum(pe), "ราคา/กำไร · ต่ำ=ถูก สูง=คาดโตสูง",
                  "neg" if isinstance(pe,(int,float)) and pe > 40 else "pos" if isinstance(pe,(int,float)) and 0 < pe < 20 else "")
            fcard("P/B", fnum(fund.get("pb")), "ราคา/มูลค่าทางบัญชี")
            fcard("P/S", fnum(fund.get("ps")), "ราคา/ยอดขาย")
        with fc_b:
            st.markdown('<div class="section-title" style="font-size:16px">📈 กำไร (Profitability)</div>',
                        unsafe_allow_html=True)
            fcard("EPS (TTM)", f"${fnum(fund.get('eps'))}" if isinstance(fund.get('eps'),(int,float)) else "—",
                  "กำไรต่อหุ้น")
            roe = fund.get("roe")
            fcard("ROE", fnum(roe, "%"), "ผลตอบแทนต่อส่วนผู้ถือหุ้น",
                  "pos" if isinstance(roe,(int,float)) and roe > 15 else "")
            fcard("GROSS MARGIN", fnum(fund.get("gross_margin"), "%"), "อัตรากำไรขั้นต้น")
            nm = fund.get("net_margin")
            fcard("NET MARGIN", fnum(nm, "%"), "อัตรากำไรสุทธิ",
                  "pos" if isinstance(nm,(int,float)) and nm > 15 else "")
        with fc_c:
            st.markdown('<div class="section-title" style="font-size:16px">🏦 สุขภาพ & เติบโต</div>',
                        unsafe_allow_html=True)
            de = fund.get("debt_equity")
            fcard("D/E (หนี้สิน/ทุน)", fnum(de), "ต่ำ = หนี้น้อย",
                  "neg" if isinstance(de,(int,float)) and de > 2 else "pos" if isinstance(de,(int,float)) and de < 1 else "")
            dv = fund.get("div_yield")
            fcard("DIVIDEND YIELD", fnum(dv, "%"), "ผลตอบแทนปันผล/ปี",
                  "pos" if isinstance(dv,(int,float)) and dv > 2 else "")
            rg = fund.get("rev_growth")
            fcard("รายได้โต (YoY)", fnum(rg, "%"), "การเติบโตของยอดขาย",
                  "pos" if isinstance(rg,(int,float)) and rg > 0 else "neg" if isinstance(rg,(int,float)) else "")
            eg = fund.get("eps_growth")
            fcard("กำไรโต (YoY)", fnum(eg, "%"), "การเติบโตของ EPS",
                  "pos" if isinstance(eg,(int,float)) and eg > 0 else "neg" if isinstance(eg,(int,float)) else "")

        st.info("📌 ปัจจัยพื้นฐานสะท้อน 'มูลค่ากิจการ' ส่วนแท็บอื่นวิเคราะห์ 'พฤติกรรมราคา' — "
                "นักลงทุนระยะยาวควรดูทั้งสองด้านประกอบกัน · ข้อมูลพื้นฐานอัปเดตช้ากว่าราคา (ตามรอบงบการเงิน)")


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
        # Bollinger band fill first (so candles overlay)
        fig.add_trace(go.Scatter(
            x=df_c.index, y=df_c["BB_up"], name="BB Upper",
            line=dict(color="rgba(91,141,239,0.4)", width=1), fill=None, showlegend=False
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df_c.index, y=df_c["BB_dn"], name="BB Band",
            fill='tonexty', fillcolor='rgba(91,141,239,0.07)',
            line=dict(color="rgba(91,141,239,0.4)", width=1), showlegend=False
        ), row=1, col=1)
        fig.add_trace(go.Candlestick(
            x=df_c.index, open=df_c["Open"], high=df_c["High"],
            low=df_c["Low"], close=df_c["Close"], name="Price",
            increasing_line_color="#2ee6a0", decreasing_line_color="#ff5d6c",
            increasing_fillcolor="rgba(46,230,160,0.55)", decreasing_fillcolor="rgba(255,93,108,0.55)"
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
            x=df_c.index, y=df_c["BB_up"], name="BB+2σ",
            line=dict(color="#e6c35c", width=1, dash="dash"), fill=None
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df_c.index, y=df_c["BB_dn"], name="BB-2σ",
            fill='tonexty', fillcolor='rgba(230,195,92,0.07)',
            line=dict(color="#e6c35c", width=1, dash="dash")
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df_c.index, y=df_c["Close"], mode="lines",
            name="ราคา", line=dict(color="#5b8def", width=2.2, shape="spline"),
            fill="tozeroy", fillcolor="rgba(91,141,239,0.06)"
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

    # ── กลยุทธ์ vs ถือยาว (Buy & Hold) สุทธิหลังค่าธรรมเนียม ──
    st.markdown('<div class="section-title" style="margin-top:18px">⚔️ กลยุทธ์ vs ถือยาว (Buy & Hold)</div>',
                unsafe_allow_html=True)
    fee_bps = st.select_slider("ค่าธรรมเนียมต่อการสลับสถานะ",
                               options=[0.0, 0.05, 0.1, 0.25, 0.5],
                               value=0.1, format_func=lambda x: f"{x:.2f}%", key="bt_fee")
    sb = strategy_vs_buyhold(m["df"], fee=fee_bps / 100)
    if sb is None:
        st.caption("ข้อมูลไม่พอสำหรับเปรียบเทียบกลยุทธ์")
    else:
        fig_sb = go.Figure()
        fig_sb.add_trace(go.Scatter(x=sb["index"], y=sb["bh_eq"], mode="lines",
            name="ถือยาว (Buy & Hold)", line=dict(color="#5b8def", width=2)))
        fig_sb.add_trace(go.Scatter(x=sb["index"], y=sb["strat_eq"], mode="lines",
            name="กลยุทธ์ MA20>MA50", line=dict(color="#e6c35c", width=2)))
        dark_layout(fig_sb, height=340,
                    title="Equity Curve — เริ่มต้นที่ 1.0 (เท่ากับลงทุนเท่ากัน)")
        st.plotly_chart(fig_sb, use_container_width=True, config={"displayModeBar": False})

        verdict_sb = ("✅ กลยุทธ์ชนะการถือยาว" if sb["beats"]
                      else "❌ กลยุทธ์แพ้การถือยาว (ถือเฉย ๆ ดีกว่า)")
        v_col = "#2ee6a0" if sb["beats"] else "#ff5d6c"
        st.markdown(f"""
        <table class="rank-table">
          <thead><tr><th>วิธี</th><th>เงินเป็น (x เท่า)</th><th>CAGR</th><th>SHARPE</th><th>MAX DD</th></tr></thead>
          <tbody>
            <tr><td><b>ถือยาว (Buy &amp; Hold)</b></td>
              <td style="font-family:'JetBrains Mono',monospace">{sb['bh_final']:.2f}x</td>
              <td style="font-family:'JetBrains Mono',monospace">{sb['b_cagr']:+.1f}%</td>
              <td style="font-family:'JetBrains Mono',monospace">{sb['b_sharpe']:.2f}</td>
              <td style="font-family:'JetBrains Mono',monospace;color:#ff5d6c">{sb['b_mdd']:.1f}%</td></tr>
            <tr><td><b>กลยุทธ์ MA Cross</b> <span style="color:var(--muted);font-size:11px">({sb['n_trades']} ครั้งเทรด)</span></td>
              <td style="font-family:'JetBrains Mono',monospace">{sb['strat_final']:.2f}x</td>
              <td style="font-family:'JetBrains Mono',monospace">{sb['s_cagr']:+.1f}%</td>
              <td style="font-family:'JetBrains Mono',monospace">{sb['s_sharpe']:.2f}</td>
              <td style="font-family:'JetBrains Mono',monospace;color:#ff5d6c">{sb['s_mdd']:.1f}%</td></tr>
          </tbody>
        </table>
        <div style="margin-top:10px;font-weight:600;color:{v_col}">{verdict_sb}</div>
        """, unsafe_allow_html=True)
        st.info("📌 หักค่าธรรมเนียมทุกครั้งที่สลับเข้า/ออกตลาดแล้ว (ยังไม่รวม slippage/ภาษี) — "
                "การเทียบกับ Buy & Hold เป็นมาตรฐานสำคัญ: กลยุทธ์ที่ดีต้องชนะการถือเฉย ๆ หลังหักต้นทุน")


with tab_forecast:
    # ══════════ ส่วนที่ 1: 5 เส้นแนวโน้มที่ดีที่สุด (Advanced Models) ══════════
    st.markdown('<div class="section-title">🎯 5 เส้นแนวโน้มที่ดีที่สุด (คณิตศาสตร์ขั้นสูง)</div>',
                unsafe_allow_html=True)
    st.markdown("""
    <div class="fc-banner">
      ฟิตหลายโมเดลคณิตศาสตร์ (Linear · Log-Linear · Polynomial · Theil-Sen · Holt) แล้ว
      <b>วัดความแม่นแบบ out-of-sample</b> (เทรน 80% / ทดสอบ 20%) จัดอันดับด้วยค่า
      <b>MAPE</b> (ยิ่งต่ำยิ่งแม่น) → เลือก <b>5 โมเดลที่ดีที่สุด</b> มาต่อเส้นแนวโน้มอนาคต
      <br><span style="color:var(--muted);font-size:12px">เป็นการคำนวณเชิงกำหนด (deterministic) ไม่ใช่การสุ่ม — เส้น Consensus = ค่าเฉลี่ยของ 5 โมเดล</span>
    </div>
    """, unsafe_allow_html=True)

    af1, af2 = st.columns([1, 1])
    with af1:
        adv_horizon = st.select_slider(
            "ระยะเวลาพยากรณ์ (เส้นแนวโน้ม)",
            options=[63, 126, 252, 504, 756], value=252,
            format_func=lambda d: f"{d//21} เดือน" if d < 252 else f"{d//252} ปี",
            key="adv_horizon")
    with af2:
        show_consensus = st.checkbox("แสดงเส้น Consensus (ค่าเฉลี่ย)", value=True, key="adv_consensus")

    price_list = m["df"]["Close"].dropna().tolist()
    with st.spinner("กำลังฟิตโมเดลและจัดอันดับ..."):
        adv = advanced_forecast(price_list, horizon=adv_horizon, top_k=5)

    if adv is None:
        st.warning("ข้อมูลไม่พอสำหรับการพยากรณ์ขั้นสูง (ต้องการอย่างน้อย ~60 วัน)")
    else:
        last_date_a = m["df"].index[-1]
        fut_dates_a = pd.bdate_range(start=last_date_a, periods=adv_horizon + 1)[1:]
        hist_a = m["df"]["Close"].tail(252)

        fig_adv = go.Figure()
        fig_adv.add_trace(go.Scatter(
            x=hist_a.index, y=hist_a.values, mode="lines", name="ราคาในอดีต",
            line=dict(color="#9aa6b8", width=2)))
        # เส้นพยากรณ์ 5 โมเดล (เส้นที่ดีที่สุด = หนา/ทึบ, ที่เหลือบางลง)
        for rank, r in enumerate(adv["top"]):
            is_best = (rank == 0)
            fig_adv.add_trace(go.Scatter(
                x=list(fut_dates_a), y=r["forecast"], mode="lines",
                name=f"{'⭐ ' if is_best else ''}{r['name']} (MAPE {r['mape']:.1f}%)",
                line=dict(color=r["color"], width=3 if is_best else 1.6,
                          dash=None if is_best else "dot"),
                opacity=1.0 if is_best else 0.75))
        # consensus
        if show_consensus:
            fig_adv.add_trace(go.Scatter(
                x=list(fut_dates_a), y=adv["consensus"], mode="lines",
                name="🎯 Consensus (เฉลี่ย 5 โมเดล)",
                line=dict(color="#ffffff", width=2.2, dash="dash")))
        # จุดราคาปัจจุบัน + เส้นแบ่งอดีต/อนาคต
        fig_adv.add_trace(go.Scatter(
            x=[hist_a.index[-1]], y=[adv["last"]], mode="markers",
            marker=dict(size=10, color="#e6c35c", line=dict(color="#fff", width=1.5)),
            name="ราคาปัจจุบัน"))
        fig_adv.add_vline(x=last_date_a, line_color="rgba(255,255,255,0.25)",
                          line_dash="dot", line_width=1)
        dark_layout(fig_adv, height=560,
                    title=f"5 เส้นแนวโน้มที่ดีที่สุด · {symbol} · {adv_horizon} วันทำการข้างหน้า")
        st.plotly_chart(fig_adv, use_container_width=True, config={"displayModeBar": False})

        # ตารางจัดอันดับโมเดล
        adv_horizon_label = f"{adv_horizon//252} ปี" if adv_horizon >= 252 else f"{adv_horizon//21} เดือน"
        rows_html = ""
        for rank, r in enumerate(adv["top"], 1):
            ret_c = "#2ee6a0" if r["ret"] >= 0 else "#ff5d6c"
            star = "⭐" if rank == 1 else str(rank)
            rows_html += f"""
            <tr>
              <td><span class="rank-num">{star}</span></td>
              <td><span style="color:{r['color']};font-weight:600">{r['name']}{' †' if r.get('clipped') else ''}</span></td>
              <td style="font-family:'JetBrains Mono',monospace">{r['mape']:.2f}%</td>
              <td style="font-family:'JetBrains Mono',monospace">{fmt_p(r['end'])}</td>
              <td style="font-family:'JetBrains Mono',monospace;color:{ret_c}">{r['ret']:+.1f}%</td>
            </tr>"""
        cons_c = "#2ee6a0" if adv["consensus_ret"] >= 0 else "#ff5d6c"
        st.markdown(f"""
        <table class="rank-table">
          <thead><tr>
            <th>อันดับ</th><th>โมเดล (วิธีคณิตศาสตร์)</th><th>ความคลาด (MAPE)</th>
            <th>ราคาคาดการณ์</th><th>ผลตอบแทน ({adv_horizon_label})</th>
          </tr></thead>
          <tbody>{rows_html}
            <tr style="background:rgba(255,255,255,0.04)">
              <td>🎯</td><td><b>Consensus (เฉลี่ย 5 โมเดล)</b></td>
              <td style="font-family:'JetBrains Mono',monospace">—</td>
              <td style="font-family:'JetBrains Mono',monospace"><b>{fmt_p(adv['consensus_end'])}</b></td>
              <td style="font-family:'JetBrains Mono',monospace;color:{cons_c}"><b>{adv['consensus_ret']:+.1f}%</b></td>
            </tr>
          </tbody>
        </table>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.info(f"📌 โมเดลที่แม่นที่สุดในอดีตคือ **{adv['best_name']}** (MAPE {adv['best_mape']:.2f}%) — "
                f"มุมมองรวม (Consensus) ชี้ว่า {symbol} มีแนวโน้ม "
                f"**{'ขึ้น' if adv['consensus_ret']>=0 else 'ลง'}** ราว {adv['consensus_ret']:+.1f}% "
                f"ใน {adv_horizon_label} · MAPE ต่ำ = โมเดลเคยพยากรณ์ช่วงทดสอบได้แม่น แต่ไม่รับประกันอนาคต · "
                "เส้นทุกโมเดลถูกจำกัดอยู่ในกรอบความผันผวน 3σ (กันโพลีโนเมียลเหวี่ยงหลุดจริง) — "
                "เครื่องหมาย † = โมเดลพยายามเหวี่ยงเกินกรอบจึงถูกตัด")

    st.markdown("<hr style='border-color:rgba(255,255,255,0.08);margin:26px 0'>",
                unsafe_allow_html=True)

    # ══════════ ส่วนที่ 2: Monte Carlo (เส้นทางจำลองความน่าจะเป็น) ══════════
    st.markdown('<div class="section-title">🔮 พยากรณ์ความน่าจะเป็น (Monte Carlo)</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="fc-banner">
      จำลองอนาคตด้วย <b>Monte Carlo (GBM + หางอ้วน Student-t)</b> — สุ่มเส้นทางราคาหลายร้อยเส้น
      จากค่าเฉลี่ยผลตอบแทน (μ) และความผันผวน (σ) ในอดีต โดยใช้การแจกแจงแบบ <b>หางอ้วน</b>
      ที่ปรับองศาอิสระ (ν) จาก kurtosis จริง — จึงจำลอง <b>วันที่ตลาดร่วงแรง/วิกฤต</b> ได้สมจริงกว่าการสุ่มแบบ normal
      <br><span style="color:var(--muted);font-size:12px">⚠️ เป็นการจำลองเชิงสถิติ (มีการสุ่ม) ไม่ใช่การทำนายแน่นอน — ต่างจาก 5 เส้นด้านบนที่เป็น deterministic · ν ยิ่งต่ำ = หางยิ่งอ้วน (เสี่ยงสุดขั้วมากขึ้น)</span>
    </div>
    """, unsafe_allow_html=True)

    fc1, fc2, fc3 = st.columns([1, 1, 1])
    with fc1:
        horizon = st.select_slider("ระยะเวลาพยากรณ์",
                                   options=[63, 126, 252, 504, 756],
                                   value=252,
                                   format_func=lambda d: f"{d//21} เดือน" if d < 252 else f"{d//252} ปี")
    with fc2:
        n_sims = st.select_slider("จำนวนเส้นทางจำลอง",
                                  options=[100, 300, 500, 1000], value=300)
    with fc3:
        show_paths = st.checkbox("แสดงเส้นทางตัวอย่าง", value=True)

    with st.spinner("กำลังจำลองอนาคต (Monte Carlo)..."):
        fc = monte_carlo_forecast(price_list, days=horizon, n_sims=n_sims)
        lin = linear_extrapolation(price_list, days=horizon)

    if fc is None:
        st.warning("ข้อมูลไม่พอสำหรับการพยากรณ์")
    else:
        # สร้างแกนเวลาอนาคต (วันทำการ)
        last_date = m["df"].index[-1]
        future_dates = pd.bdate_range(start=last_date, periods=horizon + 1)[1:]
        hist_tail = m["df"]["Close"].tail(252)  # โชว์ประวัติ 1 ปีล่าสุด

        fig_fc = go.Figure()

        # ── ประวัติ ──
        fig_fc.add_trace(go.Scatter(
            x=hist_tail.index, y=hist_tail.values, mode="lines", name="ราคาในอดีต",
            line=dict(color="#5b8def", width=2)
        ))

        # ── แถบ 5–95% (กว้างสุด) ──
        fig_fc.add_trace(go.Scatter(
            x=list(future_dates), y=fc["p95"], mode="lines", name="95th",
            line=dict(width=0), showlegend=False, hoverinfo="skip"
        ))
        fig_fc.add_trace(go.Scatter(
            x=list(future_dates), y=fc["p5"], mode="lines", name="ช่วง 5–95%",
            line=dict(width=0), fill="tonexty", fillcolor="rgba(230,195,92,0.10)"
        ))
        # ── แถบ 25–75% (แคบ) ──
        fig_fc.add_trace(go.Scatter(
            x=list(future_dates), y=fc["p75"], mode="lines", name="75th",
            line=dict(width=0), showlegend=False, hoverinfo="skip"
        ))
        fig_fc.add_trace(go.Scatter(
            x=list(future_dates), y=fc["p25"], mode="lines", name="ช่วง 25–75%",
            line=dict(width=0), fill="tonexty", fillcolor="rgba(46,230,160,0.14)"
        ))

        # ── เส้นทางตัวอย่าง ──
        if show_paths:
            for i, path in enumerate(fc["samples"][:25]):
                fig_fc.add_trace(go.Scatter(
                    x=list(future_dates), y=path[1:], mode="lines",
                    line=dict(color="rgba(120,140,170,0.18)", width=0.7),
                    showlegend=(i == 0), name="เส้นทางจำลอง" if i == 0 else None,
                    hoverinfo="skip"
                ))

        # ── median (เส้นกลาง) ──
        fig_fc.add_trace(go.Scatter(
            x=list(future_dates), y=fc["p50"], mode="lines", name="ค่ากลาง (Median)",
            line=dict(color="#2ee6a0", width=2.5, shape="spline")
        ))
        # ── เส้นแนวโน้ม linear ──
        if lin is not None:
            fig_fc.add_trace(go.Scatter(
                x=list(future_dates), y=lin, mode="lines", name="แนวโน้มเชิงเส้น (Linear)",
                line=dict(color="#a877e6", width=2, dash="dash")
            ))
        # จุดราคาปัจจุบัน
        fig_fc.add_trace(go.Scatter(
            x=[hist_tail.index[-1]], y=[fc["last"]], mode="markers",
            marker=dict(size=10, color="#e6c35c", line=dict(color="#fff", width=1.5)),
            name="ราคาปัจจุบัน"
        ))
        fig_fc.add_vline(x=last_date, line_color="rgba(255,255,255,0.25)",
                         line_dash="dot", line_width=1)
        dark_layout(fig_fc, height=560,
                    title=f"พยากรณ์ {symbol} · {horizon} วันทำการข้างหน้า · {n_sims} simulations")
        st.plotly_chart(fig_fc, use_container_width=True, config={"displayModeBar": False})

        # ── สรุปผลพยากรณ์ (การ์ด) ──
        st.markdown('<div class="section-title" style="margin-top:6px">📊 สรุปผลการพยากรณ์</div>',
                    unsafe_allow_html=True)
        fcc1, fcc2, fcc3, fcc4 = st.columns(4)
        exp_c  = "pos" if fc["exp_return"] >= 0 else "neg"
        prob_c = "pos" if fc["prob_up"] >= 50 else "neg"
        horizon_label = f"{horizon//252} ปี" if horizon >= 252 else f"{horizon//21} เดือน"
        with fcc1:
            st.markdown(f"""<div class="mcard {exp_c}">
              <div class="mcard-label">ราคาคาดการณ์ (Median)</div>
              <div class="mcard-value">{fmt_p(fc['final_median'])}</div>
              <div class="mcard-sub">ใน {horizon_label}</div></div>""", unsafe_allow_html=True)
        with fcc2:
            st.markdown(f"""<div class="mcard {exp_c}">
              <div class="mcard-label">ผลตอบแทนคาดหวัง</div>
              <div class="mcard-value">{fc['exp_return']:+.1f}%</div>
              <div class="mcard-sub">เทียบราคาปัจจุบัน</div></div>""", unsafe_allow_html=True)
        with fcc3:
            st.markdown(f"""<div class="mcard {prob_c}">
              <div class="mcard-label">โอกาสราคาขึ้น</div>
              <div class="mcard-value">{fc['prob_up']:.0f}%</div>
              <div class="mcard-sub">จาก {n_sims} เส้นทาง</div></div>""", unsafe_allow_html=True)
        with fcc4:
            st.markdown(f"""<div class="mcard">
              <div class="mcard-label">ช่วงราคา 90% CI</div>
              <div class="mcard-value" style="font-size:15px">{fmt_p(fc['final_p5'])} – {fmt_p(fc['final_p95'])}</div>
              <div class="mcard-sub">μ={fc['mu']*100:.3f}% σ={fc['sigma']*100:.2f}%/วัน · ν={fc['nu']}</div></div>""",
              unsafe_allow_html=True)

        _tail_note = (f"หางอ้วนชัด (ν={fc['nu']}, excess kurtosis {fc['exkurt']}) — โมเดลเผื่อโอกาสร่วงแรงไว้แล้ว"
                      if fc['nu'] < 10 else
                      f"หางค่อนข้างปกติ (ν={fc['nu']})")
        st.info(f"📌 ตีความ: จากการจำลอง {n_sims} เส้นทาง ราคา {symbol} มีแนวโน้ม "
                f"**{'เพิ่มขึ้น' if fc['exp_return']>=0 else 'ลดลง'}** เฉลี่ย {fc['exp_return']:+.1f}% "
                f"ใน {horizon_label} โดยมีโอกาส {fc['prob_up']:.0f}% ที่จะจบสูงกว่าราคาปัจจุบัน — "
                f"ยิ่งช่วงเวลายาว แถบความไม่แน่นอนยิ่งกว้าง · {_tail_note}")

# ══════════════════════════════════════════════════════════════
#  TAB · NEWS — ข่าว + วิเคราะห์เชื่อมโยงอนาคตด้วย AI
# ══════════════════════════════════════════════════════════════
with tab_news:
    st.markdown('<div class="section-title">📰 ข่าว & แนวโน้มอนาคต</div>', unsafe_allow_html=True)
    st.caption("ข่าวจริงจาก Finnhub — ข่าวบริษัท + ข่าวตลาด/เศรษฐกิจ/ภูมิรัฐศาสตร์ (สงคราม นโยบาย ฯลฯ) "
               "พร้อมให้ AI ประเมินผลกระทบต่ออนาคตของสินทรัพย์")

    with st.spinner("กำลังดึงข่าวล่าสุด..."):
        comp_news = fetch_company_news(symbol, days=21)
        gen_news  = fetch_general_news("general")

    # ── Sentiment heuristic จากพาดหัวข่าว ──
    all_news_for_sent = (comp_news or []) + (gen_news or [])
    sent_score, n_pos, n_neg = news_sentiment(all_news_for_sent)
    sent_label = ("เชิงบวก 🟢" if sent_score > 15 else
                  "เชิงลบ 🔴" if sent_score < -15 else "เป็นกลาง 🟡")
    sent_col = "#2ee6a0" if sent_score > 15 else "#ff5d6c" if sent_score < -15 else "#e6c35c"
    bar_pct = (sent_score + 100) / 2  # map -100..100 → 0..100

    nc1, nc2 = st.columns([1, 1])
    with nc1:
        st.markdown(f"""
        <div class="mcard" style="--accent:{sent_col}">
          <div class="mcard-label">SENTIMENT ข่าว (Heuristic)</div>
          <div class="mcard-value" style="color:{sent_col}">{sent_score:+d} · {sent_label}</div>
          <div class="mcard-sub">คำเชิงบวก {n_pos} · คำเชิงลบ {n_neg} จาก {len(all_news_for_sent)} ข่าว</div>
          <div class="pb-bg" style="margin-top:8px"><div class="pb-fill"
            style="width:{bar_pct:.0f}%;background:{sent_col};color:{sent_col}"></div></div>
        </div>""", unsafe_allow_html=True)
    with nc2:
        st.markdown(f"""
        <div class="mcard blue">
          <div class="mcard-label">ภาพรวมตัวเลข (ประกอบข่าว)</div>
          <div class="mcard-value">{m['score']}/100 · {m['verdict']}</div>
          <div class="mcard-sub">CAGR {m['cagr']:+.1f}% · Momentum {m['momentum']:+.1f}% · RSI {m['rsi']:.0f}</div>
        </div>""", unsafe_allow_html=True)

    st.caption("⚠️ Sentiment นี้เป็นการนับคำแบบหยาบ (heuristic) เพื่อดูภาพรวมเร็ว ๆ — "
               "กดปุ่มด้านล่างให้ AI วิเคราะห์เชิงลึกแทน")

    # ── ปุ่มให้ AI วิเคราะห์ข่าว → อนาคต ──
    if st.button("🧠 ให้ AI วิเคราะห์ข่าว → เชื่อมโยงอนาคต", use_container_width=False):
        if not all_news_for_sent:
            st.warning("ยังไม่มีข่าวให้วิเคราะห์ (ลองหุ้น/ETF สหรัฐ เช่น AAPL, NVDA — คริปโต/forex/ดัชนีมักไม่มีข่าวบริษัท)")
        else:
            headlines_txt = "\n".join(
                f"- [{dt.datetime.fromtimestamp(n.get('datetime', 0)).strftime('%d/%m')}] "
                f"{n.get('headline','')} ({n.get('source','')})"
                for n in all_news_for_sent[:18]
            )
            news_sys = f"""คุณคือผู้ช่วยวิเคราะห์การลงทุนเชิงปริมาณของ DGV ตอบในสไตล์ผู้ช่วย AI มืออาชีพ แบบ ChatGPT หรือ Gemini — เป็นกลาง กระชับ มีโครงสร้าง
วิเคราะห์ข่าวด้านล่างเกี่ยวกับ {symbol} ({WATCHLIST.get(symbol, symbol)}) อย่างสมดุล โดยเชื่อมโยงกับแนวโน้มราคา

ข้อมูลเชิงปริมาณปัจจุบัน:
• ราคา: {fmt_p(cur_price)} | CAGR: {m['cagr']:+.1f}% | Momentum: {m['momentum']:+.1f}% | RSI: {m['rsi']:.0f}
• Composite Score: {m['score']}/100 → {m['verdict']} | Volatility: {m['vol_l']:.1f}%

โครงสร้างคำตอบ (ภาษาไทย กระชับ อ่านง่าย):
1. สรุปภาพรวมข่าว: ประเด็นหลัก 2-3 เรื่อง (รวมข่าวมหภาค/นโยบายถ้ามี)
2. ปัจจัยบวก / ปัจจัยลบ ต่อราคา
3. ผลต่อแนวโน้มอนาคต: ข่าวเหล่านี้น่าจะหนุนหรือกดดันราคาอย่างไร เชื่อมโยงกับตัวเลขข้างต้น

อย่าคัดลอกพาดหัวข่าวมาตรง ๆ ให้สรุปด้วยคำพูดของคุณเอง"""
            try:
                client = get_claude_client()
                resp = client.messages.create(
                    model=CLAUDE_MODEL, max_tokens=1200, system=news_sys,
                    messages=[{"role": "user",
                               "content": f"ข่าวล่าสุดเกี่ยวกับ {symbol}:\n{headlines_txt}\n\n"
                                          "ช่วยวิเคราะห์เชื่อมโยงกับแนวโน้มอนาคตให้หน่อยครับ"}],
                )
                analysis = "".join(b.text for b in resp.content if b.type == "text")
                st.markdown(f"""<div class="calc-result" style="margin-bottom:14px">
                  <div style="font-size:11px;letter-spacing:2px;text-transform:uppercase;
                       color:{sent_col};margin-bottom:10px">🧠 บทวิเคราะห์ข่าว → อนาคต โดย Claude</div>
                  <div style="line-height:1.75;font-size:13px">{analysis.replace(chr(10),'<br>')}</div>
                </div>""", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"วิเคราะห์ข่าวไม่สำเร็จ (เช็ค ANTHROPIC_API_KEY): {e}")

    # ── รายการข่าว ──
    ncol1, ncol2 = st.columns(2)

    def render_news_list(items, empty_msg):
        if not items:
            st.caption(empty_msg)
            return
        for n in items[:12]:
            ts_n = n.get("datetime", 0)
            date_s = dt.datetime.fromtimestamp(ts_n).strftime("%d/%m %H:%M") if ts_n else ""
            head = (n.get("headline", "") or "")[:160]
            src  = n.get("source", "")
            url  = n.get("url", "#")
            summ = (n.get("summary", "") or "")[:140]
            summ = summ + "…" if len(n.get("summary", "") or "") > 140 else summ
            st.markdown(f"""
            <div class="mcard" style="margin-bottom:9px;animation:fadeInUp .4s ease both">
              <div style="font-size:10px;color:var(--muted);font-family:'JetBrains Mono',monospace;margin-bottom:3px">
                {date_s} · {src}</div>
              <a href="{url}" target="_blank" style="color:var(--ink);text-decoration:none;
                 font-weight:600;font-size:13px;line-height:1.4">{head}</a>
              {'<div style="font-size:11px;color:var(--muted);margin-top:5px;line-height:1.5">'+summ+'</div>' if summ else ''}
            </div>""", unsafe_allow_html=True)

    with ncol1:
        st.markdown(f'<div class="section-title" style="font-size:17px">🏢 ข่าวเกี่ยวกับ {symbol}</div>',
                    unsafe_allow_html=True)
        render_news_list(comp_news,
                         "ไม่มีข่าวบริษัทสำหรับสินทรัพย์นี้ (คริปโต/forex/ดัชนี/ทองคำ มักไม่มีข่าวบริษัทใน Finnhub) — "
                         "ลองหุ้น/ETF สหรัฐ เช่น AAPL, NVDA, TSLA")
    with ncol2:
        st.markdown('<div class="section-title" style="font-size:17px">🌍 ข่าวตลาด · เศรษฐกิจ · ภูมิรัฐศาสตร์</div>',
                    unsafe_allow_html=True)
        render_news_list(gen_news, "ดึงข่าวตลาดไม่สำเร็จ (ตรวจสอบ FINNHUB_API_KEY ใน secrets)")

    st.info("📌 ข่าวมาจาก Finnhub แบบ real-time — คลิกพาดหัวเพื่ออ่านฉบับเต็มที่ต้นทาง")

# ══════════════════════════════════════════════════════════════
#  TAB 4 — RANKING
# ══════════════════════════════════════════════════════════════
with tab_rank:
    st.markdown('<div class="section-title">🏆 อันดับสินทรัพย์ (Composite Score · คณิตศาสตร์ + ข่าว)</div>',
                unsafe_allow_html=True)
    st.caption("คำนวณจาก Sharpe, CAGR, Drawdown, Momentum, MA Alignment, Z-Score "
               "แล้วปรับด้วย News Sentiment (เปิด/ปิดได้ด้านล่าง)")

    rk_group = st.selectbox("เลือกหมวดสินทรัพย์", list(ASSET_GROUPS.keys()),
                            index=0, key="rank_group")
    rk_syms = list(ASSET_GROUPS[rk_group].keys())

    use_news = st.checkbox("📰 รวมปัจจัยข่าว (News Sentiment) ในการให้คะแนนและจัดอันดับ",
                           value=True, key="rank_use_news")

    with st.spinner(f"กำลังดึงและวิเคราะห์ {len(rk_syms)} สินทรัพย์ในหมวด «{rk_group}»..."):
        rankings = fetch_watchlist_scores(rk_syms)

    if not rankings:
        st.warning("ไม่สามารถดึงข้อมูลได้")
    else:
        # ── ปรับคะแนนด้วยข่าว: sentiment -100..+100 → ปรับ ±10 คะแนน ──
        for r in rankings:
            ns = r.get("news_sent", 0)
            adj = max(-10, min(10, round(ns / 10)))
            r["news_adj"] = adj
            r["score_final"] = max(0, min(100, r["score"] + (adj if use_news else 0)))
        rankings = sorted(rankings, key=lambda x: x["score_final"], reverse=True)

        medals = ["🥇","🥈","🥉"] + [""] * 20
        verdict_icon = {"Strong Buy":"🚀","Buy":"📈","Hold/Watch":"⏳","Underweight":"⚠️","Avoid":"🚫"}
        score_bg = lambda s: "rgba(46,230,160,0.18)" if s>=75 else "rgba(230,195,92,0.18)" if s>=50 else "rgba(255,93,108,0.18)"

        html_rows = ""
        for i, r in enumerate(rankings):
            disp_score = r["score_final"]
            sc_bg  = score_bg(disp_score)
            v_icon = verdict_icon.get(r["verdict"], "")
            cagr_c = "#2ee6a0" if r["cagr"]>=0 else "#ff5d6c"
            mom_c  = "#2ee6a0" if r["momentum"]>=0 else "#ff5d6c"

            # ── คอลัมน์ข่าว ──
            ns = r.get("news_sent", 0); ncnt = r.get("news_count", 0)
            if ncnt == 0:
                news_html = '<span style="color:var(--muted)">—</span>'
            else:
                news_c = "#2ee6a0" if ns > 15 else "#ff5d6c" if ns < -15 else "#e6c35c"
                news_html = (f'<span style="color:{news_c};font-family:\'JetBrains Mono\',monospace;'
                             f'font-weight:600">{ns:+d}</span>'
                             f'<div style="font-size:9px;color:var(--muted)">{ncnt} ข่าว</div>')

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
            if use_news and ncnt > 0:
                if ns > 15:    reasons.append(f"ข่าวเชิงบวก ({ns:+d})")
                elif ns < -15: reasons.append(f"ข่าวเชิงลบ ({ns:+d})")
            reason_str = " · ".join(reasons[:3]) if reasons else "ตัวชี้วัดปานกลาง"

            # ── เดลตาคะแนนจากข่าว (โชว์ใต้ SCORE) ──
            delta_html = ""
            if use_news and r["news_adj"] != 0:
                dcol = "#2ee6a0" if r["news_adj"] > 0 else "#ff5d6c"
                delta_html = f'<div style="font-size:9px;color:{dcol};margin-top:2px">{r["news_adj"]:+d} จากข่าว</div>'

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
                  {disp_score}
                </span>{delta_html}
              </td>
              <td style="font-family:'JetBrains Mono',monospace;color:{cagr_c}">{r['cagr']:+.1f}%</td>
              <td style="font-family:'JetBrains Mono',monospace">{r['sharpe']:.2f}</td>
              <td style="font-family:'JetBrains Mono',monospace;color:#ff5d6c">{r['mdd']:.1f}%</td>
              <td style="font-family:'JetBrains Mono',monospace;color:{mom_c}">{r['momentum']:+.1f}%</td>
              <td style="font-family:'JetBrains Mono',monospace">{r['winrate']:.0f}%</td>
              <td style="text-align:center">{news_html}</td>
              <td>{v_icon} {r['verdict']}</td>
              <td style="font-size:11px;color:var(--muted);max-width:200px">{reason_str}</td>
            </tr>"""

        st.markdown(f"""
        <table class="rank-table">
          <thead><tr>
            <th>#</th><th>สินทรัพย์</th><th>SCORE</th>
            <th>CAGR</th><th>SHARPE</th><th>MAX DD</th>
            <th>MOMENTUM</th><th>WIN RATE</th><th>NEWS</th><th>สัญญาณ</th><th>เหตุผล</th>
          </tr></thead>
          <tbody>{html_rows}</tbody>
        </table>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if use_news:
            st.info("📌 SCORE รวมปัจจัยข่าวแล้ว — ปรับ ±10 คะแนนตาม News Sentiment (heuristic นับคำจากข่าว Finnhub "
                    "ย้อนหลัง 14 วัน) · คอลัมน์ NEWS = คะแนนข่าว −100 ถึง +100 · «—» = ไม่มีข่าวบริษัท "
                    "(คริปโต/forex/ดัชนี/ETF บางตัว) จึงไม่ปรับคะแนน")
        else:
            st.info("📌 หมายเหตุ: อันดับนี้ใช้ข้อมูลราคาย้อนหลังเท่านั้น ไม่รวมปัจจัยข่าว — "
                    "ติ๊กกล่อง «รวมปัจจัยข่าว» ด้านบนเพื่อให้ข่าวมีผลต่อคะแนน")

# ══════════════════════════════════════════════════════════════
#  TAB — PORTFOLIO (กระจายความเสี่ยง: correlation + efficient frontier)
# ══════════════════════════════════════════════════════════════
with tab_portfolio:
    st.markdown('<div class="section-title">🧺 พอร์ต & การกระจายความเสี่ยง</div>',
                unsafe_allow_html=True)
    st.caption("วิเคราะห์ระดับพอร์ต (ไม่ใช่รายตัว) — ความสัมพันธ์ระหว่างสินทรัพย์ (Correlation) "
               "และการจัดสรรน้ำหนักที่เหมาะสมที่สุดด้วยทฤษฎี Markowitz (Efficient Frontier)")

    pf_group = st.selectbox("เลือกหมวดสินทรัพย์สำหรับสร้างพอร์ต", list(ASSET_GROUPS.keys()),
                            index=0, key="pf_group")
    pf_syms = list(ASSET_GROUPS[pf_group].keys())

    with st.spinner(f"กำลังจัดแนวข้อมูลและคำนวณพอร์ตจาก {len(pf_syms)} สินทรัพย์..."):
        ef = efficient_frontier(pf_syms)

    if ef is None:
        st.warning("ข้อมูลไม่พอสำหรับวิเคราะห์พอร์ต (ต้องมีอย่างน้อย 2 สินทรัพย์ที่มีข้อมูลพอ)")
    else:
        cols = ef["cols"]

        # ── Correlation heatmap ──
        st.markdown('<div class="section-title" style="font-size:17px">🔗 Correlation Matrix</div>',
                    unsafe_allow_html=True)
        st.caption("ค่าใกล้ +1 = เคลื่อนไหวไปทางเดียวกัน (กระจายเสี่ยงได้น้อย) · "
                   "ใกล้ 0 หรือติดลบ = ช่วยกระจายเสี่ยงได้ดี")
        fig_corr = go.Figure(data=go.Heatmap(
            z=ef["corr"], x=cols, y=cols, zmin=-1, zmax=1,
            colorscale=[[0, "#2ee6a0"], [0.5, "#15203a"], [1, "#ff5d6c"]],
            text=[[f"{v:.2f}" for v in row] for row in ef["corr"]],
            texttemplate="%{text}", textfont=dict(size=10, family="JetBrains Mono"),
            colorbar=dict(title="corr")))
        fig_corr.update_layout(height=380, margin=dict(l=10, r=10, t=10, b=10),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="JetBrains Mono", color="#c3cbd9", size=10))
        st.plotly_chart(fig_corr, use_container_width=True, config={"displayModeBar": False})

        # ── Efficient Frontier ──
        st.markdown('<div class="section-title" style="font-size:17px;margin-top:14px">🎯 Efficient Frontier</div>',
                    unsafe_allow_html=True)
        st.caption(f"สุ่มพอร์ต {len(ef['rets']):,} แบบ (ปรับน้ำหนักสุ่ม) · จุดยิ่งสูง-ซ้าย = "
                   "ผลตอบแทนสูง ความเสี่ยงต่ำ (ดี) · ใช้ข้อมูล {} วันทำการ".format(ef["n_days"]))
        ms, mv = ef["max_sharpe"], ef["min_vol"]
        fig_ef = go.Figure()
        fig_ef.add_trace(go.Scatter(
            x=ef["vols"], y=ef["rets"], mode="markers",
            marker=dict(size=4, color=ef["sharpes"], colorscale="Viridis",
                        showscale=True, colorbar=dict(title="Sharpe"), opacity=0.55),
            name="พอร์ตสุ่ม", hovertemplate="ความเสี่ยง %{x:.1f}%<br>ผลตอบแทน %{y:.1f}%<extra></extra>"))
        fig_ef.add_trace(go.Scatter(
            x=[ms["vol"]], y=[ms["ret"]], mode="markers",
            marker=dict(size=16, color="#e6c35c", symbol="star", line=dict(color="#fff", width=1)),
            name="⭐ Max Sharpe"))
        fig_ef.add_trace(go.Scatter(
            x=[mv["vol"]], y=[mv["ret"]], mode="markers",
            marker=dict(size=14, color="#2ee6a0", symbol="diamond", line=dict(color="#fff", width=1)),
            name="🛡️ Min Volatility"))
        dark_layout(fig_ef, height=440, title="ความเสี่ยง (แกน X) vs ผลตอบแทนคาดหวัง (แกน Y) ต่อปี")
        fig_ef.update_layout(xaxis_title="ความผันผวน/ปี (%)", yaxis_title="ผลตอบแทนคาดหวัง/ปี (%)")
        st.plotly_chart(fig_ef, use_container_width=True, config={"displayModeBar": False})

        # ── น้ำหนักพอร์ตแนะนำ ──
        def weights_rows(weights):
            items = sorted(weights.items(), key=lambda kv: kv[1], reverse=True)
            return "".join(
                f'<tr><td class="rank-ticker">{s}</td>'
                f'<td style="font-family:\'JetBrains Mono\',monospace">{w:.1f}%</td>'
                f'<td><div class="pb-bg"><div class="pb-fill" style="width:{min(w,100):.0f}%;'
                f'background:#e6c35c;color:#e6c35c"></div></div></td></tr>'
                for s, w in items if w >= 0.1)

        pcol1, pcol2 = st.columns(2)
        with pcol1:
            st.markdown('<div class="section-title" style="font-size:15px">⭐ พอร์ต Max Sharpe</div>',
                        unsafe_allow_html=True)
            st.markdown(f'<div style="font-size:12px;color:var(--muted);margin-bottom:6px">'
                        f'ผลตอบแทน {ms["ret"]:+.1f}%/ปี · ความเสี่ยง {ms["vol"]:.1f}% · Sharpe {ms["sharpe"]:.2f}</div>',
                        unsafe_allow_html=True)
            st.markdown(f'<table class="rank-table"><tbody>{weights_rows(ms["weights"])}</tbody></table>',
                        unsafe_allow_html=True)
        with pcol2:
            st.markdown('<div class="section-title" style="font-size:15px">🛡️ พอร์ต Min Volatility</div>',
                        unsafe_allow_html=True)
            st.markdown(f'<div style="font-size:12px;color:var(--muted);margin-bottom:6px">'
                        f'ผลตอบแทน {mv["ret"]:+.1f}%/ปี · ความเสี่ยง {mv["vol"]:.1f}% · Sharpe {mv["sharpe"]:.2f}</div>',
                        unsafe_allow_html=True)
            st.markdown(f'<table class="rank-table"><tbody>{weights_rows(mv["weights"])}</tbody></table>',
                        unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.info("📌 Max Sharpe = พอร์ตที่ให้ผลตอบแทนต่อความเสี่ยงดีที่สุด · Min Volatility = พอร์ตที่นิ่งที่สุด · "
                "คำนวณจากผลตอบแทน/ความผันผวน/ความสัมพันธ์ย้อนหลัง — เป็นจุดเริ่มต้นการจัดพอร์ต ไม่ใช่สูตรสำเร็จ "
                "(อดีตไม่การันตีอนาคต และไม่รวมค่าธรรมเนียม/ภาษี)")


with tab_income:
    st.markdown('<div class="section-title">💰 เครื่องคำนวณรายได้การลงทุน</div>', unsafe_allow_html=True)

    col_calc1, col_calc2 = st.columns(2)

    with col_calc1:
        st.markdown("#### 📊 คำนวณผลตอบแทนตามสถานการณ์")
        capital     = st.number_input("เงินลงทุนเริ่มต้น (USD)", min_value=1000,
                                       max_value=100_000_000, value=100_000, step=10_000)
        monthly_add = st.number_input("เงินเพิ่มต่อเดือน (USD)", min_value=0,
                                       max_value=1_000_000, value=5_000, step=1_000)
        years_inv   = st.slider("ระยะเวลาลงทุน (ปี)", 1, 30, 10)
        use_cagr    = st.checkbox(f"ใช้ CAGR จริงของ {symbol} ({m['cagr']:.1f}%/ปี)", value=True)
        rate_input  = m["cagr"] if use_cagr else st.slider(
            "อัตราผลตอบแทนต่อปี (%) — จากราคา", -20.0, 50.0, 10.0, step=0.5)

        # ── ปัจจัยจริงสำหรับนักลงทุน: ปันผล / ภาษี / ค่าธรรมเนียม ──
        with st.expander("⚙️ ปัจจัยจริง: ปันผล · ภาษี · ค่าธรรมเนียม (กดเพื่อปรับ)", expanded=False):
            _f = fetch_fundamentals(symbol)
            _dv_default = float(_f["div_yield"]) if _f and isinstance(_f.get("div_yield"), (int, float)) else 0.0
            div_yield_pct  = st.number_input("เงินปันผล/ปี (%)", min_value=0.0, max_value=20.0,
                                             value=round(min(_dv_default, 20.0), 2), step=0.1)
            wht_pct        = st.slider("ภาษีหัก ณ ที่จ่ายปันผล (%) — หุ้น US สำหรับคนไทย", 0, 30, 15)
            fee_annual_pct = st.slider("ค่าธรรมเนียม/ค่าบริหารต่อปี (%)", 0.0, 3.0, 0.5, step=0.1)

        div_net        = div_yield_pct * (1 - wht_pct / 100)        # ปันผลสุทธิหลังภาษี
        net_rate_input = rate_input + div_net - fee_annual_pct      # อัตราสุทธิต่อปี (%)

        rate_annual  = net_rate_input / 100
        rate_monthly = (1 + rate_annual) ** (1/12) - 1

        total = capital
        values = [total]
        contributions = [capital]
        for mo in range(1, years_inv * 12 + 1):
            total = total * (1 + rate_monthly) + monthly_add
            values.append(total)
            contributions.append(capital + monthly_add * mo)

        final_val      = values[-1]
        total_contrib  = capital + monthly_add * years_inv * 12
        total_gain     = final_val - total_contrib
        total_return_pct = (final_val / total_contrib - 1) * 100 if total_contrib else 0
        ann_income     = final_val * (rate_annual if rate_annual > 0 else 0.05)
        usdthb         = fetch_usdthb()

        scenarios = {}
        for label, r in [("แย่ (สุทธิ −5%)", net_rate_input-5),
                         ("ฐาน (สุทธิ)", net_rate_input),
                         ("ดี (สุทธิ +5%)", net_rate_input+5)]:
            rm = (1 + r/100) ** (1/12) - 1
            v  = capital
            for _ in range(years_inv * 12):
                v = v * (1 + rm) + monthly_add
            scenarios[label] = v

        st.markdown(f"""
        <div class="calc-result">
          <div style="font-size:11px;letter-spacing:2px;text-transform:uppercase;
                      color:#9aa6b8;margin-bottom:10px">ผลการคำนวณ · {years_inv} ปี</div>
          <div class="calc-row"><span>มูลค่าสุดท้าย</span><span>${final_val:,.0f}</span></div>
          <div class="calc-row"><span>≈ คิดเป็นเงินบาท</span><span>฿{final_val*usdthb:,.0f}</span></div>
          <div class="calc-row"><span>เงินลงทุนรวม</span><span>${total_contrib:,.0f}</span></div>
          <div class="calc-row"><span>กำไรสะสม</span><span>${total_gain:,.0f}</span></div>
          <div class="calc-row"><span>ผลตอบแทนรวม</span><span>{total_return_pct:+.1f}%</span></div>
          <div class="calc-row"><span>รายได้ต่อปี</span><span>${ann_income:,.0f}</span></div>
          <div class="calc-row"><span>รายได้ต่อเดือน</span><span>${ann_income/12:,.0f}</span></div>
          <div style="margin-top:10px;padding-top:8px;border-top:1px solid rgba(255,255,255,0.12)">
            <div style="font-size:10px;color:#9aa6b8;margin-bottom:4px">อัตราผลตอบแทนสุทธิที่ใช้คำนวณ</div>
            <div class="calc-row"><span>ราคา</span><span>{rate_input:+.1f}%</span></div>
            <div class="calc-row"><span>+ ปันผลสุทธิ (หักภาษี {wht_pct}%)</span><span>{div_net:+.2f}%</span></div>
            <div class="calc-row"><span>− ค่าธรรมเนียม</span><span>−{fee_annual_pct:.1f}%</span></div>
            <div class="calc-row"><span><b>= สุทธิต่อปี</b></span><span><b>{net_rate_input:+.1f}%</b></span></div>
          </div>
          <div style="margin-top:12px;padding-top:10px;border-top:1px solid rgba(255,255,255,0.12)">
            <div style="font-size:10px;color:#9aa6b8;margin-bottom:6px">SCENARIOS ({years_inv} ปี)</div>
        """, unsafe_allow_html=True)
        for label, sv in scenarios.items():
            col_s = "#2ee6a0" if sv > total_contrib else "#ff5d6c"
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;font-size:12px;padding:3px 0">
              <span style="color:#c3cbd9">{label}</span>
              <span style="font-family:'JetBrains Mono',monospace;color:{col_s}">${sv:,.0f}</span>
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
            line=dict(color="#2ee6a0", width=2.5, shape="spline")
        ))
        dark_layout(fig_grow, height=320, title=f"การเติบโตของพอร์ต {years_inv} ปี")
        fig_grow.update_layout(xaxis_title="ปี", yaxis_title="มูลค่า (USD)")
        st.plotly_chart(fig_grow, use_container_width=True, config={"displayModeBar": False})

        st.markdown("#### ⚠️ คำนวณความเสี่ยง")
        invest_amt  = st.number_input("เงินลงทุน (สำหรับคำนวณ VaR) (USD)", min_value=1000,
                                       max_value=10_000_000, value=100_000, step=10_000)
        conf_level  = st.select_slider("Confidence Level", [90, 95, 99], value=95)
        returns_full = m["df"]["Close"].pct_change().dropna()
        var_pct  = np.percentile(returns_full, (1 - conf_level/100) * 100) * 100
        tail_r   = returns_full[returns_full <= var_pct/100]
        es_pct   = tail_r.mean() * 100 if len(tail_r) else var_pct
        var_thb  = invest_amt * abs(var_pct) / 100
        es_thb   = invest_amt * abs(es_pct)  / 100

        # Kelly ที่ถูกต้องขึ้น: f* = W - (1-W)/R, R = avg win / avg loss (ใช้ 1.0 เป็นค่าฐานปลอดภัย)
        W = bt["winrate"] / 100
        kelly = max(0.0, (W - (1 - W) / 1.0)) * 100  # R≈1 (1.5%TP/1.5%SL) → conservative

        st.markdown(f"""
        <div class="calc-result" style="margin-top:0">
          <div style="font-size:11px;letter-spacing:2px;text-transform:uppercase;
                      color:#9aa6b8;margin-bottom:10px">RISK METRICS · {conf_level}% Confidence</div>
          <div class="calc-row"><span>VaR/วัน ({conf_level}%)</span><span>{var_pct:.2f}%</span></div>
          <div class="calc-row"><span>VaR เงิน</span><span>${var_thb:,.0f}</span></div>
          <div class="calc-row"><span>Expected Shortfall</span><span>{es_pct:.2f}%</span></div>
          <div class="calc-row"><span>ES เงิน</span><span>${es_thb:,.0f}</span></div>
          <div class="calc-row"><span>Max Drawdown</span><span>{m['mdd']:.1f}%</span></div>
          <div class="calc-row"><span>Max Loss เงิน (DD)</span>
            <span>${invest_amt * abs(m['mdd'])/100:,.0f}</span></div>
          <div class="calc-row"><span>Kelly Criterion</span>
            <span>{kelly:.1f}% ของพอร์ต</span></div>
        </div>
        """, unsafe_allow_html=True)

    st.info(f"📌 มุมนักลงทุนไทย: ตัวเลขเป็น USD (≈ {usdthb:.2f} บาท/ดอลลาร์ ณ ปัจจุบัน) — "
            "การลงทุนหุ้น US มีความเสี่ยงค่าเงิน USD/THB เพิ่มอีกชั้น (บาทแข็ง = ผลตอบแทนจริงลดลง) · "
            "ภาษีหัก ณ ที่จ่ายปันผลตั้งค่าเริ่มต้น 15% ตามอนุสัญญาภาษีซ้อนไทย-สหรัฐ (ปรับได้) · "
            "ยังไม่รวมภาษี capital gains และค่าธรรมเนียมแปลงเงิน")

# ══════════════════════════════════════════════════════════════
#  TAB 6 — AI CHAT  (Claude) — เพื่อนคุย + ที่ปรึกษา
# ══════════════════════════════════════════════════════════════
with tab_chat:
    col_ch, _ = st.columns([3, 2])
    with col_ch:
        st.markdown('<div class="section-title">🤖 AI ที่ปรึกษาการลงทุน (Claude)</div>',
                    unsafe_allow_html=True)
        st.caption("ผู้ช่วยวิเคราะห์เชิงปริมาณ ตอบตรงประเด็น · อ้างอิงตัวเลข DGV · ขับเคลื่อนโดย Claude")

        rt_ctx = ""
        if rt_quote:
            rt_ctx = f"""
• ราคา Real-time (Finnhub): {fmt_p(rt_quote['c'])} (เปลี่ยน {price_chg:+.2f} / {price_chg_pct:+.2f}%)
• High วันนี้: {fmt_p(rt_quote['h'])} · Low: {fmt_p(rt_quote['l'])} · Open: {fmt_p(rt_quote['o'])}"""

        # ── บริบทพยากรณ์ขั้นสูง (5 โมเดล) ──
        fc_ctx = ""
        try:
            if adv is not None:
                fc_ctx = (f"\n• พยากรณ์ขั้นสูง: โมเดลแม่นสุด «{adv['best_name']}» (MAPE {adv['best_mape']:.1f}%) | "
                          f"Consensus 5 โมเดล → {adv['consensus_ret']:+.1f}%")
        except NameError:
            pass

        # ── บริบทข่าว (พาดหัวล่าสุด + sentiment) ──
        news_ctx = ""
        try:
            heads = (comp_news or []) + (gen_news or [])
            if heads:
                top_heads = "; ".join((n.get("headline", "") or "")[:90] for n in heads[:6])
                news_ctx = (f"\n• ข่าวล่าสุด (sentiment heuristic {sent_score:+d}): {top_heads}")
        except NameError:
            pass

        sys_ctx = f"""คุณคือ "DGV" ผู้ช่วยวิเคราะห์การลงทุนเชิงปริมาณ ตอบในสไตล์ผู้ช่วย AI มืออาชีพ แบบเดียวกับ ChatGPT หรือ Gemini — เป็นกลาง กระชับ ชัดเจน ตรงประเด็น และมีโครงสร้างอ่านง่าย

แนวทางการตอบ:
• ตอบตรงคำถามทันที ไม่เกริ่นยืดยาว ไม่ออกตัว
• ใช้น้ำเสียงทางการที่เป็นมิตร หลีกเลี่ยงการลงท้าย "ครับ" ทุกประโยค และไม่ใส่อิโมจิที่ไม่จำเป็น
• จัดระเบียบคำตอบด้วยหัวข้อ/บูลเล็ตเมื่อช่วยให้อ่านง่าย สรุปประเด็นสำคัญขึ้นก่อน
• อ้างอิงตัวเลขจริงด้านล่างเสมอเวลาวิเคราะห์ และอธิบายความหมายของตัวเลขสั้น ๆ
• ให้ภาพที่สมดุล ระบุทั้งจุดแข็งและความเสี่ยง ไม่เชียร์เกินจริงและไม่ขู่เกินจริง
• เชื่อมโยงข่าว (ถ้ามี) เข้ากับแนวโน้มราคาเมื่อผู้ใช้ถามถึงอนาคต/ข่าว
• ตอบเป็นภาษาไทยเป็นค่าเริ่มต้น และสลับภาษาตามที่ผู้ใช้ใช้

ข้อมูลเชิงปริมาณปัจจุบันของ {symbol}:{rt_ctx}
• CAGR: {m['cagr']:+.1f}%/ปี | Sharpe: {m['sharpe']:.2f} | Sortino: {m['sortino']:.2f} | Calmar: {m['calmar']:.2f}
• Max Drawdown: {m['mdd']:.1f}% | VaR 95%: {m['var95']:.2f}%/วัน | Expected Shortfall: {m['es95']:.2f}%
• Win Rate Backtest: {bt['winrate']}% ({bt['wins']}W/{bt['losses']}L)
• Momentum Score: {m['momentum']:+.1f}% | Z-Score: {m['zscore']:+.2f}
• RSI: {m['rsi']:.1f} | MACD: {'Bullish' if m['macd']>m['macd_sig'] else 'Bearish'}
• Linear Trend: {m['trend_slope']:+.1f}%/ปี | R²={m['r2']:.2f}
• Volatility: Short={m['vol_s']:.1f}% Long={m['vol_l']:.1f}%
• ผลตอบแทน: 1M {m['ret_1m']:+.1f}% · 3M {m['ret_3m']:+.1f}% · 1Y {m['ret_1y']:+.1f}%
• Composite Score: {m['score']}/100 → {m['verdict']}{fc_ctx}{news_ctx}"""

        # Quick prompts (ปุ่มเริ่มต้นบทสนทนา)
        st.markdown("**💬 เริ่มจากคำถามยอดฮิต:**")
        qp1, qp2, qp3 = st.columns(3)
        quick = None
        with qp1:
            if st.button(f"📈 {symbol} น่าลงทุนไหม?", use_container_width=True):
                quick = f"ช่วยสรุปหน่อยว่า {symbol} ตอนนี้น่าลงทุนไหม จากตัวเลขที่มี?"
        with qp2:
            if st.button("⚠️ เสี่ยงแค่ไหน?", use_container_width=True):
                quick = f"{symbol} มีความเสี่ยงระดับไหน ถ้าผมลงเงินไป จะขาดทุนหนักสุดได้แค่ไหน?"
        with qp3:
            if st.button("💡 ควรลงเท่าไหร่?", use_container_width=True):
                quick = f"ถ้าผมมีเงินก้อนหนึ่ง ควรแบ่งลงทุนใน {symbol} สัดส่วนเท่าไหร่ดี?"

        # Chat history render
        chat_html = '<div class="chat-wrap">'
        for msg in st.session_state.chat:
            content = msg["content"].replace(chr(10), "<br>")
            if msg["role"] == "assistant":
                chat_html += f'<div class="msg-row"><div class="av ai">C</div><div class="bub ai-b">{content}</div></div>'
            else:
                chat_html += f'<div class="msg-row u"><div class="av usr">คุณ</div><div class="bub u-b">{content}</div></div>'
        chat_html += '</div>'
        st.markdown(chat_html, unsafe_allow_html=True)

        typed = st.chat_input("ถาม DGV ได้เลย เช่น ความเสี่ยง ผลตอบแทน หรือการจัดสรรเงินลงทุน",
                              key="main_chat")
        user_msg = quick or typed

        if user_msg:
            st.session_state.chat.append({"role": "user", "content": user_msg})
            try:
                client = get_claude_client()
                hist = [
                    {"role": m_["role"], "content": m_["content"]}
                    for m_ in st.session_state.chat[1:-1]
                ]
                with st.spinner("🤖 DGV กำลังวิเคราะห์ตัวเลขและเรียบเรียงคำตอบ..."):
                    resp = client.messages.create(
                        model=CLAUDE_MODEL,
                        max_tokens=1024,
                        system=sys_ctx,
                        messages=hist + [{"role": "user", "content": user_msg}],
                    )
                reply = "".join(
                    block.text for block in resp.content if block.type == "text"
                )
            except Exception as e:
                reply = (f"ขออภัยครับ ตอนนี้ผมเชื่อมต่อ AI ไม่ได้ 😅 "
                         f"(ลองเช็คว่าตั้งค่า ANTHROPIC_API_KEY ใน secrets แล้วหรือยัง)\n\n`{e}`")
            st.session_state.chat.append({"role": "assistant", "content": reply})
            st.rerun()

        if st.button("🗑️ ล้างบทสนทนา"):
            st.session_state.chat = st.session_state.chat[:1]
            st.rerun()

# ─────────────────────────────────────────────────────────────
#  REAL-TIME GUIDE (Expander) — แนะนำการหากราฟเรียลไทม์
# ─────────────────────────────────────────────────────────────
with st.expander("📡 วิธีดู/หากราฟแบบเรียลไทม์ (Real-time) — คำแนะนำ"):
    st.markdown("""
**ในแอปนี้ (อัปเดตแล้ว ✅):** กราฟ Real-time ด้านบนเป็น **ข้อมูลจริง** — แท่งราคา intraday
(1m/5m/15m/1h) จาก yfinance + จุดราคา live ล่าสุดจาก Finnhub อัปเดตเองทุก ~3 วินาที
โดยไม่ต้องรีเฟรชหน้า สลับช่วงเวลา/สไตล์ (เส้น↔แท่งเทียน) ได้จากปุ่มเหนือกราฟ

**Symbol ที่รองรับ live price (Finnhub) ในแอปนี้:**
- หุ้น/ETF สหรัฐ: `AAPL`, `NVDA`, `MSFT`, `SPY`, `QQQ`, `ARKK` ฯลฯ
- คริปโต: `BTC-USD`, `ETH-USD`, `SOL-USD`, `BNB-USD`, `XRP-USD` (→ Binance)
- Forex: `EURUSD=X`, `GBPUSD=X`, `USDJPY=X`, `USDTHB=X` (→ OANDA)
- ⚠️ ทองคำ `GC=F`, เงิน `SI=F`, น้ำมัน `CL=F`, ดัชนี `^GSPC/^IXIC/^DJI` ใช้แท่ง intraday
  จาก yfinance (Finnhub free ไม่รองรับ live price แต่กราฟ intraday ยังเห็นได้)
    """)

# ─────────────────────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
fcol1, fcol2 = st.columns([1, 3])
with fcol1:
    if st.button("🔄 โหลดข้อมูลวิเคราะห์ใหม่ทั้งหมด"):
        fetch_realtime_quote.clear()
        fetch_intraday.clear()
        fetch_data.clear()
        fetch_watchlist_scores.clear()
        monte_carlo_forecast.clear()
        advanced_forecast.clear()
        fetch_company_news.clear()
        fetch_general_news.clear()
        st.rerun()
with fcol2:
    st.caption("กราฟ Real-time (intraday จริง) อัปเดตเองทุก 3 วินาที (fragment) · "
               "ปุ่มนี้โหลดข้อมูลย้อนหลัง + ตัวเลขวิเคราะห์ + พยากรณ์ + ข่าวใหม่ทั้งหมด · "
               "DGV เป็นเครื่องมือวิเคราะห์เชิงปริมาณ")
