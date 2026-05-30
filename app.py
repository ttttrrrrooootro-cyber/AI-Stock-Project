import streamlit as st
import yfinance as yf

st.title("AI Stock Investment Platform")

symbol = st.text_input(
    "กรอกชื่อหุ้น",
    "AAPL"
)

data = yf.Ticker(symbol).history(period="1y")

st.line_chart(data["Close"])
