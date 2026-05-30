import time
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf
from google import genai

st.set_page_config(page_title="AI Live Trading & Chatbot Platform", layout="wide")
st.title("🚀 AI Stock Investment & Chatbot Platform (LIVE)")

if "search_history" not in st.session_state:
    st.session_state.search_history = []
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {
            "role": "assistant",
            "content": "สวัสดีครับ! ผมเป็นผู้ช่วยด้านการลงทุนและการเทรด 📊\n\nถามได้เลยครับ เช่น:\n- หุ้น: AAPL, TSLA, NVDA แนวโน้มเป็นยังไง?\n- Forex: EUR/USD, USD/JPY น่าเทรดไหม?\n- ทองคำ: ราคาตอนนี้เท่าไหร่? แนวโน้มยังไง?\n- คริปโต: BTC, ETH วันนี้ราคาเท่าไหร่?\n- โลหะมีค่า: Silver, Platinum ราคาตอนนี้?",
        }
    ]

col_input, col_refresh_info = st.columns([1, 2])
with col_input:
    symbol = (
        st.text_input("🔍 กรอกชื่อหุ้น คู่เงิน หรือทองคำ (เช่น AAPL, EURUSD=X, GC=F)", "AAPL")
        .upper()
        .replace("/", "")
    )

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
    "gold": "GC=F", "ทอง": "GC=F", "xauusd": "GC=F",
    "silver": "SI=F", "xagusd": "SI=F",
    "platinum": "PL=F", "แพลทินัม": "PL=F",
    "btc": "BTC-USD", "bitcoin": "BTC-USD", "บิทคอยน์": "BTC-USD",
    "eth": "ETH-USD", "ethereum": "ETH-USD", "อีเธอเรียม": "ETH-USD",
    "eurusd": "EURUSD=X", "gbpusd": "GBPUSD=X", "usdjpy": "USDJPY=X",
    "audusd": "AUDUSD=X", "usdthb": "USDTHB=X",
    "oil": "CL=F", "น้ำมัน": "CL=F",
    "sp500": "^GSPC", "nasdaq": "^IXIC", "dow": "^DJI",
    "aapl": "AAPL", "tsla": "TSLA", "nvda": "NVDA", "msft": "MSFT",
    "google": "GOOGL", "meta": "META", "amazon": "AMZN",
}

def detect_symbols_from_query(query):
    q = query.lower()
    found = []
    for keyword, sym in MARKET_SYMBOLS.items():
        if keyword in q and sym not in found:
            found.append(sym)
    return found[:3]

def get_market_prices_for_query(query):
    syms = detect_symbols_from_query(query)
    if not syms:
        return ""
    prices = []
    for sym in syms:
        info = fetch_price(sym)
        if info:
            sign = "+" if info["change"] >= 0 else ""
            prices.append(f"{sym}: {info['price']:,} ({sign}{info['change_pct']}%)")
    if prices:
        return "\n\n[ราคาตลาดปัจจุบัน]\n" + "\n".join(prices)
    return ""

try:
    ticker = yf.Ticker(symbol)
    data = ticker.history(period="1y")
    if not data.empty:
        current_price = data["Close"].iloc[-1]
        previous_close = data["Close"].iloc[-2] if len(data) > 1 else current_price
        price_change = current_price - previous_close
        price_change_pct = (price_change / previous_close) * 100
    else:
        current_price = 0
except Exception as e:
    st.error(f"เกิดข้อผิดพลาดในการเชื่อมต่อข้อมูล: {e}")
    data = pd.DataFrame()

if not data.empty:
    st.markdown("### 🔴 ราคาตลาดปัจจุบัน (Real-time Market Price)")
    metric_col1, metric_col2 = st.columns([1, 3])
    with metric_col1:
        st.metric(
            label=f"ราคาล่าสุดของ {symbol}",
            value=f"{current_price:,.4f}" if "=X" in symbol else f"${current_price:,.2f}",
            delta=f"{price_change:+.4f} ({price_change_pct:+.2f}%)" if "=X" in symbol else f"${price_change:+.2f} ({price_change_pct:+.2f}%)"
        )
    with col_refresh_info:
        st.caption("🔄 **ระบบกำลังเปิดโหมด Live อัปเดตราคาอัตโนมัติทุกๆ 10 วินาที**")

    data["MA50"] = data["Close"].rolling(50).mean()
    if len(data) >= 126:
        growth = ((data["Close"].iloc[-1] - data["Close"].iloc[-126]) / data["Close"].iloc[-126]) * 100
    else:
        growth = 0

    data["Vol_Avg20"] = data["Volume"].rolling(20).mean()
    volatility = data["Close"].pct_change().tail(30).std() * 100

    score = 0
    reasons = []

    if data["Close"].iloc[-1] > data["MA50"].iloc[-1]:
        score += 30
        reasons.append("ราคาอยู่เหนือเส้น MA50 (แนวโน้มขาขึ้น)")
    else:
        reasons.append("ราคาต่ำกว่าเส้น MA50 (แนวโน้มขาลง)")

    if growth > 0:
        score += 30
        reasons.append(f"ผลตอบแทน 6 เดือนเป็นบวก (+{growth:.2f}%)")
    else:
        reasons.append(f"ผลตอบแทน 6 เดือนติดลบ ({growth:.2f}%)")

    if "=X" in symbol or symbol in ["GC=F", "SI=F", "PL=F", "CL=F"]:
        score += 20
        reasons.append("สภาพคล่องสินทรัพย์ระดับโลกสูงตลอด 24 ชั่วโมง")
    else:
        if not data["Vol_Avg20"].empty and data["Volume"].iloc[-1] > data["Vol_Avg20"].iloc[-1]:
            score += 20
            reasons.append("ราคาซื้อขายหนาแน่นกว่าค่าเฉลี่ย 20 วัน")
        else:
            reasons.append("ปริมาณการซื้อขายเบาบาง")

    if volatility < 2.5:
        score += 20
        reasons.append("ความผันผวนต่ำ สภาพคล่องค่อนข้างนิ่ง")
    else:
        reasons.append("ความผันผวนสูง มีความเสี่ยงในการแกว่งตัว")

    history_dict = {item["Ticker"]: item for item in st.session_state.search_history}
    history_dict[symbol] = {
        "Ticker": symbol,
        "Score": score,
        "ราคาปัจจุบัน": f"{current_price:,.4f}" if "=X" in symbol else f"{current_price:,.2f}",
        "เหตุผลเด่น": reasons[0] if score >= 50 else reasons[1],
    }
    st.session_state.search_history = list(history_dict.values())

    left_main_col, right_main_col = st.columns([3, 2])

    with left_main_col:
        st.subheader(f"📈 กราฟเทคนิคอลหุ้น {symbol}")
        chart_type = st.radio(
            "เลือกประเภทกราฟ:",
            ("กราฟแท่งเทียน (Candlestick)", "กราฟเส้น (Line Chart)"),
            horizontal=True,
        )
        show_ma50 = st.checkbox("แสดงเส้นค่าเฉลี่ย MA50", value=True)

        fig = go.Figure()
        if chart_type == "กราฟแท่งเทียน (Candlestick)":
            fig.add_trace(go.Candlestick(
                x=data.index, open=data["Open"], high=data["High"],
                low=data["Low"], close=data["Close"], name="ราคาแท่งเทียน",
            ))
        else:
            fig.add_trace(go.Scatter(x=data.index, y=data["Close"], mode="lines", name="ราคาปิด (Line)"))

        if show_ma50:
            fig.add_trace(go.Scatter(
                x=data.index, y=data["MA50"], mode="lines", name="MA50 Line",
                line=dict(color="orange", width=1.5),
            ))

        fig.update_layout(
            xaxis_rangeslider_visible=False,
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("🏆 อันดับสินทรัพย์น่าลงทุนที่ผ่านการวิเคราะห์")
        df_rank = pd.DataFrame(st.session_state.search_history)
        if not df_rank.empty:
            df_rank = df_rank.sort_values(by="Score", ascending=False).reset_index(drop=True)
            st.dataframe(df_rank, use_container_width=True)

    with right_main_col:
        st.subheader("💡 ผลการวิเคราะห์จาก AI")
        st.metric(label=f"AI Investment Score ({symbol})", value=f"{score} / 100")

        if score >= 80:
            st.success("🔥 สัญญาณ: น่าสนใจลงทุนสูงมาก (Strong Buy)")
        elif score >= 50:
            st.warning("⏳ สัญญาณ: ทยอยสะสม หรือรอเลือกจังหวะ (Hold/Watch)")
        else:
            st.error("🚨 สัญญาณ: ความเสี่ยงสูง ควรชะลอการลงทุน (Avoid)")

        st.write("**เหตุผลประกอบการประเมิน:**")
        for r in reasons:
            st.write(f"- {r}")

        st.markdown("---")
        st.subheader("💬 AI Trading Assistant")

        asset_type = "หุ้น"
        if "=X" in symbol:
            asset_type = "คู่เงิน Forex"
        elif symbol in ["GC=F", "XAU=F"]:
            asset_type = "ทองคำ (Gold)"
        elif symbol == "SI=F":
            asset_type = "เงิน (Silver)"
        elif symbol in ["BTC-USD", "ETH-USD"]:
            asset_type = "คริปโตเคอร์เรนซี"

        above_ma50 = "ใช่" if data["Close"].iloc[-1] > data["MA50"].iloc[-1] else "ไม่ใช่"
        signal = "Strong Buy" if score >= 80 else "Hold/Watch" if score >= 50 else "Avoid"
        price_fmt = f"{current_price:,.4f}" if "=X" in symbol else f"{current_price:,.2f}"
        change_fmt = f"{price_change:+.4f} ({price_change_pct:+.2f}%)" if "=X" in symbol else f"{price_change:+.2f} ({price_change_pct:+.2f}%)"
        reasons_str = ", ".join(reasons)

        system_prompt = (
            "คุณคือ AI Trading Assistant ผู้ช่วยด้านการเทรดและการลงทุนมืออาชีพที่พูดภาษาไทย\n\n"
            "ข้อมูลสินทรัพย์ที่ผู้ใช้กำลังดูอยู่ตอนนี้:\n"
            f"- Symbol: {symbol} ({asset_type})\n"
            f"- ราคาปัจจุบัน: {price_fmt}\n"
            f"- เปลี่ยนแปลง: {change_fmt}\n"
            f"- AI Score: {score}/100\n"
            f"- สัญญาณ: {signal}\n"
            f"- อยู่เหนือ MA50: {above_ma50}\n"
            f"- ผลตอบแทน 6 เดือน: {growth:.2f}%\n"
            f"- ความผันผวน 30 วัน: {volatility:.2f}%\n"
            f"- เหตุผลหลัก: {reasons_str}\n\n"
            "ความสามารถของคุณ:\n"
            "1. วิเคราะห์แนวโน้มตลาด หุ้น Forex ทองคำ เงิน คริปโต โลหะมีค่า น้ำมัน\n"
            "2. อธิบาย Technical Analysis (SMC, FVG, OB, BOS, MA, RSI, MACD ฯลฯ)\n"
            "3. บอกราคาตลาดโลก แนะนำให้พิมพ์ symbol ในช่องค้นหาเพื่อดูราคาจริง\n"
            "4. ให้คำแนะนำการเทรดแบบมืออาชีพ\n"
            "5. แนะนำ risk management และ position sizing\n\n"
            "สไตล์การตอบ:\n"
            "- ตอบเป็นภาษาไทยเสมอ\n"
            "- กระชับ ตรงประเด็น ใช้ emoji ประกอบ\n"
            "- ระบุว่าเป็นการวิเคราะห์เพื่อประกอบการตัดสินใจเท่านั้น"
        )

        chat_container = st.container(height=300)
        with chat_container:
            for msg in st.session_state.chat_messages:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])

        if user_query := st.chat_input("ถามเกี่ยวกับหุ้น Forex ทอง คริปโต หรือราคาตลาดโลก..."):
            st.session_state.chat_messages.append({"role": "user", "content": user_query})
            with chat_container:
                with st.chat_message("user"):
                    st.write(user_query)

            market_prices = get_market_prices_for_query(user_query)
            full_query = user_query + market_prices if market_prices else user_query

            try:
                api_key = st.secrets["GOOGLE_API_KEY"]
                client = genai.Client(api_key=api_key)

                history = []
                for m in st.session_state.chat_messages[1:-1]:
                    role = "user" if m["role"] == "user" else "model"
                    history.append({"role": role, "parts": [{"text": m["content"]}]})

                full_prompt = system_prompt + "\n\n---\n" + full_query

                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=history + [{"role": "user", "parts": [{"text": full_prompt}]}],
                )
                ai_reply = response.text

            except Exception as e:
                ai_reply = f" ขออภัย ไม่สามารถเชื่อมต่อ AI ได้: {str(e)}"

            st.session_state.chat_messages.append({"role": "assistant", "content": ai_reply})
            with chat_container:
                with st.chat_message("assistant"):
                    st.write(ai_reply)

    time.sleep(10)
    st.rerun()
