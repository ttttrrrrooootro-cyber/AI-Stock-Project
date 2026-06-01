# ค้นหาจุดเริ่มต้นของโค้ด CSS (น่าจะอยู่แถวๆ บรรทัด 1219 หรือ 1220) 
# แล้วปรับโค้ดให้ครอบด้วย st.markdown แบบนี้ครับ:

st.markdown(
    """
    <style>
    .section-title {
        font-family: 'DM Serif Display', serif;
        font-size: 20px;
        color: var(--ink);
        border-bottom: 1.5px solid var(--border);
    }

    .metric-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
        gap: 10px;
        margin-bottom: 10px;
    }
    /* หากมีคลาส CSS อื่นๆ ด้านล่างอีก ให้ใส่ต่อในนี้ได้เลยครับ */
    </style>
    """,
    unsafe_allow_html=True
)
