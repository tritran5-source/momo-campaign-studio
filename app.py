"""
app.py — giao diện web cho Growth PM.
Chạy: streamlit run app.py
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st

# Streamlit Cloud: secrets phải load vào env trước khi import pipeline
try:
    if "OPENAI_API_KEY" in st.secrets:
        os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
except Exception:
    pass

import tools
import pipeline

st.set_page_config(page_title="MoMo Campaign Studio", page_icon="🎯", layout="centered")

# ---- Header ----
st.markdown(
    "<h1 style='color:#D6218C;margin-bottom:0'>🎯 MoMo Campaign Studio</h1>"
    "<p style='color:#6B6B70;margin-top:4px'>Gõ tên sản phẩm/tính năng MoMo → nhận research thị trường, "
    "slogan và báo cáo campaign.</p>",
    unsafe_allow_html=True,
)

# ---- Input ----
product_name = st.text_input(
    "Tên sản phẩm / tính năng MoMo",
    placeholder="VD: Ví Trả Sau, Chuyển tiền, Túi Thần Tài, Đầu tư, Tiết kiệm...",
)

campaign_context = st.text_area(
    "Bối cảnh campaign (tùy chọn)",
    placeholder="VD: Campaign dịp Tết cho Gen Z, ngân sách 500M, kênh push notification + in-app, tone vui tươi...",
    height=80,
)

if st.button("🚀 Tạo Campaign", type="primary", use_container_width=True):
    if not product_name.strip():
        st.warning("Hãy nhập tên sản phẩm trước đã.")
    else:
        try:
            with st.spinner("Đang chạy 4 agent: research → design → copywriter → packaging ..."):
                st.session_state["result"] = pipeline.run_pipeline(
                    product_name, campaign_context=campaign_context
                )
            st.session_state["error"] = None
        except Exception as e:
            st.session_state["error"] = str(e)
            st.session_state["result"] = None

# ---- Lỗi ----
if st.session_state.get("error"):
    st.error(f"Có lỗi khi gọi OpenAI: {st.session_state['error'][:300]}\n\nThử bấm lại sau vài giây.")

# ---- Kết quả ----
r = st.session_state.get("result")
if r:
    st.success(f"Hoàn tất campaign cho: {r['product_name']}")
    slug = re.sub(r"[^a-z0-9]+", "-", r["product_name"].lower()).strip("-") or "campaign"

    tab1, tab2, tab3 = st.tabs(["📊 Báo cáo cuối", "🖼️ Tạo ảnh (free)", "🔍 Chi tiết từng agent"])

    with tab1:
        st.markdown(r["report_md"])
        st.download_button(
            "⬇️ Tải báo cáo (.md)",
            data=r["report_md"],
            file_name=f"campaign_{slug}.md",
            mime="text/markdown",
            use_container_width=True,
        )

    with tab2:
        st.write(f"**Caption đề xuất:** {r['caption']}")
        st.info(
            "📋 **Bấm icon copy ở góc trên phải ↗ của khung dưới** — rồi dán vào "
            "[ChatGPT](https://chatgpt.com) hoặc [Gemini](https://gemini.google.com) "
            "để tạo ảnh **miễn phí** cho campaign:"
        )
        st.code(r["image_prompt"], language=None)

    with tab3:
        st.subheader("1. Market Research Agent")
        st.markdown(r["insight"])
        st.subheader("3. Copywriter Agent")
        st.markdown(f"**Slogan:** {r['quote']}")
        st.caption(r["justification"])
