"""
app.py — Giao diện web cho Growth PMs. KHÔNG cần mở notebook, không chạy từng cell.

Chạy:  streamlit run app.py
PM chỉ: gõ tên sản phẩm → bấm "Tạo Campaign" → nhận Báo cáo + Slogan + Image Prompt.
"""

import os
import re
import sys

# Đảm bảo import được tools.py / pipeline.py nằm cùng thư mục dù chạy từ đâu
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st

# Streamlit Cloud: đọc key từ Secrets -> env TRƯỚC khi import pipeline
try:
    if "GEMINI_API_KEY" in st.secrets:
        os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
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

# ---- Input: user TỰ NHẬP tên sản phẩm ----
product_name = st.text_input(
    "Tên sản phẩm / tính năng MoMo",
    placeholder="VD: Ví Trả Sau, Chuyển tiền, Túi Thần Tài, Đầu tư, Tiết kiệm...",
)

if st.button("🚀 Tạo Campaign", type="primary", use_container_width=True):
    if not product_name.strip():
        st.warning("Hãy nhập tên sản phẩm trước đã.")
    else:
        try:
            with st.spinner("Đang chạy 4 agent: research → design → copywriter → packaging ..."):
                st.session_state["result"] = pipeline.run_pipeline(product_name)
            st.session_state["error"] = None
        except Exception as e:
            st.session_state["error"] = str(e)
            st.session_state["result"] = None

# ---- Lỗi (vd Gemini quá tải / hết quota tạm) ----
if st.session_state.get("error"):
    st.error(f"Có lỗi khi gọi Gemini: {st.session_state['error'][:300]}\n\nThử bấm lại sau vài giây.")

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
        st.write(
            "Dán prompt dưới đây vào "
            "[ChatGPT](https://chatgpt.com) hoặc [Gemini](https://gemini.google.com) "
            "để tạo ảnh **miễn phí**, rồi dùng cho campaign:"
        )
        st.code(r["image_prompt"], language=None)

    with tab3:
        st.subheader("1. Market Research Agent")
        st.markdown(r["insight"])
        st.subheader("3. Copywriter Agent")
        st.markdown(f"**Slogan:** {r['quote']}")
        st.caption(r["justification"])

st.markdown(
    "<hr><p style='color:#8A8A8F;font-size:0.8em'>Backend: Gemini free tier. "
    "Ảnh tạo thủ công (free tier không sinh ảnh). Brand: Home Mới #D6218C.</p>",
    unsafe_allow_html=True,
)
