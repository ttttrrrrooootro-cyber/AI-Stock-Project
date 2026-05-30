import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

# ตั้งค่าหน้าเว็บให้ดูเป็นมืออาชีพ
st.set_page_config(page_title="AI Stock Investment Platform", layout="wide")
st.title("📊 AI Stock Investment Platform")

# ส่วนรับอินพุตจากผู้ใช้
symbol = st.text_input("กรอกชื่อหุ้น (เช่น AAPL, TSLA, PTT.BK)", "AAPL").upper()

# ดักจับการดึงข้อมูลเพื่อไม่ให้แอปพัง
try:
    with st.spinner("กำลังดึงข้อมูล..."):
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1y")

    if data.empty:
        st.error(
            f"ไม่พบข้อมูลสำหรับหุ้น '{symbol}' กรุณาตรวจสอบชื่อหุ้นอีกครั้ง"
        )
    else:
        # --- 1. คำนวณอินดิเคเตอร์ ---
        # MA50
        data["MA50"] = data["Close"].rolling(50).mean()

        # Growth (ประมาณ 6 เดือน หรือ 126 วันทำการ)
        if len(data) >= 126:
            growth = (
                (data["Close"].iloc[-1] - data["Close"].iloc[-126])
                / data["Close"].iloc[-126]
            ) * 100
        else:
            growth = 0  # กรณีข้อมูลไม่พอ 6 เดือน

        # Volume (ปริมาณการซื้อขายเฉลี่ย 20 วัน เทียบกับวันล่าสุด)
        data["Vol_Avg20"] = data["Volume"].rolling(20).mean()
        current_volume = data["Volume"].iloc[-1]
        avg_volume = data["Vol_Avg20"].iloc[-1]

        # Volatility (ความผันผวนย้อนหลัง 30 วัน)
        volatility = data["Close"].pct_change().tail(30).std() * 100

        # --- 2. ระบบให้คะแนน AI Score (เต็ม 100) ---
        score = 0
        reasons = []

        # เงื่อนไขที่ 1: ราคาเหนือเส้น MA50 (เทรนด์ขาขึ้น) -> 30 คะแนน
        if data["Close"].iloc[-1] > data["MA50"].iloc[-1]:
            score += 30
            reasons.append("✅ราคายังอยู่บนแนวโน้มขาขึ้น (เหนือ MA50)")
        else:
            reasons.append("❌ราคาต่ำกว่าเส้น MA50 (แนวโน้มขาลง)")

        # เงื่อนไขที่ 2: การเติบโตเป็นบวกในรอบ 6 เดือน -> 30 คะแนน
        if growth > 0:
            score += 30
            reasons.append(f"✅ผลตอบแทน 6 เดือนเป็นบวก (+{growth:.2f}%)")
        else:
            reasons.append(f"❌ผลตอบแทน 6 เดือนติดลบ ({growth:.2f}%)")

        # เงื่อนไขที่ 3: ปริมาณการซื้อขายหนาแน่นกว่าค่าเฉลี่ย -> 20 คะแนน
        if current_volume > avg_volume:
            score += 20
            reasons.append("✅ปริมาณการซื้อขายล่าสุดสูงกว่าค่าเฉลี่ย 20 วัน")
        else:
            reasons.append("❌ปริมาณการซื้อขายค่อนข้างเบาบาง")

        # เงื่อนไขที่ 4: ความผันผวนไม่สูงจนเกินไป (< 2.5%) -> 20 คะแนน
        if volatility < 2.5:
            score += 20
            reasons.append(
                f"✅ความผันผวนต่ำ สภาพคล่องมั่นคง ({volatility:.2f}%)"
            )
        else:
            reasons.append(
                f"⚠️ความผันผวนค่อนข้างสูง เสี่ยงสูง ({volatility:.2f}%)"
            )

        # --- 3. การแสดงผลบน Streamlit ---
        # แบ่งคอลัมน์แสดงข้อมูลสรุป
        col1, col2 = st.columns([1, 2])

        with col1:
            st.subheader("🤖 AI Analysis Score")
            # แสดงคะแนนขนาดใหญ่
            st.metric(label="คะแนนความน่าลงทุน", value=f"{score} / 100")

            # แสดงแถบสีตามระดับคะแนน
            if score >= 80:
                st.success("🔥 คำแนะนำ: น่าสนใจลงทุนอย่างยิ่ง (Strong Buy)")
            elif score >= 50:
                st.warning("⏳ คำแนะนำ: ถือ/รอดูจังหวะ (Hold/Watchlist)")
            else:
                st.error(
                    "🚨 คำแนะนำ: ควรหลีกเลี่ยงในตอนนี้ (Avoid/High Risk)"
                )

            # แสดงเหตุผลประกอบ
            st.write("**สรุปมุมมอง AI:**")
            for reason in reasons:
                st.write(reason)

        with col2:
            st.subheader("📈 กราฟราคาเชิงเทคนิค")
            # ใช้ Plotly เพื่อให้กราฟสวยงาม ซูมได้ และแสดงเส้น MA50 คู่กันได้
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data["Close"],
                    mode="lines",
                    name="ราคาปิด",
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data["MA50"],
                    mode="lines",
                    name="MA50",
                    line=dict(dash="dash"),
                )
            )
            fig.update_layout(
                margin=dict(l=20, r=20, t=20, b=20),
                legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
            )
            st.plotly_chart(fig, use_container_width=True)

        # ตารางข้อมูลดิบล่าสุด
        st.subheader("📋 ข้อมูลราคาล่าสุด")
        st.dataframe(data[["Close", "Volume", "MA50"]].tail(5))

except Exception as e:
    st.error(f"เกิดข้อผิดพลาดในการประมวลผล: {e}")
# 1. คำนวณค่าเฉลี่ย Volume ก่อน (ประกาศตัวแปรให้ชัดเจน)
volume_avg = data["Volume"].rolling(20).mean()

# 2. นำมาสร้างเงื่อนไขในระบบคะแนน (ตรวจสอบให้มั่นใจว่าชื่อสะกดเหมือนกันเป๊ะๆ)
if data["Volume"].iloc[-1] > volume_avg.iloc[-1]:
    score += 20
if growth > 0:
    score += 30

if volatility < 0.03:
    score += 20

st.subheader("ผลการวิเคราะห์")

st.metric("คะแนนหุ้น", score)

st.write(f"Growth 6 เดือน : {growth:.2f}%")
st.write(f"Volatility : {volatility:.4f}")

if score >= 80:
    st.success("น่าลงทุน")
elif score >= 60:
    st.warning("น่าจับตา")
else:
    st.error("ความเสี่ยงสูง")
    import plotly.graph_objects as go
fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=data.index,
        y=data["Close"],
        name="Close Price"
    )
)

fig.add_trace(
    go.Scatter(
        x=data.index,
        y=data["MA50"],
        name="MA50"
    )
)

st.plotly_chart(fig)

stocks = [
    "AAPL",
    "MSFT",
    "NVDA",
    "GOOGL",
    "META",
    "PTT",
    "TSLA",
    "NDQ",
]
results = []

for s in stocks:

    d = yf.Ticker(s).history(period="1y")

    d["MA50"] = d["Close"].rolling(50).mean()

    growth = (
        (d["Close"].iloc[-1]
        - d["Close"].iloc[-126])
        / d["Close"].iloc[-126]
    ) * 100

    volume_avg = d["Volume"].rolling(20).mean()

    volatility = d["Close"].pct_change().std()

    score = 0

    if d["Close"].iloc[-1] > d["MA50"].iloc[-1]:
        score += 30

    if d["Volume"].iloc[-1] > volume_avg.iloc[-1]:
        score += 20

    if growth > 0:
        score += 30

    if volatility < 0.03:
        score += 20

    results.append([s, score])

ranking = pd.DataFrame(
    results,
    columns=["Stock", "Score"]
)

ranking = ranking.sort_values(
    by="Score",
    ascending=False
)
ranking = ranking.reset_index(drop=True)

ranking.insert(
    0,
    "Rank",
    range(1, len(ranking) + 1)
)
st.subheader("Top 5 หุ้นน่าลงทุน")

st.dataframe(ranking)


fig = go.Figure(
    data=[
        go.Candlestick(
            x=data.index,
            open=data["Open"],
            high=data["High"],
            low=data["Low"],
            close=data["Close"]
        )
    ]
)

fig.add_trace(
    go.Scatter(
        x=data.index,
        y=data["MA50"],
        name="MA50"
    )
)

st.plotly_chart(fig, use_container_width=True)
