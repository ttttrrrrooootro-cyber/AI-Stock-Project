import plotly.graph_objects as go
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
st.title("AI Stock Investment Platform")

symbol = st.text_input("กรอกชื่อหุ้น", "AAPL")

data = yf.Ticker(symbol).history(period="1y")

# กราฟราคา
st.subheader("กราฟราคาหุ้น")
st.line_chart(data["Close"])

# MA50
data["MA50"] = data["Close"].rolling(50).mean()

# Growth
growth = (
    (data["Close"].iloc[-1]
    - data["Close"].iloc[-126])
    / data["Close"].iloc[-126]
) * 100

# Volume
volume_avg = data["Volume"].rolling(20).mean()

# Volatility
volatility = data["Close"].pct_change().std()

# Score
score = 0

if data["Close"].iloc[-1] > data["MA50"].iloc[-1]:
    score += 30

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
    "META"
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
