import time
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

# 1. ตั้งค่าหน้าเว็บในสไตล์ Dashboard แบบกว้าง
st.set_page_config(page_title="AI Live Trading & Chatbot Platform", layout="wide")
st.title("🚀 AI Stock Investment & Chatbot Platform (LIVE)")

# ใช้ st.session_state สำหรับจำประวัติการค้นหาหุ้นและการคุยกับ Chatbot
if "search_history" not in st.session_state:
    st.session_state.search_history = []
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {
            "role": "assistant",
            "content": "สวัสดีครับ! พิมพ์คุยหรือสอบถามเกี่ยวกับหุ้นที่ค้นหาได้เลยครับ เช่น 'หุ้นตัวนี้แนวโน้มเป็นอย่างไรบ้าง?'",
        }
    ]

# --- ส่วนรับข้อมูลเข้า ---
col_input, col_refresh_info = st.columns([1, 2])
with col_input:
    # ลบเครื่องหมาย / ออกให้อัตโนมัติ เพื่อรองรับ EURUSD=X หรือ GC=F (ทองคำ)
    symbol = (
        st.text_input("🔍 กรอกชื่อหุ้น คู่เงิน หรือทองคำ (เช่น AAPL, EURUSD=X, GC=F)", "AAPL")
        .upper()
        .replace("/", "")
    )

# ดึงข้อมูลจาก yfinance ด้วยระบบดักจับข้อผิดพลาด
try:
    ticker = yf.Ticker(symbol)
    # ดึงข้อมูลย้อนหลัง 1 ปี (สำหรับวาดกราฟและคำนวณอินดิเคเตอร์)
    data = ticker.history(period="1y")
    
    # ดึงข้อมูลราคาล่าสุด (Real-time Market Price)
    # ใช้ข้อมูลจากวันล่าสุดใน history หรือดึงราคา fast info
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

# ทำงานต่อเมื่อดึงข้อมูลสำเร็จและมีข้อมูลอยู่จริง
if not data.empty:
    # --- แสดงราคาตลาดปัจจุบัน (Market Price Snapshot) ---
    st.markdown("### 🔴 ราคาตลาดปัจจุบัน (Real-time Market Price)")
    metric_col1, metric_col2 = st.columns([1, 3])
    with metric_col1:
        # แสดงราคาปัจจุบันพร้อมเปอร์เซ็นต์การเปลี่ยนแปลง (+/- เขียวแดงอัตโนมัติ)
        st.metric(
            label=f"ราคาล่าสุดของ {symbol}", 
            value=f"{current_price:,.4f}" if "=X" in symbol else f"${current_price:,.2f}",
            delta=f"{price_change:+.4f} ({price_change_pct:+.2f}%)" if "=X" in symbol else f"${price_change:+.2f} ({price_change_pct:+.2f}%)"
        )
    with col_refresh_info:
        st.caption("🔄 **ระบบกำลังเปิดโหมด Live อัปเดตราคาอัตโนมัติทุกๆ 10 วินาที**")

    # --- 2. การคำนวณอินดิเคเตอร์และคะแนน AI ---
    data["MA50"] = data["Close"].rolling(50).mean()

    # คำนวณ Growth (6 เดือน หรือประมาณ 126 วันทำการ)
    if len(data) >= 126:
        growth = (
            (data["Close"].iloc[-1] - data["Close"].iloc[-126])
            / data["Close"].iloc[-126]
        ) * 100
    else:
        growth = 0

    # คำนวณ Volume และ Volatility
    data["Vol_Avg20"] = data["Volume"].rolling(20).mean()
    volatility = data["Close"].pct_change().tail(30).std() * 100

    # คำนวณ Score (เต็ม 100)
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

    # ดักจับเงื่อนไขสภาพคล่องสำหรับ Forex และ ทองคำ
    if "=X" in symbol or "GC=F" in symbol:
        score += 20
        reasons.append("🌍 สภาพคล่องสินทรัพย์ระดับโลกสูงตลอด 24 ชั่วโมง (ข้ามการเช็ค Volume)")
    else:
        if data["Volume"].iloc[-1] > data["Vol_Avg20"].iloc[-1]:
            score += 20
            reasons.append("ราคาซื้อขายหนาแน่นกว่าค่าเฉลี่ย 20 วัน")
        else:
            reasons.append("ปริมาณการซื้อขายเบาบาง")

    if volatility < 2.5:
        score += 20
        reasons.append("ความผันผวนต่ำ สภาพคล่องค่อนข้างนิ่ง")
    else:
        reasons.append("ความผันผวนสูง มีความเสี่ยงในการแกว่งตัว")

    # บันทึกประวัติการค้นหาลงตารางจัดอันดับ (อัปเดตราคาล่าสุดเสมอ)
    history_dict = {
        item["Ticker"]: item for item in st.session_state.search_history
    }
    history_dict[symbol] = {
        "Ticker": symbol,
        "Score": score,
        "ราคาปัจจุบัน": f"{current_price:,.4f}" if "=X" in symbol else f"{current_price:,.2f}",
        "เหตุผลเด่น": reasons[0] if score >= 50 else reasons[1],
    }
    st.session_state.search_history = list(history_dict.values())

    # --- 3. การจัดเลย์เอาต์หน้าจอแสดงผล ---
    left_main_col, right_main_col = st.columns([3, 2])

    with left_main_col:
        # ส่วนแสดงผลกราฟเทคนิค
        st.subheader(f"📈 กราฟเทคนิคอลหุ้น {symbol}")
        chart_type = st.radio(
            "เลือกประเภทกราฟ:",
            ("กราฟแท่งเทียน (Candlestick)", "กราฟเส้น (Line Chart)"),
            horizontal=True,
        )
        show_ma50 = st.checkbox("แสดงเส้นค่าเฉลี่ย MA50", value=True)

        fig = go.Figure()

        if chart_type == "กราฟแท่งเทียน (Candlestick)":
            fig.add_trace(
                go.Candlestick(
                    x=data.index,
                    open=data["Open"],
                    high=data["High"],
                    low=data["Low"],
                    close=data["Close"],
                    name="ราคาแท่งเทียน",
                )
            )
        else:
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data["Close"],
                    mode="lines",
                    name="ราคาปิด (Line)",
                )
            )

        if show_ma50:
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data["MA50"],
                    mode="lines",
                    name="MA50 Line",
                    line=dict(color="orange", width=1.5),
                )
            )

        fig.update_layout(
            xaxis_rangeslider_visible=False,
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        )
        st.plotly_chart(fig, use_container_width=True)

        # ส่วนแสดงผลการจัดอันดับหุ้นน่าลงทุน
        st.subheader("🏆 อันดับสินทรัพย์น่าลงทุนที่ผ่านการวิเคราะห์")
        df_rank = pd.DataFrame(st.session_state.search_history)
        if not df_rank.empty:
            df_rank = df_rank.sort_values(by="Score", ascending=False).reset_index(
                drop=True
            )
            st.dataframe(df_rank, use_container_width=True)

    with right_main_col:
        # ส่วนแสดงผลคะแนนและสรุปเหตุผล
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

        # --- 4. ระบบห้องแชทจำลองตอบโต้กับ AI ---
        st.subheader("💬 AI Stock Assistant Chat")

        chat_container = st.container(height=250)
        with chat_container:
            for msg in st.session_state.chat_messages:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])

        if user_query := st.chat_input("พิมพ์คำถามของคุณที่นี่..."):
            st.session_state.chat_messages.append(
                {"role": "user", "content": user_query}
            )
            with chat_container:
                with st.chat_message("user"):
                    st.write(user_query)

            ai_reply = ""
            query_lower = user_query.lower()

            if "ซื้อ" in query_lower or "ลงทุน" in query_lower or "คำแนะนำ" in query_lower:
                if score >= 80:
                    ai_reply = f"สำหรับ {symbol} มีคะแนนสูงถึง {score}/100 ครับ เทคนิคอลเป็นขาขึ้นและโวลุ่มซัพพอร์ต ชวนให้มองเป็นโอกาสเข้าสะสมครับ"
                elif score >= 50:
                    ai_reply = f"สถานะของ {symbol} อยู่ในช่วงก้ำกึ่ง ({score}/100) แนะนำแบ่งไม้ซื้อ หรือรอให้ราคาทะลุแนวต้านสำคัญก่อนครับ"
                else:
                    ai_reply = f"ตอนนี้ {symbol} ได้คะแนนต่ำค่อนข้างน่าเป็นห่วงครับ ({score}/100) แนะนำให้รอดูสถานการณ์ไปก่อนดีกว่าครับ"
            elif "แนวโน้ม" in query_lower or "กราฟ" in query_lower or "เทคนิค" in query_lower:
                if data["Close"].iloc[-1] > data["MA50"].iloc[-1]:
                    ai_reply = f"กราฟของ {symbol} ปัจจุบันยืนอยู่เหนือเส้น MA50 ได้สะท้อนภาพเชิงบวก คาดว่ายังมีแรงเฉื่อยในทิศทางขาขึ้นต่อครับ"
                else:
                    ai_reply = f"ตอนนี้ราคาของ {symbol} หลุดเส้น MA50 ลงมา ภาพรวมติดลบระยะสั้น ต้องระวังแรงเทขายเพิ่มเติมครับ"
            elif "ราคา" in query_lower or "เท่าไหร่" in query_lower:
                ai_reply = f"ราคาปัจจุบันของ {symbol} อยู่ที่ {current_price:,.4f if '=X' in symbol else ',.2f'} ครับ"
            else:
                ai_reply = f"ผมได้รับคำถามเรื่อง '{user_query}' แล้วครับ! จากมุมมองภาพรวมของสินทรัพย์ {symbol} ปัจจุบันมี AI Score อยู่ที่ {score} คะแนน ครับ มีอะไรอยากให้ช่วยเจาะลึกเพิ่มไหมครับ?"

            st.session_state.chat_messages.append(
                {"role": "assistant", "content": ai_reply}
            )
            with chat_container:
                with st.chat_message("assistant"):
                    st.write(ai_reply)

    # --- 5. ลูปหน่วงเวลาเพื่อให้หน้าจออัปเดตราคาตลาดวิ่งตลอดเวลา ---
    time.sleep(10)
    st.rerun()

else:
    st.error(
        f"❌ ไม่พบข้อมูลของ '{symbol}' กรุณาตรวจสอบและกรอกชื่อหุ้นใหม่อีกครั้ง (เช่น AAPL, TSLA, PTT.BK, EURUSD=X, GC=F)"
    )
