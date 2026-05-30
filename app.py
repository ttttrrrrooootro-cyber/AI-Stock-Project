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

        # --- 4. ระบบห้องแชทจำลองตอบโต้กับ AI (ปรับปรุงให้ตรงคำถาม) ---
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
            
            # ตรวจสอบประเภทสินทรัพย์ปัจจุบันที่เปิดดูอยู่ เพื่อใช้ในการตอบคำถาม
            asset_type = "หุ้น"
            if "=X" in symbol:
                asset_type = "คู่เงิน Forex"
            elif "GC=F" in symbol:
                asset_type = "ทองคำ"

            # 1. เงื่อนไขเกี่ยวกับทองคำโดยเฉพาะ
            if "ทอง" in query_lower or "gold" in query_lower or ("GC=F" in symbol and ("ซื้อ" in query_lower or "แนวโน้ม" in query_lower)):
                if "GC=F" in symbol:
                    if score >= 70:
                        ai_reply = f"ทองคำ ({symbol}) ตอนนี้ได้คะแนน {score}/100 ครับ ภาพรวมค่อนข้างแข็งแกร่งและปลอดภัย น่าสนใจพิจารณาตามแนวโน้มครับ"
                    else:
                        ai_reply = f"ภาพเทคนิคอลของ ทองคำ ({symbol}) ปัจจุบันหลุดเส้นสำคัญบางเส้น ทำให้คะแนนอยู่ที่ {score}/100 แนะนำรอสะสมเมื่อย่อตัวดีกว่าครับ"
                else:
                    ai_reply = f"หากต้องการคุยเกี่ยวกับทองคำ รบกวนพิมพ์เปลี่ยนชื่อสินทรัพย์ในช่องค้นหาด้านบนเป็น 'GC=F' ก่อนนะครับ ผมจะได้ดึงกราฟทองคำมาช่วยวิเคราะห์ให้แม่นยำยิ่งขึ้นครับ!"
            
            # 2. เงื่อนไขคำแนะนำการซื้อ/ลงทุนทั่วไป
            elif "ซื้อ" in query_lower or "ลงทุน" in query_lower or "คำแนะนำ" in query_lower:
                if score >= 80:
                    ai_reply = f"สำหรับ {symbol} ({asset_type}) มีคะแนนสูงถึง {score}/100 ครับ ปัจจัยเทคนิคอลสนับสนุนการปรับตัวขึ้น ชวนให้มองเป็นโอกาสเข้าสะสมครับ"
                elif score >= 50:
                    ai_reply = f"สถานะของ {symbol} อยู่ในช่วงพักตัวหรือสะสมกำลัง คะแนนอยู่ที่ {score}/100 แนะนำแบ่งไม้ซื้อ หรือรอเลือกจังหวะตั้งรับครับ"
                else:
                    ai_reply = f"ตอนนี้ {symbol} มีความเสี่ยงทางเทคนิคอล คะแนนค่อนข้างต่ำ ({score}/100) แนะนำชะลอการลงทุนไปก่อนครับ"
            
            # 3. เงื่อนไขแนวโน้มกราฟ
            elif "แนวโน้ม" in query_lower or "กราฟ" in query_lower or "เทคนิค" in query_lower:
                if data["Close"].iloc[-1] > data["MA50"].iloc[-1]:
                    ai_reply = f"กราฟของ {symbol} ปัจจุบันยืนอยู่เหนือเส้นค่าเฉลี่ย MA50 ได้อย่างแข็งแกร่ง สะท้อนแนวโน้มขาขึ้นในภาพรวมครับ"
                else:
                    ai_reply = f"ปัจจุบันราคาของ {symbol} ต่ำกว่าเส้น MA50 สัญญาณระยะสั้นแสดงถึงแรงเทขาย ต้องระวังการปรับฐานครับ"
            
            # 4. เงื่อนไขราคาล่าสุด
            elif "ราคา" in query_lower or "เท่าไหร่" in query_lower:
                price_fmt = f"{current_price:,.4f}" if "=X" in symbol else f"${current_price:,.2f}"
                ai_reply = f"ราคาตลาดล่าสุดของ {symbol} อยู่ที่ {price_fmt} ครับ"
            
            # 5. คำตอบแบบ Default (ในกรณีที่เดาเจตนาไม่ออก)
            else:
                ai_reply = f"เกี่ยวกับ {symbol} ({asset_type}) ปัจจุบันระบบให้คะแนน AI Score อยู่ที่ {score} คะแนนเต็ม 100 ครับ โดยมีสัญญาณสำคัญคือ {reasons[0]} อยากให้ผมช่วยวิเคราะห์จุดไหนเพิ่มเติมพิมพ์บอกได้เลยครับ!"

            st.session_state.chat_messages.append(
                {"role": "assistant", "content": ai_reply}
            )
            with chat_container:
                with st.chat_message("assistant"):
                    st.write(ai_reply)

    # --- 5. ลูปหน่วงเวลาเพื่อให้หน้าจออัปเดตราคาตลาดวิ่งตลอดเวลา ---
    time.sleep(10)
    st.rerun()
