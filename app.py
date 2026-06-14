"""
DGV Investment Analyzer — Mathematical Deep Analysis (Clean Edition)
วิเคราะห์การลงทุนด้วยคณิตศาสตร์ย้อนหลัง 10 ปี
ราคา Real-time จาก Finnhub | ข้อมูลย้อนหลังจาก yfinance + Stooq | AI โดย Claude (Anthropic)

Clean Edition: เมนูย้ายมาด้านซ้าย (sidebar) · โหมดมือใหม่ที่ซ่อนของขั้นสูง ·
   ดีไซน์เท่ขึ้น เรียบขึ้น · อนิเมชั่นเท่าที่จำเป็น · ฟังก์ชันคณิตศาสตร์ครบเหมือนเดิม
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

# -------------------------------------------------------------
#  PAGE CONFIG  —  เปิด sidebar ค้างไว้ (เมนูอยู่ซ้าย)
# -------------------------------------------------------------
st.set_page_config(
    page_title="DGV · Investment Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="auto",
)

# -------------------------------------------------------------
#  GLOBAL CSS  —  Dark "Terminal" theme (calmer + left nav)
# -------------------------------------------------------------
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

/* =============== KEYFRAMES (เหลือเท่าที่จำเป็น) =============== */
@keyframes fadeInUp {
  from { opacity:0; transform: translateY(14px); }
  to   { opacity:1; transform: translateY(0); }
}
@keyframes fadeIn { from { opacity:0; } to { opacity:1; } }
@keyframes slideInLeft {
  from { opacity:0; transform: translateX(-14px); }
  to   { opacity:1; transform: translateX(0); }
}
@keyframes scaleIn {
  from { opacity:0; transform: scale(.94); }
  to   { opacity:1; transform: scale(1); }
}
@keyframes pulse {
  0%,100% { opacity:1; transform: scale(1); }
  50%     { opacity:.35; transform: scale(.7); }
}
@keyframes ringSweep {
  from { stroke-dashoffset: var(--dash-full); }
  to   { stroke-dashoffset: var(--dash-target); }
}
@keyframes blink { 0%,100% { opacity:1; } 50% { opacity:.2; } }

/* App background — radial glow แบบนิ่ง (ไม่เลื่อนไปมา) */
html, body, [class*="css"], .stApp {
  font-family: 'Space Grotesk','DM Sans', sans-serif !important;
  color: var(--ink) !important;
}
.stApp {
  background:
    radial-gradient(1100px 520px at 18% -8%, rgba(230,195,92,0.07), transparent 60%),
    radial-gradient(900px 520px at 95% 8%, rgba(52,227,196,0.05), transparent 55%),
    var(--bg) !important;
}
.block-container { padding-top: 1.2rem; animation: fadeIn .5s ease both; }

.dm-serif { font-family:'DM Serif Display',serif; }
.mono { font-family:'JetBrains Mono',monospace; }

/* -- Sidebar (เมนูซ้าย) ------------------------------ */
section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0a0e18 0%, #0b0f1a 100%) !important;
  border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] > div { padding-top: 14px; }
.side-brand { padding: 2px 6px 12px; }
.side-mark {
  font-family:'DM Serif Display',serif; font-size: 30px; line-height:1; letter-spacing:-1.5px;
  background: linear-gradient(120deg, var(--gold), #fff4cf 50%, var(--gold-dim));
  -webkit-background-clip:text; background-clip:text; color:transparent;
  filter: drop-shadow(0 1px 10px var(--glow-gold));
}
.side-brand-sub {
  font-family:'JetBrains Mono',monospace; font-size:9.5px; letter-spacing:3px;
  text-transform:uppercase; color: var(--muted); margin-top:3px;
}
.side-divider { height:1px; background: var(--border); margin: 12px 0; }
.side-cap { font-size:11px; color: var(--muted); line-height:1.6; }

/* radio → vertical nav (ซ่อนวงกลม + ทำเป็นเมนู) */
section[data-testid="stSidebar"] [role="radiogroup"] { gap: 3px; }
section[data-testid="stSidebar"] [role="radiogroup"] > label {
  padding: 9px 13px !important; border-radius: 10px; cursor: pointer;
  font-family:'Space Grotesk',sans-serif; font-size: 14px !important; font-weight:500;
  color: var(--muted) !important; transition: background .15s ease, color .15s ease;
  border: 1px solid transparent;
}
section[data-testid="stSidebar"] [role="radiogroup"] > label:hover {
  background: rgba(255,255,255,0.04); color: var(--ink) !important;
}
section[data-testid="stSidebar"] [role="radiogroup"] > label > div:first-child { display:none !important; }
section[data-testid="stSidebar"] [role="radiogroup"] > label:has(input:checked) {
  background: linear-gradient(100deg, rgba(230,195,92,0.16), rgba(230,195,92,0.04));
  color: var(--gold) !important; border-color: rgba(230,195,92,0.22);
  box-shadow: inset 2px 0 0 var(--gold);
}

/* -- Compact top header (แทน masthead เดิม) ----------- */
.top-head {
  display:flex; align-items:center; gap: 22px; flex-wrap:wrap;
  background: linear-gradient(135deg, rgba(255,255,255,0.035), rgba(255,255,255,0.01));
  border: 1px solid var(--border); border-radius: 14px;
  padding: 14px 20px; margin: -4px 0 18px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.3);
  animation: fadeInUp .5s ease both;
}
.th-left { display:flex; align-items:baseline; gap:10px; }
.th-sym { font-family:'JetBrains Mono',monospace; font-weight:700; font-size:22px; color:#fff; letter-spacing:.5px; }
.th-name { font-size:13px; color: var(--muted); }
.th-price { display:flex; align-items:baseline; gap:12px; }
.th-px { font-family:'JetBrains Mono',monospace; font-weight:600; font-size:22px; color: var(--gold); }
.th-chg { font-family:'JetBrains Mono',monospace; font-size:13px; font-weight:600; }
.th-chg.pos { color: var(--green); } .th-chg.neg { color: var(--red); }
.th-meta { margin-left:auto; text-align:right; }
.th-page { font-family:'DM Serif Display',serif; font-size:16px; color: var(--ink); }
.th-src { font-size:10px; color: var(--muted); font-family:'JetBrains Mono',monospace; letter-spacing:.5px; }

/* -- Beginner hint ----------------------------------- */
.beginner-hint {
  background: linear-gradient(135deg, rgba(46,230,160,0.08), rgba(52,227,196,0.04));
  border: 1px solid rgba(46,230,160,0.2); border-left: 3px solid var(--green);
  border-radius: 10px; padding: 11px 15px; margin-bottom: 16px;
  font-size: 13px; color: var(--ink); line-height:1.6;
  animation: fadeInUp .5s ease both;
}
.beginner-hint b { color: var(--green); }

/* -- Real-time badge / dot ---------------------------- */
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

/* -- Finnhub price panel (glass) ---------------------- */
.rt-panel {
  background: linear-gradient(160deg, rgba(255,255,255,0.04), rgba(255,255,255,0.01));
  backdrop-filter: blur(14px);
  border: 1px solid var(--border);
  border-radius: 14px; padding: 16px 20px; margin-bottom: 18px;
  display: grid; grid-template-columns: repeat(auto-fit, minmax(112px,1fr)); gap: 14px;
  box-shadow: 0 6px 30px rgba(0,0,0,0.35);
  animation: fadeInUp .5s ease both;
}
.rt-item { animation: scaleIn .4s ease both; }
.rt-item-label { font-size:10px; letter-spacing:1.5px; text-transform:uppercase;
  color: var(--muted); margin-bottom:4px; font-family:'JetBrains Mono',monospace; }
.rt-item-val { font-family:'JetBrains Mono',monospace; font-size:17px; font-weight:600; color:#fff;
  transition: color .3s ease; }
.rt-item-val.pos { color: var(--green); text-shadow:0 0 12px rgba(46,230,160,.4); }
.rt-item-val.neg { color: var(--red);   text-shadow:0 0 12px rgba(255,93,108,.35); }
.rt-item-val.gold{ color: var(--gold);  text-shadow:0 0 14px var(--glow-gold); }

/* -- Section headers ---------------------------------- */
.section-title {
  font-family:'DM Serif Display',serif; font-size: 21px; color: var(--ink);
  margin-bottom: 14px; display:flex; align-items:center; gap:10px;
  animation: slideInLeft .4s ease both;
}
.section-title::before {
  content:''; width:4px; height:20px; border-radius:3px;
  background: linear-gradient(var(--gold), var(--cyan));
  box-shadow: 0 0 10px var(--glow-gold);
}

/* -- Metric cards (glass + glow rail) ----------------- */
.mcard {
  background: linear-gradient(160deg, rgba(255,255,255,0.045), rgba(255,255,255,0.012));
  border: 1px solid var(--border); border-radius: 12px;
  padding: 13px 15px; position: relative; overflow:hidden;
  transition: transform .2s cubic-bezier(.2,.8,.2,1), box-shadow .2s ease, border-color .2s ease;
  animation: fadeInUp .45s ease both;
}
.mcard:hover { transform: translateY(-3px) scale(1.012);
  box-shadow:0 12px 30px rgba(0,0,0,.45); border-color: var(--border-hi); }
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
.mcard.blue::before { background: var(--blue); box-shadow:0 0 14px rgba(91,141,239,.45); }

/* -- Score ring / verdict ----------------------------- */
.score-ring {
  display:flex; align-items:center; gap:26px;
  background: linear-gradient(135deg, #0d1322, #15203a);
  border: 1px solid var(--border); border-radius: 16px;
  padding: 20px 26px; margin-bottom: 18px; position:relative; overflow:hidden;
  box-shadow: inset 0 1px 0 rgba(255,255,255,.05);
  animation: scaleIn .5s cubic-bezier(.2,.8,.2,1) both;
}
.score-ring::after { content:''; position:absolute; right:-40px; top:-40px;
  width:180px; height:180px; border-radius:50%;
  background: radial-gradient(var(--glow-gold), transparent 70%); }

.gauge-wrap { position:relative; width:120px; height:120px; flex-shrink:0; }
.gauge-svg { transform: rotate(-90deg); }
.gauge-track { fill:none; stroke: rgba(255,255,255,0.07); stroke-width:11; }
.gauge-prog  { fill:none; stroke-width:11; stroke-linecap:round;
  stroke-dasharray: var(--circ);
  animation: ringSweep 1.3s cubic-bezier(.2,.8,.2,1) forwards;
  filter: drop-shadow(0 0 8px currentColor); }
.gauge-center { position:absolute; inset:0; display:flex; flex-direction:column;
  align-items:center; justify-content:center; }
.gauge-num { font-family:'DM Serif Display',serif; font-size:38px; line-height:1;
  background: linear-gradient(120deg,var(--gold),#fff4cf,var(--gold-dim));
  -webkit-background-clip:text; background-clip:text; color:transparent;
  filter: drop-shadow(0 0 12px var(--glow-gold)); }
.gauge-max { font-size:10px; color:#7d8799; margin-top:-2px; }

.score-label { font-size:11px; color: var(--muted); letter-spacing:2px; text-transform:uppercase; }
.score-verdict { font-size:22px; font-weight:700; color:#fff; margin-top:4px; }

/* -- Signal rows -------------------------------------- */
.sig-row { display:flex; align-items:center; gap:11px; padding:8px 0;
  border-bottom:1px solid var(--border); font-size:13px;
  animation: slideInLeft .4s ease both; transition: background .2s ease; }
.sig-row:hover { background: rgba(255,255,255,0.02); }
.sig-icon { font-size:16px; width:22px; text-align:center; }
.sig-text { flex:1; color: var(--ink); }
.sig-badge { font-family:'JetBrains Mono',monospace; font-size:11px; padding:2px 8px;
  border-radius:6px; background: rgba(255,255,255,0.05); color: var(--muted);
  border:1px solid var(--border); }

/* -- Chat --------------------------------------------- */
.chat-wrap { max-height:380px; overflow-y:auto; padding:14px;
  border:1px solid var(--border); border-radius:14px;
  background: linear-gradient(160deg, rgba(255,255,255,0.03), rgba(255,255,255,0.008));
  margin-bottom:8px; scroll-behavior:smooth; }
.chat-wrap::-webkit-scrollbar { width:7px; }
.chat-wrap::-webkit-scrollbar-thumb { background: rgba(230,195,92,0.25); border-radius:6px; }
.msg-row { display:flex; gap:8px; margin-bottom:12px; align-items:flex-start;
  animation: fadeInUp .35s ease both; }
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

/* -- Calc result -------------------------------------- */
.calc-result { background: linear-gradient(135deg,#0d1322,#15203a);
  border:1px solid var(--border); color:#fff; border-radius:14px; padding:16px 20px;
  animation: fadeInUp .45s ease both; }
.calc-row { display:flex; justify-content:space-between; padding:6px 0;
  border-bottom:1px solid var(--border); font-size:13px; }
.calc-row:last-child { border-bottom:none; }
.calc-row span:last-child { font-family:'JetBrains Mono',monospace; color: var(--gold); font-weight:600; }

/* -- Progress bar ------------------------------------- */
.pb-bg { background: rgba(255,255,255,0.07); border-radius:6px; height:10px; width:100%; overflow:hidden; }
.pb-fill { height:10px; border-radius:6px; transition: width 1s cubic-bezier(.2,.8,.2,1);
  box-shadow:0 0 12px currentColor; }

/* -- Rank table --------------------------------------- */
.rank-table { width:100%; border-collapse: collapse; font-size:13px;
  background: rgba(255,255,255,0.02); border-radius:12px; overflow:hidden;
  animation: fadeInUp .5s ease both; }
.rank-table th { background: rgba(255,255,255,0.04); color: var(--gold); padding:11px 12px;
  text-align:left; font-family:'JetBrains Mono',monospace; font-weight:600;
  font-size:11px; letter-spacing:1px; border-bottom:1px solid var(--border); }
.rank-table td { padding:11px 12px; border-bottom:1px solid var(--border); vertical-align:middle; color:var(--ink); }
.rank-table tr { transition: background .2s ease; }
.rank-table tr:hover td { background: rgba(255,255,255,0.05); }
.rank-num { font-family:'DM Serif Display',serif; font-size:21px; color: var(--gold); }
.rank-ticker { font-family:'JetBrains Mono',monospace; font-weight:600; font-size:14px; color:var(--ink); }

/* -- Info pill / forecast box ------------------------- */
.fc-banner { background: linear-gradient(135deg, rgba(91,141,239,0.10), rgba(168,119,230,0.06));
  border:1px solid var(--border); border-radius:14px; padding:14px 18px; margin-bottom:14px;
  font-size:13px; color:var(--ink); animation: fadeInUp .45s ease both; }
.fc-banner b { color: var(--gold); }

/* -- Streamlit widgets (dark) ------------------------- */
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

/* alerts */
.stAlert { background: rgba(255,255,255,0.04) !important; border:1px solid var(--border) !important;
  border-radius:12px !important; color: var(--ink) !important; }

/* expander */
.streamlit-expanderHeader, [data-testid="stExpander"] summary {
  background: rgba(255,255,255,0.03) !important; border-radius:10px !important; color: var(--ink) !important; }

/* =============== MOBILE RESPONSIVE (จอมือถือ ≤640px) =============== */
@media (max-width: 640px) {
  /* คอลัมน์ทุกชุด → เรียงลงแนวตั้ง เพื่อให้กราฟ/การ์ด/ปุ่มเต็มความกว้าง ไม่ถูกบีบจนหาย */
  div[data-testid="stHorizontalBlock"] {
    flex-direction: column !important;
    gap: 10px !important;
  }
  div[data-testid="stHorizontalBlock"] > div {
    width: 100% !important;
    flex: 1 1 100% !important;
    min-width: 0 !important;
  }

  .block-container {
    padding-left: 0.6rem !important;
    padding-right: 0.6rem !important;
    padding-top: 0.8rem;
  }

  /* แถบหัวบนสุด: ย่อให้พอดีจอ */
  .top-head { gap: 8px 14px; padding: 12px 14px; }
  .th-sym, .th-px { font-size: 18px; }
  .th-chg { font-size: 12px; }
  .th-meta { margin-left: 0; text-align: left; width: 100%; }
  .th-page { font-size: 15px; }

  /* วงแหวนคะแนน: เรียงลงไม่ให้ล้นขอบ */
  .score-ring { flex-direction: column; gap: 14px; text-align: center; padding: 18px 16px; }
  .score-ring::after { display: none; }

  /* แผง real-time: 2 คอลัมน์กำลังดี */
  .rt-panel {
    grid-template-columns: repeat(2, 1fr) !important;
    gap: 10px; padding: 12px 14px;
  }

  .section-title { font-size: 18px; }
  .mcard-value { font-size: 18px; }
  .fc-banner, .beginner-hint { font-size: 12px; }

  /* กล่องแชต: เตี้ยลงให้เห็นช่องพิมพ์และปุ่ม */
  .chat-wrap { max-height: 46vh; }
  .bub { max-width: 88%; }

  /* ตารางกว้าง ๆ ให้เลื่อนแนวนอนได้ ไม่ดันจนล้นจอ */
  .rank-table {
    display: block;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
#  CLIENTS  (Finnhub + Claude)
# -------------------------------------------------------------
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

# -------------------------------------------------------------
#  SESSION STATE
# -------------------------------------------------------------
for k, v in [
    ("history", {}),
    ("chat", [{"role": "assistant", "content":
               "สวัสดีครับ ผม DGV 👋\n\n"
               "ถามได้ทุกเรื่องเลยนะ — แต่ที่ผมถนัดสุดคือวิเคราะห์การลงทุนจากตัวเลขจริง "
               "เช่น สินทรัพย์ที่คุณกำลังดูเสี่ยงแค่ไหน ผลตอบแทนย้อนหลังเป็นยังไง หรือควรจัดพอร์ตแบบไหน\n\n"
               "อยากเริ่มตรงไหนดีครับ?"}]),
    ("last_refresh", 0),
]:
    if k not in st.session_state:
        st.session_state[k] = v

# -------------------------------------------------------------
#  ASSET GROUPS (กองทุน/ETF/คริปโต/หุ้น/ดัชนี)
# -------------------------------------------------------------
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

# -------------------------------------------------------------
#  REAL-TIME QUOTE (Finnhub)
# -------------------------------------------------------------
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

# -------------------------------------------------------------
#  INTRADAY (Real-time จริง) — yfinance 1m/5m/15m/1h
# -------------------------------------------------------------
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

# -------------------------------------------------------------
#  NEWS (Finnhub)
# -------------------------------------------------------------
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

# -------------------------------------------------------------
#  MATH FUNCTIONS
# -------------------------------------------------------------
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

# -------------------------------------------------------------
#  FORECAST — Monte Carlo (GBM + fat tail) + Linear extrapolation
# -------------------------------------------------------------
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

    # -- ประมาณความอ้วนของหาง (fat tail) จาก excess kurtosis --
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

# -------------------------------------------------------------
#  ADVANCED FORECAST — 5 เส้นแนวโน้มที่ดีที่สุด (คณิตศาสตร์ขั้นสูง)
#  Deterministic (ไม่ใช่การสุ่ม) — จัดอันดับด้วย out-of-sample error
# -------------------------------------------------------------
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

    # -- กรอบความผันผวน 3-sigma (diffusion cone) — กันโมเดลเหวี่ยงหลุดจริง --
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

# -------------------------------------------------------------
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

# Plotly dark theme helper
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

# -------------------------------------------------------------
#  FETCH DATA (historical) — yfinance + Stooq fallback
# -------------------------------------------------------------
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

# -------------------------------------------------------------
#  FUNDAMENTALS (Finnhub) — ปัจจัยพื้นฐาน
# -------------------------------------------------------------
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

# -------------------------------------------------------------
#  BETA / ALPHA vs BENCHMARK (เทียบดัชนีอ้างอิง เช่น S&P 500)
# -------------------------------------------------------------
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

# -------------------------------------------------------------
#  PORTFOLIO — correlation + efficient frontier (Markowitz, numpy)
# -------------------------------------------------------------
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

# -------------------------------------------------------------
#  STRATEGY vs BUY-AND-HOLD (เทียบกลยุทธ์กับการถือยาว สุทธิหลังค่าธรรมเนียม)
# -------------------------------------------------------------
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

# -------------------------------------------------------------
#  USD/THB rate (สำหรับมุมนักลงทุนไทย)
# -------------------------------------------------------------
@st.cache_data(ttl=900, show_spinner=False)
def fetch_usdthb():
    q = fetch_realtime_quote("USDTHB=X")
    if q and q.get("c", 0) > 0:
        return float(q["c"])
    d = fetch_data("USDTHB=X")
    if d is not None and len(d):
        return float(d["Close"].iloc[-1])
    return 36.0

# -------------------------------------------------------------
#  MY PORTFOLIO — วิเคราะห์พอร์ตจริงของผู้ใช้
# -------------------------------------------------------------
@st.cache_data(ttl=120, show_spinner=False)
def analyze_holdings(holdings_tuple, rf=0.05):
    """holdings_tuple: tuple ของ (ticker, shares, avg_cost) → คืนรายตัว + เมตริกระดับพอร์ต"""
    rows = []
    for tk, sh, cost in holdings_tuple:
        tk = str(tk).upper().replace("/", "").strip()
        try:
            sh = float(sh); cost = float(cost or 0)
        except (TypeError, ValueError):
            continue
        if not tk or sh <= 0:
            continue
        d = fetch_data(tk)
        if d is None or len(d) < 30:
            rows.append({"ticker": tk, "shares": sh, "avg_cost": cost, "price": None,
                         "value": 0.0, "cost_value": sh * cost, "pnl": 0.0,
                         "pnl_pct": 0.0, "ok": False})
            continue
        q = fetch_realtime_quote(tk)
        price = float(q["c"]) if q and q.get("c", 0) > 0 else float(d["Close"].iloc[-1])
        val = price * sh
        costv = cost * sh
        rows.append({"ticker": tk, "shares": sh, "avg_cost": cost, "price": price,
                     "value": val, "cost_value": costv, "pnl": val - costv,
                     "pnl_pct": ((val - costv) / costv * 100 if costv > 0 else 0.0),
                     "ok": True})

    total_val = sum(r["value"] for r in rows)
    total_cost = sum(r["cost_value"] for r in rows)
    for r in rows:
        r["weight"] = (r["value"] / total_val * 100) if total_val > 0 else 0.0

    metrics = None
    ok_ticks = [r["ticker"] for r in rows if r["ok"] and r["value"] > 0]
    if ok_ticks and total_val > 0:
        try:
            if len(ok_ticks) >= 2:
                rdf = portfolio_returns_frame(ok_ticks)
            else:
                d1 = fetch_data(ok_ticks[0])
                rdf = pd.DataFrame({ok_ticks[0]: _naive_index(d1["Close"].pct_change().dropna())}).dropna()
            if rdf is not None and len(rdf) >= 60:
                wmap = {r["ticker"]: r["value"] for r in rows if r["ticker"] in rdf.columns}
                wsum = sum(wmap.values())
                w = np.array([wmap[c] / wsum for c in rdf.columns])
                port_ret = (rdf.values * w).sum(axis=1)
                port_ret = pd.Series(port_ret, index=rdf.index)
                yrs = len(port_ret) / 252
                cum = float((1 + port_ret).prod())
                cagr_v = (cum ** (1 / yrs) - 1) * 100 if yrs > 0 and cum > 0 else 0.0
                vol = float(port_ret.std() * np.sqrt(252) * 100)
                sharpe = float((port_ret.mean() - rf / 252) / (port_ret.std() + 1e-12) * np.sqrt(252))
                eq = (1 + port_ret).cumprod()
                mdd = float(((eq - eq.cummax()) / eq.cummax()).min() * 100)
                # beta vs S&P 500
                beta = None
                bench = fetch_data("^GSPC")
                if bench is not None:
                    bret = _naive_index(bench["Close"].pct_change().dropna())
                    j = pd.concat([port_ret.rename("p"), bret.rename("b")], axis=1).dropna()
                    if len(j) >= 60:
                        cov = np.cov(j["p"].values, j["b"].values)
                        if cov[1, 1] > 0:
                            beta = round(float(cov[0, 1] / cov[1, 1]), 3)
                # avg correlation (diversification)
                avg_corr = None
                if len(rdf.columns) >= 2:
                    cm = rdf.corr().values
                    iu = np.triu_indices_from(cm, k=1)
                    avg_corr = round(float(np.mean(cm[iu])), 3)
                metrics = {"cagr": round(cagr_v, 1), "vol": round(vol, 1),
                           "sharpe": round(sharpe, 2), "mdd": round(mdd, 1),
                           "beta": beta, "avg_corr": avg_corr, "n_days": len(port_ret)}
        except Exception:
            metrics = None

    return {"rows": rows, "total_val": total_val, "total_cost": total_cost,
            "total_pnl": total_val - total_cost,
            "total_pnl_pct": ((total_val - total_cost) / total_cost * 100) if total_cost > 0 else 0.0,
            "metrics": metrics}

# -------------------------------------------------------------
#  SIDEBAR — เมนูหลัก (ย้ายมาด้านซ้าย) + โหมดมือใหม่
# -------------------------------------------------------------
NAV = [
    ("overview", "ภาพรวม",         "🏠"),
    ("fund",     "ปัจจัยพื้นฐาน",   "🏛️"),
    ("chart",    "กราฟราคา",        "📈"),
    ("forecast", "พยากรณ์อนาคต",    "🔮"),
    ("news",     "ข่าว",            "📰"),
    ("rank",     "อันดับสินทรัพย์",  "🏆"),
    ("portfolio","จัดพอร์ต",        "🧺"),
    ("myport",   "พอร์ตของฉัน",     "💼"),
    ("income",   "วางแผนเงิน",      "💰"),
    ("chat",     "ถาม AI",          "🤖"),
]
SIMPLE_PAGES = {"overview", "chart", "forecast", "income", "chat"}
_NAV_TITLE = {k: f"{ic} {lbl}" for k, lbl, ic in NAV}

with st.sidebar:
    st.markdown("""
    <div class="side-brand">
      <div class="side-mark">DGV</div>
      <div class="side-brand-sub">Investment Analyzer</div>
    </div>
    """, unsafe_allow_html=True)

    symbol = st.text_input(
        "ค้นหาสินทรัพย์", "AAPL",
        placeholder="เช่น AAPL, BTC-USD, GLD",
        label_visibility="collapsed",
    ).upper().replace("/", "").strip()

    simple_mode = st.toggle(
        "โหมดมือใหม่ · เรียบง่าย", value=True,
        help="ซ่อนเครื่องมือขั้นสูง แสดงเฉพาะสิ่งที่จำเป็น เหมาะกับผู้เริ่มต้น "
             "ปิดสวิตช์เพื่อปลดล็อกทุกเครื่องมือ")

    st.markdown('<div class="side-divider"></div>', unsafe_allow_html=True)

    visible = [(k, lbl, ic) for k, lbl, ic in NAV
               if (not simple_mode or k in SIMPLE_PAGES)]
    labels = [f"{ic}  {lbl}" for _, lbl, ic in visible]
    choice = st.radio("เมนู", labels, label_visibility="collapsed")
    page = visible[labels.index(choice)][0]

    st.markdown('<div class="side-divider"></div>', unsafe_allow_html=True)
    if simple_mode:
        st.markdown('<div class="side-cap">กำลังใช้ <b style="color:#2ee6a0">โหมดมือใหม่</b> — '
                    'เปิดสวิตช์ด้านบนเพื่อปลดล็อกเครื่องมือขั้นสูง '
                    '(ปัจจัยพื้นฐาน · ข่าว · อันดับ · จัดพอร์ต · พยากรณ์หลายโมเดล)</div>',
                    unsafe_allow_html=True)
    else:
        st.markdown('<div class="side-cap"><b style="color:#e6c35c">โหมดมืออาชีพ</b> — '
                    'แสดงทุกเครื่องมือและตัวเลขเชิงลึก</div>', unsafe_allow_html=True)

# -------------------------------------------------------------
#  FETCH: Historical + Real-time
# -------------------------------------------------------------
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

# -------------------------------------------------------------
#  COMPACT TOP HEADER (แทน masthead เดิม)
# -------------------------------------------------------------
_name    = WATCHLIST.get(symbol, symbol)
_chg_cls = "pos" if price_chg >= 0 else "neg"
_arrow   = "▲" if price_chg >= 0 else "▼"
_delta   = (f"{price_chg:+.4f} ({price_chg_pct:+.2f}%)" if is_fx
            else f"{price_chg:+.2f} ({price_chg_pct:+.2f}%)")
_src     = "Finnhub · real-time" if price_source == "finnhub" else "yfinance · ล่าสุด"
st.markdown(f"""
<div class="top-head">
  <div class="th-left">
    <div class="th-sym">{symbol}</div>
    <div class="th-name">{_name}</div>
  </div>
  <div class="th-price">
    <div class="th-px">{fmt_p(cur_price)}</div>
    <div class="th-chg {_chg_cls}">{_arrow} {_delta}</div>
  </div>
  <div class="th-meta">
    <div class="th-page">{_NAV_TITLE.get(page, "")}</div>
    <div class="th-src">{_src} · ข้อมูล {len(data)/252:.1f} ปี ({len(data):,} วัน)</div>
  </div>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
#  REAL-TIME PANEL + LIVE INTRADAY CHART (เฉพาะหน้าภาพรวม/กราฟ)
# -------------------------------------------------------------
_RT_INTERVAL, _RT_PERIOD, _rt_style = "5m", "5d", "เส้น"
_show_live = page in ("overview", "chart")

# ตัวเลือกช่วง/สไตล์กราฟ — โชว์เฉพาะโหมดมืออาชีพ (มือใหม่ใช้ค่าเริ่มต้น สะอาดตา)
if _show_live and not simple_mode and (get_finnhub_symbol(symbol) is not None or not is_fx):
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

    # -- กราฟ intraday จริง (yfinance) + จุดราคา live ล่าสุด (Finnhub) --
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
                    config={"displayModeBar": False, "responsive": True}, key=f"live_chart_{symbol}")
    st.caption(f"📡 กราฟ Real-time จริง · {_RT_INTERVAL} bars จาก yfinance ({len(intra)} แท่ง) · "
               f"จุดทอง = ราคา live ล่าสุดจาก Finnhub · เส้นประขาว = ราคาปิดก่อนหน้า")

# แสดงแผง live เฉพาะหน้าภาพรวม/กราฟ
if _show_live and get_finnhub_symbol(symbol) is not None:
    realtime_panel()
elif _show_live:
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
        st.plotly_chart(_fig0, use_container_width=True, config={"displayModeBar": False, "responsive": True},
                        key=f"intra0_{symbol}")
        st.caption(f"📊 กราฟ intraday จริง · {_RT_INTERVAL} bars จาก yfinance "
                   "(Finnhub free ไม่รองรับ live สำหรับสินทรัพย์นี้)")

# -------------------------------------------------------------
#  COMPUTE Math Analysis
# -------------------------------------------------------------
with st.spinner("กำลังวิเคราะห์คณิตศาสตร์..."):
    m   = full_math_analysis(data, symbol)
    bt  = winrate_backtest(data)

# ==============================================================
#  PAGE — OVERVIEW
# ==============================================================
if page == "overview":
    if simple_mode:
        st.markdown(
            '<div class="beginner-hint">💡 <b>อ่านยังไง:</b> คะแนนรวมด้านซ้าย (0–100) '
            'สรุปจากสถิติย้อนหลังล้วน ๆ ยิ่งสูงยิ่งแข็งแรงในอดีต '
            '<b>แต่ไม่ใช่คำทำนายอนาคต</b> · ดูตัวเลขสำคัญทางขวาประกอบ — '
            'อยากเจาะลึก ปิดสวิตช์ "โหมดมือใหม่" ที่เมนูซ้าย</div>',
            unsafe_allow_html=True)

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

        # -- จำเป็น (โชว์เสมอ) — เลือกเฉพาะตัวที่มือใหม่เข้าใจได้ --
        if rt_quote:
            mcard("PRICE (REAL-TIME)",
                  fmt_p(rt_quote['c']),
                  f"H: {fmt_p(rt_quote['h'])} · L: {fmt_p(rt_quote['l'])}",
                  "pos" if price_chg >= 0 else "neg")

        mcard("CAGR (ต่อปี)", f"{m['cagr']:+.1f}%",
              f"ผลตอบแทนทบต้น · ย้อนหลัง {len(data)/252:.0f} ปี",
              "pos" if m['cagr']>0 else "neg")
        mcard("SHARPE RATIO", f"{m['sharpe']:.2f}",
              "ผลตอบแทนเทียบความเสี่ยง (>1 ดี)",
              "pos" if m['sharpe']>=1 else "neg" if m['sharpe']<0 else "")
        mcard("MAX DRAWDOWN", f"{m['mdd']:.1f}%",
              "เคยร่วงแรงสุดจากจุดพีคกี่ %",
              "neg" if m['mdd']<-30 else "")
        mcard("MOMENTUM SCORE", f"{m['momentum']:+.1f}%",
              "แรงส่งราคาช่วงนี้ (บวก=ขาขึ้น)",
              "pos" if m['momentum']>0 else "neg")
        mcard("VOLATILITY (30D)", f"{m['vol_s']:.1f}%",
              f"ความผันผวน · ระยะยาว {m['vol_l']:.1f}%", "")

        # -- Beta / ชนะตลาด — เข้าใจง่าย เก็บไว้เป็นตัวหลัก --
        ba = beta_alpha_vs_benchmark(symbol, bench="^GSPC")
        if ba:
            mcard("BETA (เทียบ S&P 500)", f"{ba['beta']:.2f}",
                  ">1 = เหวี่ยงกว่าตลาด · <1 = นิ่งกว่าตลาด",
                  "neg" if ba['beta'] > 1.3 else "pos")
            mcard("ชนะ/แพ้ตลาด (1 ปี)", f"{ba['excess_1y']:+.1f}%",
                  f"{symbol} {ba['asset_1y']:+.1f}% vs S&P {ba['bench_1y']:+.1f}%",
                  "pos" if ba['excess_1y'] >= 0 else "neg")

        # -- ตัวเลขเชิงลึก (พับไว้ ลดความรกสำหรับมือใหม่) --
        with st.expander("🔬 ตัวเลขเชิงลึก (ขั้นสูง)", expanded=not simple_mode):
            mcard("SORTINO RATIO", f"{m['sortino']:.2f}",
                  "เหมือน Sharpe แต่นับเฉพาะความเสี่ยงขาลง",
                  "pos" if m['sortino']>=1 else "neg" if m['sortino']<0 else "")
            mcard("CALMAR RATIO", f"{m['calmar']:.2f}",
                  "CAGR / |MaxDD|", "pos" if m['calmar']>1 else "")
            mcard("VALUE AT RISK (95%)", f"{m['var95']:.2f}%",
                  "ขาดทุนสูงสุด/วัน ที่ระดับเชื่อมั่น 95%", "neg")
            mcard("LINEAR TREND", f"{m['trend_slope']:+.1f}%/ปี",
                  f"R²={m['r2']:.2f} · p={m['pval']:.3f}",
                  "pos" if m['trend_slope']>0 else "neg")
            mcard("Z-SCORE (60D)", f"{m['zscore']:+.2f}",
                  ">+2: Overbought | <-2: Oversold",
                  "neg" if abs(m['zscore'])>2 else "pos")
            if ba:
                mcard("ALPHA (ส่วนเกินตลาด/ปี)", f"{ba['alpha']:+.1f}%",
                      f"Correlation {ba['corr']:.2f} · R²={ba['r2']:.2f}",
                      "pos" if ba['alpha'] > 0 else "neg")

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

# ==============================================================
#  PAGE — FUNDAMENTALS (ปัจจัยพื้นฐาน)
# ==============================================================
elif page == "fund":
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

        st.info("📌 ปัจจัยพื้นฐานสะท้อน 'มูลค่ากิจการ' ส่วนหน้าอื่นวิเคราะห์ 'พฤติกรรมราคา' — "
                "นักลงทุนระยะยาวควรดูทั้งสองด้านประกอบกัน · ข้อมูลพื้นฐานอัปเดตช้ากว่าราคา (ตามรอบงบการเงิน)")

# ==============================================================
#  PAGE — CHART
# ==============================================================
elif page == "chart":
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

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False, "responsive": True})

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
        st.plotly_chart(fig_bt, use_container_width=True, config={"displayModeBar": False, "responsive": True})

    # -- กลยุทธ์ vs ถือยาว (Buy & Hold) สุทธิหลังค่าธรรมเนียม --
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
        st.plotly_chart(fig_sb, use_container_width=True, config={"displayModeBar": False, "responsive": True})

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

# ==============================================================
#  PAGE — FORECAST
# ==============================================================
elif page == "forecast":
    # ========== ส่วนที่ 1: 5 เส้นแนวโน้มที่ดีที่สุด (Advanced Models) ==========
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
        st.plotly_chart(fig_adv, use_container_width=True, config={"displayModeBar": False, "responsive": True})

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

    # ========== ส่วนที่ 2: Monte Carlo (เส้นทางจำลองความน่าจะเป็น) ==========
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

        # -- ประวัติ --
        fig_fc.add_trace(go.Scatter(
            x=hist_tail.index, y=hist_tail.values, mode="lines", name="ราคาในอดีต",
            line=dict(color="#5b8def", width=2)
        ))

        # -- แถบ 5–95% (กว้างสุด) --
        fig_fc.add_trace(go.Scatter(
            x=list(future_dates), y=fc["p95"], mode="lines", name="95th",
            line=dict(width=0), showlegend=False, hoverinfo="skip"
        ))
        fig_fc.add_trace(go.Scatter(
            x=list(future_dates), y=fc["p5"], mode="lines", name="ช่วง 5–95%",
            line=dict(width=0), fill="tonexty", fillcolor="rgba(230,195,92,0.10)"
        ))
        # -- แถบ 25–75% (แคบ) --
        fig_fc.add_trace(go.Scatter(
            x=list(future_dates), y=fc["p75"], mode="lines", name="75th",
            line=dict(width=0), showlegend=False, hoverinfo="skip"
        ))
        fig_fc.add_trace(go.Scatter(
            x=list(future_dates), y=fc["p25"], mode="lines", name="ช่วง 25–75%",
            line=dict(width=0), fill="tonexty", fillcolor="rgba(46,230,160,0.14)"
        ))

        # -- เส้นทางตัวอย่าง --
        if show_paths:
            for i, path in enumerate(fc["samples"][:25]):
                fig_fc.add_trace(go.Scatter(
                    x=list(future_dates), y=path[1:], mode="lines",
                    line=dict(color="rgba(120,140,170,0.18)", width=0.7),
                    showlegend=(i == 0), name="เส้นทางจำลอง" if i == 0 else None,
                    hoverinfo="skip"
                ))

        # -- median (เส้นกลาง) --
        fig_fc.add_trace(go.Scatter(
            x=list(future_dates), y=fc["p50"], mode="lines", name="ค่ากลาง (Median)",
            line=dict(color="#2ee6a0", width=2.5, shape="spline")
        ))
        # -- เส้นแนวโน้ม linear --
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
        st.plotly_chart(fig_fc, use_container_width=True, config={"displayModeBar": False, "responsive": True})

        # -- สรุปผลพยากรณ์ (การ์ด) --
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

# ==============================================================
#  PAGE — NEWS
# ==============================================================
elif page == "news":
    st.markdown('<div class="section-title">📰 ข่าว & แนวโน้มอนาคต</div>', unsafe_allow_html=True)
    st.caption("ข่าวจริงจาก Finnhub — ข่าวบริษัท + ข่าวตลาด/เศรษฐกิจ/ภูมิรัฐศาสตร์ (สงคราม นโยบาย ฯลฯ) "
               "พร้อมให้ AI ประเมินผลกระทบต่ออนาคตของสินทรัพย์")

    with st.spinner("กำลังดึงข่าวล่าสุด..."):
        comp_news = fetch_company_news(symbol, days=21)
        gen_news  = fetch_general_news("general")

    # -- Sentiment heuristic จากพาดหัวข่าว --
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

    # -- ปุ่มให้ AI วิเคราะห์ข่าว → อนาคต --
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

    # -- รายการข่าว --
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

# ==============================================================
#  PAGE — RANK (อันดับสินทรัพย์)
# ==============================================================
elif page == "rank":
    st.markdown('<div class="section-title">🏆 อันดับสินทรัพย์ (Composite Ranking)</div>',
                unsafe_allow_html=True)
    st.markdown("""
    <div class="fc-banner">
      จัดอันดับสินทรัพย์ในกลุ่มด้วย <b>คะแนนรวม (0–100)</b> ที่สังเคราะห์จากหลายตัวชี้วัด —
      Sharpe, Max Drawdown, CAGR, โมเมนตัม, การเรียงตัวของเส้นค่าเฉลี่ย ฯลฯ — แล้วเรียงจากแข็งแรงสุดไปอ่อนสุด
      <br><span style="color:var(--muted);font-size:12px">เลือกเปิด "ปรับด้วยข่าว" เพื่อบวก/ลบคะแนนตาม sentiment ข่าวล่าสุด · ข้อมูลย้อนหลังไม่รับประกันอนาคต</span>
    </div>
    """, unsafe_allow_html=True)

    rc1, rc2 = st.columns([2, 1])
    with rc1:
        grp_name = st.selectbox("เลือกกลุ่มสินทรัพย์", list(ASSET_GROUPS.keys()), key="rank_group")
    with rc2:
        use_news = st.checkbox("ปรับคะแนนด้วยข่าว", value=False, key="rank_use_news",
                               help="บวก/ลบคะแนนตาม sentiment ข่าวล่าสุด (เฉพาะหุ้น/ETF ที่มีข่าว)")

    syms = list(ASSET_GROUPS[grp_name].keys())
    with st.spinner(f"กำลังวิเคราะห์และจัดอันดับ {len(syms)} สินทรัพย์ในกลุ่ม {grp_name}..."):
        scores = fetch_watchlist_scores(syms)

    if not scores:
        st.warning("ดึงข้อมูลไม่สำเร็จสำหรับกลุ่มนี้ (อาจติด rate limit ของ Yahoo Finance) — ลองรีเฟรชอีกครั้ง")
    else:
        # ปรับคะแนนด้วย sentiment ข่าว (ถ้าเลือก)
        for s in scores:
            s["adj"] = s["score"]
            if use_news and s.get("news_count", 0) > 0:
                s["adj"] = int(max(0, min(100, round(s["score"] + s["news_sent"] * 0.15))))
        ranked = sorted(scores, key=lambda x: (x["adj"] if use_news else x["score"]), reverse=True)

        news_col_head = "<th>ข่าว</th>" if use_news else ""
        rows_html = ""
        for i, s in enumerate(ranked, 1):
            shown_score = s["adj"] if use_news else s["score"]
            sc_col = score_color(shown_score)
            cagr_c = "#2ee6a0" if s["cagr"] >= 0 else "#ff5d6c"
            mom_c  = "#2ee6a0" if s["momentum"] >= 0 else "#ff5d6c"
            medal  = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, f"{i}")
            news_cell = ""
            if use_news:
                if s.get("news_count", 0) > 0:
                    ncol = "#2ee6a0" if s["news_sent"] > 15 else "#ff5d6c" if s["news_sent"] < -15 else "#e6c35c"
                    news_cell = (f'<td style="font-family:JetBrains Mono,monospace;color:{ncol}">'
                                 f'{s["news_sent"]:+d}</td>')
                else:
                    news_cell = '<td style="color:var(--muted)">—</td>'
            rows_html += f"""
            <tr>
              <td><span class="rank-num">{medal}</span></td>
              <td><span class="rank-ticker">{s['sym']}</span>
                  <div style="font-size:11px;color:var(--muted)">{s['name']}</div></td>
              <td><span style="font-weight:700;color:{sc_col};font-size:16px">{shown_score}</span>
                  <span style="color:var(--muted);font-size:11px">/100</span></td>
              <td style="font-weight:600;color:{sc_col}">{s['verdict']}</td>
              <td style="font-family:JetBrains Mono,monospace;color:{cagr_c}">{s['cagr']:+.1f}%</td>
              <td style="font-family:JetBrains Mono,monospace">{s['sharpe']:.2f}</td>
              <td style="font-family:JetBrains Mono,monospace;color:#ff5d6c">{s['mdd']:.0f}%</td>
              <td style="font-family:JetBrains Mono,monospace">{s['winrate']:.0f}%</td>
              <td style="font-family:JetBrains Mono,monospace;color:{mom_c}">{s['momentum']:+.0f}%</td>
              {news_cell}
            </tr>"""
        st.markdown(f"""
        <table class="rank-table">
          <thead><tr>
            <th>อันดับ</th><th>สินทรัพย์</th><th>คะแนน</th><th>คำตัดสิน</th>
            <th>CAGR</th><th>SHARPE</th><th>MAX DD</th><th>WIN RATE</th><th>MOMENTUM</th>{news_col_head}
          </tr></thead>
          <tbody>{rows_html}</tbody>
        </table>""", unsafe_allow_html=True)

        best = ranked[0]
        st.markdown("<br>", unsafe_allow_html=True)
        st.info(f"📌 ในกลุ่ม **{grp_name}** สินทรัพย์ที่คะแนนสูงสุดคือ **{best['sym']}** "
                f"({best['name']}) ที่ {best['adj'] if use_news else best['score']}/100 → {best['verdict']} · "
                "คะแนนสะท้อนความแข็งแรงเชิงสถิติในอดีต ไม่ใช่คำแนะนำให้ซื้อ — "
                "พิมพ์สัญลักษณ์ในช่องค้นหาด้านซ้ายเพื่อเจาะลึกรายตัว")

# ==============================================================
#  PAGE — PORTFOLIO (จัดพอร์ต · Markowitz)
# ==============================================================
elif page == "portfolio":
    st.markdown('<div class="section-title">🧺 จัดพอร์ตที่เหมาะสม (Efficient Frontier)</div>',
                unsafe_allow_html=True)
    st.markdown("""
    <div class="fc-banner">
      ทฤษฎีพอร์ตของ <b>Markowitz</b> — สุ่มสัดส่วนการลงทุนหลายพันแบบ คำนวณผลตอบแทน/ความเสี่ยงของแต่ละพอร์ต
      แล้วหา <b>เส้นขอบประสิทธิภาพ (Efficient Frontier)</b> · ชี้จุด <b>Max-Sharpe</b> (คุ้มความเสี่ยงสุด)
      และ <b>Min-Volatility</b> (เสี่ยงต่ำสุด)
      <br><span style="color:var(--muted);font-size:12px">เลือกสินทรัพย์ 2–8 ตัวเพื่อกระจายความเสี่ยง · Correlation ต่ำ = กระจายความเสี่ยงได้ดี</span>
    </div>
    """, unsafe_allow_html=True)

    all_syms = list(WATCHLIST.keys())
    default_pick = [s for s in ["AAPL", "MSFT", "GLD", "QQQ", "BTC-USD"] if s in all_syms][:5]
    picks = st.multiselect(
        "เลือกสินทรัพย์เข้าพอร์ต (2–8 ตัว)",
        options=all_syms,
        default=default_pick,
        format_func=lambda s: f"{s} · {WATCHLIST.get(s, s)}",
        key="pf_picks")

    if len(picks) < 2:
        st.warning("เลือกอย่างน้อย 2 สินทรัพย์เพื่อสร้างพอร์ต")
    elif len(picks) > 8:
        st.warning("เลือกไม่เกิน 8 สินทรัพย์ (เพื่อความเร็วและอ่านง่าย)")
    else:
        with st.spinner("กำลังคำนวณเส้นขอบประสิทธิภาพ (สุ่ม 4,000 พอร์ต)..."):
            ef = efficient_frontier(picks)

        if ef is None:
            st.warning("ข้อมูลไม่พอ (บางสินทรัพย์มีประวัติสั้นเกินไป หรือติด rate limit) — ลองเปลี่ยนสินทรัพย์/รีเฟรช")
        else:
            cols = ef["cols"]
            pcol1, pcol2 = st.columns([3, 2])

            with pcol1:
                # -- Efficient Frontier scatter --
                fig_ef = go.Figure()
                fig_ef.add_trace(go.Scatter(
                    x=ef["vols"], y=ef["rets"], mode="markers",
                    marker=dict(size=4, color=ef["sharpes"], colorscale="Viridis",
                                showscale=True, colorbar=dict(title="Sharpe", thickness=12),
                                opacity=0.55),
                    name="พอร์ตสุ่ม", hovertemplate="ความเสี่ยง %{x:.1f}%<br>ผลตอบแทน %{y:.1f}%<extra></extra>"))
                ms, mv = ef["max_sharpe"], ef["min_vol"]
                fig_ef.add_trace(go.Scatter(
                    x=[ms["vol"]], y=[ms["ret"]], mode="markers",
                    marker=dict(size=18, color="#e6c35c", symbol="star",
                                line=dict(color="#fff", width=1.5)),
                    name=f"Max-Sharpe ({ms['sharpe']:.2f})"))
                fig_ef.add_trace(go.Scatter(
                    x=[mv["vol"]], y=[mv["ret"]], mode="markers",
                    marker=dict(size=15, color="#2ee6a0", symbol="diamond",
                                line=dict(color="#fff", width=1.5)),
                    name=f"Min-Vol ({mv['vol']:.1f}%)"))
                dark_layout(fig_ef, height=440, title="Efficient Frontier — ความเสี่ยง (x) vs ผลตอบแทนคาดหวัง (y)")
                fig_ef.update_xaxes(title="ความผันผวน/ปี (%)")
                fig_ef.update_yaxes(title="ผลตอบแทนคาดหวัง/ปี (%)")
                st.plotly_chart(fig_ef, use_container_width=True, config={"displayModeBar": False, "responsive": True})

            with pcol2:
                # -- Correlation heatmap --
                fig_cor = go.Figure(go.Heatmap(
                    z=ef["corr"], x=cols, y=cols,
                    colorscale="RdBu_r", zmid=0, zmin=-1, zmax=1,
                    text=[[f"{v:.2f}" for v in row] for row in ef["corr"]],
                    texttemplate="%{text}", textfont=dict(size=10),
                    colorbar=dict(title="Corr", thickness=12)))
                fig_cor.update_layout(
                    height=440, margin=dict(l=10, r=10, t=46, b=10),
                    title=dict(text="Correlation Matrix", font=dict(size=15, color="#e9eef7")),
                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="JetBrains Mono", color="#c3cbd9", size=10))
                st.plotly_chart(fig_cor, use_container_width=True, config={"displayModeBar": False, "responsive": True})

            # -- ตารางน้ำหนักพอร์ต --
            st.markdown('<div class="section-title" style="font-size:17px;margin-top:8px">⚖️ สัดส่วนพอร์ตที่แนะนำ</div>',
                        unsafe_allow_html=True)
            wc1, wc2 = st.columns(2)

            def weight_table(title, pack, accent):
                rows = "".join(
                    f"""<tr><td><span class="rank-ticker">{c}</span>
                        <span style="color:var(--muted);font-size:11px"> {WATCHLIST.get(c,'')}</span></td>
                        <td style="font-family:JetBrains Mono,monospace;color:{accent};font-weight:600">{w:.1f}%</td></tr>"""
                    for c, w in sorted(pack["weights"].items(), key=lambda x: -x[1]))
                return f"""
                <div style="font-weight:600;color:{accent};margin-bottom:8px">{title}</div>
                <table class="rank-table">
                  <thead><tr><th>สินทรัพย์</th><th>น้ำหนัก</th></tr></thead>
                  <tbody>{rows}</tbody>
                </table>
                <div style="margin-top:8px;font-size:12px;color:var(--muted)">
                  ผลตอบแทนคาดหวัง <b style="color:{accent}">{pack['ret']:+.1f}%</b>/ปี ·
                  ความเสี่ยง <b>{pack['vol']:.1f}%</b> · Sharpe <b>{pack['sharpe']:.2f}</b></div>
                """

            with wc1:
                st.markdown(weight_table("🌟 Max-Sharpe (คุ้มความเสี่ยงสุด)", ef["max_sharpe"], "#e6c35c"),
                            unsafe_allow_html=True)
            with wc2:
                st.markdown(weight_table("🛡️ Min-Volatility (เสี่ยงต่ำสุด)", ef["min_vol"], "#2ee6a0"),
                            unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.info(f"📌 คำนวณจากข้อมูลย้อนหลัง {ef['n_days']:,} วันที่ทุกสินทรัพย์มีตรงกัน · "
                    "พอร์ต Max-Sharpe ให้ผลตอบแทนต่อหน่วยความเสี่ยงสูงสุด ส่วน Min-Vol เน้นเสถียร — "
                    "เลือกตามระดับความเสี่ยงที่รับได้ · นี่คือการ optimize บนอดีต ไม่รับประกันอนาคต")

# ==============================================================
#  PAGE — MY PORTFOLIO (พอร์ตของฉัน)
# ==============================================================
elif page == "myport":
    st.markdown('<div class="section-title">💼 พอร์ตของฉัน (วิเคราะห์พอร์ตจริง)</div>',
                unsafe_allow_html=True)
    st.markdown("""
    <div class="fc-banner">
      กรอกหุ้น/ETF/คริปโตที่ถืออยู่จริง (สัญลักษณ์ · จำนวน · ราคาทุนเฉลี่ย) แล้วระบบจะดึงราคาล่าสุด
      คำนวณ <b>กำไร/ขาดทุน</b> รายตัวและทั้งพอร์ต พร้อมเมตริกความเสี่ยงระดับพอร์ต (Sharpe, ความผันผวน, Beta, การกระจายความเสี่ยง)
      <br><span style="color:var(--muted);font-size:12px">แก้ไขในตารางได้เลย · เพิ่ม/ลบแถวด้วยปุ่ม + / ไอคอนถังขยะ · ข้อมูลไม่ถูกบันทึก (อยู่แค่ในเซสชันนี้)</span>
    </div>
    """, unsafe_allow_html=True)

    default_holdings = pd.DataFrame({
        "สัญลักษณ์":      ["AAPL", "NVDA", "MSFT"],
        "จำนวนหน่วย":     [10.0, 5.0, 8.0],
        "ราคาทุนเฉลี่ย":  [180.0, 450.0, 350.0],
    })
    edited = st.data_editor(
        default_holdings, num_rows="dynamic", use_container_width=True, key="holdings_editor",
        column_config={
            "สัญลักษณ์":     st.column_config.TextColumn("สัญลักษณ์", help="เช่น AAPL, BTC-USD, GLD"),
            "จำนวนหน่วย":    st.column_config.NumberColumn("จำนวนหน่วย", min_value=0.0, format="%.4f"),
            "ราคาทุนเฉลี่ย": st.column_config.NumberColumn("ราคาทุนเฉลี่ย ($)", min_value=0.0, format="%.2f"),
        })

    holdings = tuple(
        (str(r["สัญลักษณ์"]).upper().strip(), float(r["จำนวนหน่วย"] or 0), float(r["ราคาทุนเฉลี่ย"] or 0))
        for _, r in edited.iterrows()
        if str(r["สัญลักษณ์"]).strip()
    )

    if not holdings:
        st.info("กรอกอย่างน้อย 1 รายการในตารางด้านบนเพื่อเริ่มวิเคราะห์")
    else:
        with st.spinner("กำลังดึงราคาล่าสุดและวิเคราะห์พอร์ต..."):
            pf = analyze_holdings(holdings)

        rows = pf["rows"]
        # -- การ์ดสรุประดับพอร์ต --
        pnl_cls = "pos" if pf["total_pnl"] >= 0 else "neg"
        mc1, mc2, mc3, mc4 = st.columns(4)
        with mc1:
            st.markdown(f"""<div class="mcard">
              <div class="mcard-label">มูลค่าพอร์ตปัจจุบัน</div>
              <div class="mcard-value">${pf['total_val']:,.2f}</div>
              <div class="mcard-sub">{len([r for r in rows if r['ok']])} สินทรัพย์</div></div>""",
              unsafe_allow_html=True)
        with mc2:
            st.markdown(f"""<div class="mcard">
              <div class="mcard-label">ต้นทุนรวม</div>
              <div class="mcard-value">${pf['total_cost']:,.2f}</div></div>""", unsafe_allow_html=True)
        with mc3:
            st.markdown(f"""<div class="mcard {pnl_cls}">
              <div class="mcard-label">กำไร/ขาดทุนรวม</div>
              <div class="mcard-value">{'+' if pf['total_pnl']>=0 else ''}${pf['total_pnl']:,.2f}</div>
              <div class="mcard-sub">{pf['total_pnl_pct']:+.2f}%</div></div>""", unsafe_allow_html=True)
        with mc4:
            mt = pf["metrics"]
            if mt:
                shc = "pos" if mt["sharpe"] >= 1 else "neg" if mt["sharpe"] < 0 else ""
                st.markdown(f"""<div class="mcard {shc}">
                  <div class="mcard-label">Sharpe พอร์ต</div>
                  <div class="mcard-value">{mt['sharpe']:.2f}</div>
                  <div class="mcard-sub">CAGR {mt['cagr']:+.1f}% · Vol {mt['vol']:.1f}%</div></div>""",
                  unsafe_allow_html=True)
            else:
                st.markdown("""<div class="mcard">
                  <div class="mcard-label">Sharpe พอร์ต</div>
                  <div class="mcard-value">—</div>
                  <div class="mcard-sub">ข้อมูลไม่พอ</div></div>""", unsafe_allow_html=True)

        pcol1, pcol2 = st.columns([3, 2])
        with pcol1:
            # -- ตารางรายตัว --
            rows_html = ""
            for r in rows:
                if not r["ok"]:
                    rows_html += f"""<tr><td><span class="rank-ticker">{r['ticker']}</span></td>
                      <td colspan="5" style="color:var(--muted)">ดึงราคาไม่สำเร็จ</td></tr>"""
                    continue
                pcl = "#2ee6a0" if r["pnl"] >= 0 else "#ff5d6c"
                rows_html += f"""
                <tr>
                  <td><span class="rank-ticker">{r['ticker']}</span></td>
                  <td style="font-family:JetBrains Mono,monospace">{r['shares']:g}</td>
                  <td style="font-family:JetBrains Mono,monospace">${r['avg_cost']:,.2f}</td>
                  <td style="font-family:JetBrains Mono,monospace">${r['price']:,.2f}</td>
                  <td style="font-family:JetBrains Mono,monospace">${r['value']:,.2f}</td>
                  <td style="font-family:JetBrains Mono,monospace;color:{pcl}">
                    {r['pnl']:+,.0f} ({r['pnl_pct']:+.1f}%)</td>
                </tr>"""
            st.markdown(f"""
            <table class="rank-table">
              <thead><tr><th>สินทรัพย์</th><th>จำนวน</th><th>ทุนเฉลี่ย</th>
                <th>ราคาล่าสุด</th><th>มูลค่า</th><th>กำไร/ขาดทุน</th></tr></thead>
              <tbody>{rows_html}</tbody>
            </table>""", unsafe_allow_html=True)

            # -- ดาวน์โหลด CSV --
            csv = edited.to_csv(index=False).encode("utf-8-sig")
            st.download_button("⬇️ ดาวน์โหลดพอร์ต (CSV)", csv,
                               file_name="my_portfolio.csv", mime="text/csv")

        with pcol2:
            # -- Pie สัดส่วน --
            ok_rows = [r for r in rows if r["ok"] and r["value"] > 0]
            if ok_rows:
                fig_pie = go.Figure(go.Pie(
                    labels=[r["ticker"] for r in ok_rows],
                    values=[r["value"] for r in ok_rows],
                    hole=0.55, textinfo="label+percent",
                    marker=dict(line=dict(color="#0b0f1a", width=2)),
                    textfont=dict(family="JetBrains Mono", size=11, color="#e9eef7")))
                fig_pie.update_layout(
                    height=300, margin=dict(l=10, r=10, t=30, b=10), showlegend=False,
                    title=dict(text="สัดส่วนพอร์ต", font=dict(size=14, color="#e9eef7")),
                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                    colorway=["#e6c35c", "#2ee6a0", "#5b8def", "#a877e6", "#34e3c4",
                              "#ff5d6c", "#ff9f43", "#f3b34c"])
                st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False, "responsive": True})

        # -- เมตริกความเสี่ยงระดับพอร์ต --
        mt = pf["metrics"]
        if mt:
            st.markdown('<div class="section-title" style="font-size:17px;margin-top:8px">📐 ความเสี่ยงระดับพอร์ต</div>',
                        unsafe_allow_html=True)
            rk1, rk2, rk3, rk4 = st.columns(4)
            with rk1:
                st.markdown(f"""<div class="mcard"><div class="mcard-label">ความผันผวน/ปี</div>
                  <div class="mcard-value">{mt['vol']:.1f}%</div></div>""", unsafe_allow_html=True)
            with rk2:
                st.markdown(f"""<div class="mcard neg"><div class="mcard-label">Max Drawdown</div>
                  <div class="mcard-value">{mt['mdd']:.1f}%</div></div>""", unsafe_allow_html=True)
            with rk3:
                beta_txt = f"{mt['beta']:.2f}" if mt['beta'] is not None else "—"
                st.markdown(f"""<div class="mcard"><div class="mcard-label">Beta (เทียบ S&P 500)</div>
                  <div class="mcard-value">{beta_txt}</div>
                  <div class="mcard-sub">>1 เหวี่ยงกว่าตลาด</div></div>""", unsafe_allow_html=True)
            with rk4:
                if mt['avg_corr'] is not None:
                    div_txt = ("กระจายดี" if mt['avg_corr'] < 0.4 else
                               "ปานกลาง" if mt['avg_corr'] < 0.7 else "กระจุกตัว")
                    dcl = "pos" if mt['avg_corr'] < 0.4 else "neg" if mt['avg_corr'] >= 0.7 else ""
                    st.markdown(f"""<div class="mcard {dcl}"><div class="mcard-label">Correlation เฉลี่ย</div>
                      <div class="mcard-value">{mt['avg_corr']:.2f}</div>
                      <div class="mcard-sub">{div_txt}</div></div>""", unsafe_allow_html=True)
                else:
                    st.markdown("""<div class="mcard"><div class="mcard-label">Correlation เฉลี่ย</div>
                      <div class="mcard-value">—</div>
                      <div class="mcard-sub">ต้องมี ≥2 สินทรัพย์</div></div>""", unsafe_allow_html=True)
            st.info("📌 Beta บอกว่าพอร์ตเคลื่อนไหวแรงกว่า/น้อยกว่าตลาดแค่ไหน · "
                    "Correlation เฉลี่ยต่ำ = สินทรัพย์ไม่ขึ้นลงพร้อมกัน = กระจายความเสี่ยงได้ดี (ลดความเสี่ยงรวม)")

# ==============================================================
#  PAGE — INCOME (วางแผนเงิน · เครื่องคิดเลขการลงทุน)
# ==============================================================
elif page == "income":
    st.markdown('<div class="section-title">💰 วางแผนเงิน (Investment Planner)</div>',
                unsafe_allow_html=True)
    st.markdown(f"""
    <div class="fc-banner">
      จำลองการเติบโตของเงินลงทุนแบบ <b>ทบต้นรายเดือน</b> พร้อมเงินลงทุนเพิ่มทุกเดือน (DCA) —
      คำนวณ 3 สถานการณ์ (แย่ · ปกติ · ดี) จากผลตอบแทนและความผันผวนจริงของ <b>{symbol}</b>
      <br><span style="color:var(--muted);font-size:12px">ปรับสมมติฐานได้เอง · รวมผลของปันผล ภาษีหัก ณ ที่จ่าย และค่าธรรมเนียม · แปลงเป็นเงินบาทให้ด้วย</span>
    </div>
    """, unsafe_allow_html=True)

    ic1, ic2, ic3, ic4 = st.columns(4)
    with ic1:
        capital = st.number_input("เงินลงทุนเริ่มต้น ($)", min_value=0.0, value=10000.0, step=1000.0)
    with ic2:
        monthly = st.number_input("ลงทุนเพิ่ม/เดือน ($)", min_value=0.0, value=500.0, step=100.0)
    with ic3:
        years = st.number_input("ระยะเวลา (ปี)", min_value=1, max_value=50, value=10, step=1)
    with ic4:
        _default_ret = float(max(-15.0, min(35.0, round(m["cagr"], 1))))
        annual_return = st.number_input("ผลตอบแทนคาดหวัง/ปี (%)", value=_default_ret, step=0.5,
                                        help=f"ค่าเริ่มต้น = CAGR ย้อนหลังของ {symbol} ({m['cagr']:+.1f}%) ปรับได้ตามที่คุณคาด")

    with st.expander("⚙️ ปันผล · ภาษี · ค่าธรรมเนียม (สำหรับนักลงทุนไทย)", expanded=False):
        ec1, ec2, ec3 = st.columns(3)
        with ec1:
            div_yield = st.number_input("ปันผล/ปี (%)", min_value=0.0, value=0.0, step=0.5,
                                        help="เงินปันผลที่ได้รับต่อปี (นำกลับไปลงทุนต่อ)")
        with ec2:
            wht = st.number_input("ภาษีหัก ณ ที่จ่าย (%)", min_value=0.0, max_value=50.0, value=15.0, step=1.0,
                                  help="หุ้นสหรัฐหักภาษีปันผล 15% สำหรับนักลงทุนไทย (ตามสนธิสัญญาภาษีซ้อน)")
        with ec3:
            fee = st.number_input("ค่าธรรมเนียม/ปี (%)", min_value=0.0, value=0.0, step=0.1,
                                  help="ค่าธรรมเนียมการจัดการกองทุน/โบรกเกอร์ต่อปี (ถ้ามี)")

    # -- โมเดลการเติบโต (ทบต้นรายเดือน) --
    months = int(years * 12)
    div_m = div_yield / 100 * (1 - wht / 100) / 12   # ปันผลสุทธิหลังภาษี ต่อเดือน
    fee_m = fee / 100 / 12

    def project(ann_ret_pct):
        eff = ann_ret_pct / 100 / 12 + div_m - fee_m
        bal = capital
        out = [capital]
        for _ in range(months):
            bal = bal * (1 + eff) + monthly
            out.append(bal)
        return out

    vol_band = m["vol_l"]   # ±1σ ความผันผวนต่อปี (%)
    base_path = project(annual_return)
    bull_path = project(annual_return + vol_band)
    bear_path = project(max(-90.0, annual_return - vol_band))

    total_contrib = capital + monthly * months
    final_base = base_path[-1]
    total_gain = final_base - total_contrib
    gain_pct = (total_gain / total_contrib * 100) if total_contrib > 0 else 0.0

    # -- การ์ดสรุป --
    oc1, oc2, oc3, oc4 = st.columns(4)
    gcl = "pos" if total_gain >= 0 else "neg"
    with oc1:
        st.markdown(f"""<div class="mcard gold"><div class="mcard-label">มูลค่าปลายทาง (ปกติ)</div>
          <div class="mcard-value">${final_base:,.0f}</div>
          <div class="mcard-sub">ใน {years} ปี</div></div>""", unsafe_allow_html=True)
    with oc2:
        st.markdown(f"""<div class="mcard"><div class="mcard-label">เงินที่ลงไปทั้งหมด</div>
          <div class="mcard-value">${total_contrib:,.0f}</div>
          <div class="mcard-sub">ต้น ${capital:,.0f} + เพิ่ม ${monthly:,.0f}/ด.</div></div>""",
          unsafe_allow_html=True)
    with oc3:
        st.markdown(f"""<div class="mcard {gcl}"><div class="mcard-label">กำไรจากการลงทุน</div>
          <div class="mcard-value">{'+' if total_gain>=0 else ''}${total_gain:,.0f}</div>
          <div class="mcard-sub">{gain_pct:+.0f}% จากเงินต้น</div></div>""", unsafe_allow_html=True)
    with oc4:
        usdthb = fetch_usdthb()
        st.markdown(f"""<div class="mcard"><div class="mcard-label">≈ เงินบาท (ปลายทาง)</div>
          <div class="mcard-value" style="font-size:18px">฿{final_base*usdthb:,.0f}</div>
          <div class="mcard-sub">ที่ ฿{usdthb:.2f}/$</div></div>""", unsafe_allow_html=True)

    # -- กราฟการเติบโต 3 สถานการณ์ --
    xs = list(range(months + 1))
    xs_years = [x / 12 for x in xs]
    contrib_line = [capital + monthly * i for i in xs]
    fig_g = go.Figure()
    fig_g.add_trace(go.Scatter(x=xs_years, y=bull_path, mode="lines", name=f"ดี (+{vol_band:.0f}% vol)",
                               line=dict(color="#2ee6a0", width=2, dash="dot")))
    fig_g.add_trace(go.Scatter(x=xs_years, y=base_path, mode="lines", name="ปกติ (ตามคาด)",
                               line=dict(color="#e6c35c", width=2.5),
                               fill="tonexty", fillcolor="rgba(46,230,160,0.05)"))
    fig_g.add_trace(go.Scatter(x=xs_years, y=bear_path, mode="lines", name=f"แย่ (−{vol_band:.0f}% vol)",
                               line=dict(color="#ff5d6c", width=2, dash="dot"),
                               fill="tonexty", fillcolor="rgba(255,93,108,0.05)"))
    fig_g.add_trace(go.Scatter(x=xs_years, y=contrib_line, mode="lines", name="เงินต้นสะสม",
                               line=dict(color="#7d8799", width=1.5, dash="dash")))
    dark_layout(fig_g, height=420, title="การเติบโตของพอร์ต — 3 สถานการณ์")
    fig_g.update_xaxes(title="ปี")
    fig_g.update_yaxes(title="มูลค่าพอร์ต ($)")
    st.plotly_chart(fig_g, use_container_width=True, config={"displayModeBar": False, "responsive": True})

    sc_c1, sc_c2, sc_c3 = st.columns(3)
    for col, (label, path, c) in zip(
        [sc_c1, sc_c2, sc_c3],
        [("🔴 แย่", bear_path, "#ff5d6c"), ("🟡 ปกติ", base_path, "#e6c35c"), ("🟢 ดี", bull_path, "#2ee6a0")]):
        g = path[-1] - total_contrib
        with col:
            st.markdown(f"""<div class="mcard" style="--accent:{c}">
              <div class="mcard-label">{label}</div>
              <div class="mcard-value" style="color:{c}">${path[-1]:,.0f}</div>
              <div class="mcard-sub">กำไร {'+' if g>=0 else ''}${g:,.0f} · ≈ ฿{path[-1]*usdthb:,.0f}</div></div>""",
              unsafe_allow_html=True)

    # -- เมตริกความเสี่ยง (VaR / ES / Kelly) --
    st.markdown('<div class="section-title" style="font-size:17px;margin-top:10px">⚠️ มุมความเสี่ยง</div>',
                unsafe_allow_html=True)
    rets_i = data["Close"].pct_change().dropna()
    kelly_raw = float(rets_i.mean() / (rets_i.var() + 1e-12))
    kelly = max(0.0, min(kelly_raw, 1.0))
    kc1, kc2, kc3 = st.columns(3)
    with kc1:
        st.markdown(f"""<div class="mcard neg"><div class="mcard-label">VALUE AT RISK (95%)</div>
          <div class="mcard-value">{m['var95']:.2f}%</div>
          <div class="mcard-sub">วันแย่ ๆ มีโอกาส 5% ที่จะขาดทุนเกินนี้/วัน</div></div>""", unsafe_allow_html=True)
    with kc2:
        st.markdown(f"""<div class="mcard neg"><div class="mcard-label">EXPECTED SHORTFALL</div>
          <div class="mcard-value">{m['es95']:.2f}%</div>
          <div class="mcard-sub">ค่าเฉลี่ยขาดทุนในวันที่แย่กว่า VaR</div></div>""", unsafe_allow_html=True)
    with kc3:
        kcl = "pos" if kelly > 0 else "neg"
        st.markdown(f"""<div class="mcard {kcl}"><div class="mcard-label">KELLY CRITERION</div>
          <div class="mcard-value">{kelly*100:.0f}%</div>
          <div class="mcard-sub">สัดส่วนเงินที่เหมาะ (ทางทฤษฎี) · นิยมใช้ครึ่งหนึ่ง (½ Kelly)</div></div>""",
          unsafe_allow_html=True)

    st.info("📌 ตัวเลขสมมติจากผลตอบแทน/ความผันผวนในอดีต — ผลจริงอาจต่างมาก · "
            "Kelly Criterion บอกสัดส่วนเงินลงทุนที่ทำให้พอร์ตโตเร็วสุดทางทฤษฎี แต่เสี่ยงสูง "
            "นักลงทุนส่วนใหญ่ใช้แค่ครึ่งเดียว (½ Kelly) · นี่ไม่ใช่คำแนะนำการลงทุน ควรปรึกษาผู้เชี่ยวชาญ")

# ==============================================================
#  PAGE — CHAT (ที่ปรึกษา AI · Claude)
# ==============================================================
elif page == "chat":
    st.markdown('<div class="section-title">🤖 ถาม AI ที่ปรึกษาการลงทุน</div>', unsafe_allow_html=True)
    st.caption("ผู้ช่วยเชิงปริมาณที่อิงตัวเลขและสถิติย้อนหลัง — Claude (Anthropic) "
               "วิเคราะห์จากข้อมูลของสินทรัพย์ที่คุณกำลังดูอยู่")

    # -- สร้างบริบท (context) จากหน้าต่าง ๆ ที่เปิดไว้ — degrade ได้ถ้าหน้าไหนยังไม่ถูกเปิด --
    ctx = [
        "คุณคือ DGV — ผู้ช่วย AI ที่คุยได้เป็นธรรมชาติเหมือนเพื่อนที่รู้เรื่องการเงิน "
        "ไม่ใช่หุ่นยนต์ที่อ่านรายงาน\n"
        "\n"
        "วิธีคุย:\n"
        "- พูดคุยให้เป็นกันเองและลื่นไหลเป็นภาษาไทยที่เป็นธรรมชาติ เหมือนคนจริงที่เก่งเรื่องลงทุนนั่งคุยด้วย\n"
        "- อย่าใส่หัวข้อ บูลเล็ต หรือโครงสร้างทุกครั้ง — ดูจากคำถาม ถ้าเขาถามสั้นก็ตอบสั้น ๆ เป็นย่อหน้า "
        "ถ้าเรื่องซับซ้อนค่อยจัดเป็นข้อ ๆ ให้อ่านง่าย\n"
        "- ปรับโทนตามผู้ถาม ถามเล่น ๆ ก็ตอบสบาย ๆ ได้ ถามจริงจังก็จริงจัง\n"
        "\n"
        "คุณตอบได้ทุกเรื่องเหมือน ChatGPT/Gemini — ความรู้ทั่วไป อธิบายแนวคิด เขียนข้อความ ช่วยคิด คุยเล่น "
        "แต่สิ่งที่คุณ 'เก่งที่สุด' คือการวิเคราะห์การลงทุนเชิงปริมาณ "
        "เมื่อคำถามเกี่ยวกับหุ้น/การเงิน/สินทรัพย์ ให้ดึงตัวเลขด้านล่างมาวิเคราะห์อย่างลึกซึ้งจากสถิติจริง\n"
        "\n"
        "หลักการสำคัญ:\n"
        "- เรื่องลงทุน: อิงตัวเลข/สถิติย้อนหลังที่ให้มาเท่านั้น ไม่เดาสุ่ม ไม่อิงข่าวลือ "
        "และเตือนตามจังหวะที่เหมาะ (ไม่ต้องท่องซ้ำทุกครั้ง) ว่าผลย้อนหลังไม่การันตีอนาคต และไม่ใช่คำแนะนำการลงทุน\n"
        "- ถ้าไม่รู้หรือไม่มีข้อมูล บอกตรง ๆ ว่าไม่รู้ ดีกว่าแต่งขึ้นมา\n"
        "- เรื่องนอกเหนือการลงทุน ตอบได้ตามปกติแบบผู้ช่วยทั่วไปที่เป็นมิตร",
        f"\nสินทรัพย์ที่ผู้ใช้กำลังดู: {symbol} ({WATCHLIST.get(symbol, symbol)})",
        f"ราคาล่าสุด {fmt_p(cur_price)} ({price_chg_pct:+.2f}% วันนี้)",
        f"คะแนนรวม {m['score']}/100 → {m['verdict']}",
        f"CAGR {m['cagr']:+.1f}%/ปี · Sharpe {m['sharpe']:.2f} · Sortino {m['sortino']:.2f} · "
        f"Max Drawdown {m['mdd']:.1f}% · ความผันผวน {m['vol_l']:.1f}%/ปี · Momentum {m['momentum']:+.1f}% · RSI {m['rsi']:.0f}",
        f"ผลตอบแทนย้อนหลัง: 1เดือน {m['ret_1m']:+.1f}% · 6เดือน {m['ret_6m']:+.1f}% · 1ปี {m['ret_1y']:+.1f}% · 3ปี {m['ret_3y']:+.1f}%",
        f"ความเสี่ยง: VaR95 {m['var95']:.2f}%/วัน · Expected Shortfall {m['es95']:.2f}% · Win Rate (backtest) {bt['winrate']}%",
    ]
    try:
        if rt_quote:
            ctx.append(f"Real-time: {fmt_p(rt_quote['c'])} (High {fmt_p(rt_quote['h'])}, Low {fmt_p(rt_quote['l'])})")
    except NameError:
        pass
    try:
        ctx.append(f"พยากรณ์ Monte Carlo: ผลตอบแทนคาดหวัง {fc['exp_return']:+.1f}% "
                   f"โอกาสขึ้น {fc['prob_up']:.0f}% (ν={fc['nu']})")
    except NameError:
        pass
    try:
        ctx.append(f"พยากรณ์เชิงโมเดล: โมเดลแม่นสุด {adv['best_name']} (MAPE {adv['best_mape']:.1f}%), "
                   f"Consensus {adv['consensus_ret']:+.1f}%")
    except NameError:
        pass
    try:
        if comp_news or gen_news:
            ctx.append(f"Sentiment ข่าวล่าสุด: {sent_score:+d} (จากการนับคำหยาบ ๆ)")
    except NameError:
        pass
    try:
        if pf and pf["rows"]:
            holds = ", ".join(f"{r['ticker']} {r['weight']:.0f}%" for r in pf["rows"] if r["ok"])
            line = f"พอร์ตจริงของผู้ใช้: มูลค่า ${pf['total_val']:,.0f}, กำไร/ขาดทุน {pf['total_pnl_pct']:+.1f}% [{holds}]"
            if pf["metrics"]:
                line += (f" · Sharpe {pf['metrics']['sharpe']:.2f}, Vol {pf['metrics']['vol']:.1f}%, "
                         f"MaxDD {pf['metrics']['mdd']:.1f}%")
            ctx.append(line)
    except NameError:
        pass
    sys_ctx = "\n".join(ctx)

    # -- ปุ่มคำถามด่วน --
    prompt = None
    quick = ["สรุปความเสี่ยงของสินทรัพย์นี้",
             "ผลตอบแทนย้อนหลังเป็นอย่างไร",
             "ควรจัดสรรเงินลงทุนอย่างไร",
             "วิเคราะห์พอร์ตของฉัน"]
    qcols = st.columns(4)
    for col, q in zip(qcols, quick):
        if col.button(q, use_container_width=True, key=f"qp_{q}"):
            prompt = q

    # -- แสดงประวัติแชต --
    msgs_html = ""
    for msg in st.session_state["chat"]:
        is_user = msg["role"] == "user"
        body = msg["content"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
        if is_user:
            msgs_html += f"""<div class="msg-row u">
              <div class="av usr">คุณ</div><div class="bub u-b">{body}</div></div>"""
        else:
            msgs_html += f"""<div class="msg-row">
              <div class="av ai">D</div><div class="bub ai-b">{body}</div></div>"""
    st.markdown(f'<div class="chat-wrap">{msgs_html}</div>', unsafe_allow_html=True)

    # -- ช่องพิมพ์ --
    typed = st.chat_input("พิมพ์คำถามเกี่ยวกับการลงทุน เช่น สินทรัพย์นี้เสี่ยงไหม...")
    if typed:
        prompt = typed

    if prompt:
        st.session_state["chat"].append({"role": "user", "content": prompt})
        try:
            client = get_claude_client()
            # ส่งประวัติย้อนหลังไม่เกิน 10 ข้อความ (ลด token)
            history = [{"role": msg["role"], "content": msg["content"]}
                       for msg in st.session_state["chat"][-10:]]
            with st.spinner("DGV กำลังวิเคราะห์..."):
                resp = client.messages.create(
                    model=CLAUDE_MODEL, max_tokens=1400, temperature=0.7,
                    system=sys_ctx, messages=history)
            answer = "".join(b.text for b in resp.content if b.type == "text")
        except Exception as e:
            answer = (f"ขออภัย เชื่อมต่อ AI ไม่สำเร็จ — ตรวจสอบ ANTHROPIC_API_KEY ใน Streamlit secrets\n\n"
                      f"รายละเอียด: {e}")
        st.session_state["chat"].append({"role": "assistant", "content": answer})
        st.rerun()

    if len(st.session_state["chat"]) > 1:
        if st.button("🗑️ ล้างประวัติการสนทนา"):
            st.session_state["chat"] = st.session_state["chat"][:1]
            st.rerun()

# --------------------------------------------------------------
#  FOOTER (ท้ายหน้า — แสดงทุกหน้า)
# --------------------------------------------------------------
st.markdown("<hr style='border-color:rgba(255,255,255,0.08);margin:28px 0 14px'>",
            unsafe_allow_html=True)
fcol1, fcol2 = st.columns([1, 4])
with fcol1:
    if st.button("🔄 ล้างแคช & รีโหลดข้อมูล"):
        st.cache_data.clear()
        st.rerun()
with fcol2:
    st.caption("DGV Investment Analyzer · ข้อมูลย้อนหลังจาก yfinance/Stooq · Real-time & ข่าวจาก Finnhub · "
               "AI โดย Claude (Anthropic) · วิเคราะห์ด้วยคณิตศาสตร์/สถิติล้วน ๆ — "
               "เพื่อการศึกษาเท่านั้น ไม่ใช่คำแนะนำการลงทุน")
