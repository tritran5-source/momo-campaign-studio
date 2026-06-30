"""
app.py — MoMo Campaign Studio v1
Design: MoMo Campaign Studio v1.dc.html
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import streamlit.components.v1 as components

try:
    if "OPENAI_API_KEY" in st.secrets:
        os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
except Exception:
    pass

import tools
import pipeline

st.set_page_config(
    page_title="MoMo Campaign Studio",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Minimal chrome-hide (short style block, safe in all Streamlit versions) ──
st.markdown("""
<style>
#MainMenu, header[data-testid="stHeader"], footer { display: none !important; }
.block-container { padding-top: 28px !important; max-width: 1120px !important; }
</style>
""", unsafe_allow_html=True)

FNT = "font-family:'Be Vietnam Pro',sans-serif;"

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="display:flex;align-items:center;gap:14px;margin-bottom:8px;">
  <div style="width:48px;height:48px;border-radius:13px;background:#D6218C;
              display:flex;align-items:center;justify-content:center;
              box-shadow:0 8px 24px rgba(80,0,48,.16);flex-shrink:0;">
    <span style="font-size:26px;font-weight:800;color:#fff;line-height:1;{FNT}">M</span>
  </div>
  <h1 style="margin:0;font-size:28px;font-weight:800;letter-spacing:-.5px;
             color:#1C1C1E;{FNT}">MoMo Campaign Studio</h1>
  <span style="font-size:11px;font-weight:700;color:#B0186F;background:#FCE9F2;
               padding:5px 11px;border-radius:999px;letter-spacing:.3px;
               white-space:nowrap;{FNT}">1.0.0.1</span>
</div>
<p style="margin:0 0 22px;font-size:15px;color:#6B6B70;line-height:1.5;{FNT}">
  Gõ tên sản phẩm/tính năng MoMo → nhận research thị trường, slogan và báo cáo campaign.
</p>
""", unsafe_allow_html=True)

# ── 2-column layout ──────────────────────────────────────────────────────────
col_left, col_right = st.columns([1, 1.75], gap="large")

# ── LEFT: Setup panel ────────────────────────────────────────────────────────
with col_left:
    st.markdown(f"""
    <div style="background:#fff;border-radius:20px;padding:22px 22px 12px;
                box-shadow:0 4px 16px rgba(0,0,0,.05);border:1px solid #ECECEF;">
      <div style="font-size:16px;font-weight:800;color:#1C1C1E;margin-bottom:4px;{FNT}">
        Thiết lập campaign
      </div>
    </div>
    """, unsafe_allow_html=True)

    product_name = st.text_input(
        "Tên sản phẩm / tính năng MoMo",
        placeholder="VD: Ví Trả Sau, Chuyển tiền, Túi Thần Tài, Đầu tư...",
    )
    campaign_context = st.text_area(
        "Bối cảnh campaign (tùy chọn)",
        placeholder="VD: Campaign dịp Tết cho Gen Z, ngân sách 500M, kênh push + in-app...",
        height=110,
    )
    run_clicked = st.button("Tạo Campaign", type="primary", use_container_width=True)

    r_prev = st.session_state.get("result")
    if r_prev:
        agents_html = "".join([
            f"""<div style="display:flex;align-items:center;gap:9px;padding:5px 0;">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#12B886"
                   stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"
                   style="flex-shrink:0;">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
              <span style="font-size:13px;font-weight:500;color:#3A3A3C;flex:1;{FNT}">{n}</span>
              <span style="font-size:11px;font-weight:600;color:#8A8A8F;{FNT}">Hoàn tất</span>
            </div>"""
            for n in ["Nghiên cứu thị trường", "Sáng tạo slogan & caption", "Báo cáo campaign"]
        ])
        st.markdown(f"""
        <div style="margin-top:16px;padding:16px;background:#F6FFF9;
                    border-radius:14px;border:1.5px solid #D3F9E3;">
          <div style="display:flex;align-items:center;gap:9px;margin-bottom:10px;">
            <div style="width:22px;height:22px;border-radius:50%;background:#12B886;
                        display:flex;align-items:center;justify-content:center;flex-shrink:0;">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#fff"
                   stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
            </div>
            <span style="font-size:13.5px;font-weight:700;color:#0E7A53;{FNT}">
              Hoàn tất: {r_prev['product_name']}
            </span>
          </div>
          {agents_html}
        </div>
        """, unsafe_allow_html=True)

# ── Run pipeline ──────────────────────────────────────────────────────────────
if run_clicked:
    if not product_name.strip():
        st.warning("Hãy nhập tên sản phẩm trước đã.")
    else:
        try:
            with st.spinner("Đang chạy 4 agent: research → design → copywriter → packaging ..."):
                st.session_state["result"] = pipeline.run_pipeline(
                    product_name, campaign_context=campaign_context
                )
                st.session_state["campaign_context_used"] = campaign_context
            st.session_state["error"] = None
            st.rerun()
        except Exception as e:
            st.session_state["error"] = str(e)
            st.session_state["result"] = None

if st.session_state.get("error"):
    st.error(f"Có lỗi khi gọi OpenAI: {st.session_state['error'][:300]}")

# ── RIGHT: Results ────────────────────────────────────────────────────────────
with col_right:
    r = st.session_state.get("result")

    if not r:
        st.markdown(f"""
        <div style="background:#fff;border-radius:20px;padding:80px 28px;
                    box-shadow:0 4px 16px rgba(0,0,0,.05);border:1px solid #ECECEF;
                    text-align:center;">
          <div style="font-size:52px;margin-bottom:16px;">🎯</div>
          <p style="font-size:16px;font-weight:700;color:#3A3A3C;margin:0 0 8px;{FNT}">
            Nhập tên sản phẩm và bấm "Tạo Campaign"
          </p>
          <p style="font-size:14px;color:#8A8A8F;margin:0;{FNT}">
            4 agent AI sẽ tự động research, thiết kế và đóng gói campaign cho bạn.
          </p>
        </div>
        """, unsafe_allow_html=True)

    else:
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
            # Caption card
            st.markdown(f"""
            <div style="background:#FAFAFC;border:1.5px solid #ECECEF;border-radius:14px;
                        padding:15px 18px;margin-bottom:16px;">
              <div style="font-size:11px;font-weight:700;color:#8A8A8F;
                          text-transform:uppercase;letter-spacing:.6px;margin-bottom:6px;{FNT}">
                Caption đề xuất
              </div>
              <p style="margin:0;font-size:15px;font-weight:600;color:#1C1C1E;
                        line-height:1.5;{FNT}">{r['caption']}</p>
            </div>
            """, unsafe_allow_html=True)

            # Pink info box
            st.markdown(f"""
            <div style="display:flex;gap:10px;padding:13px 16px;border-radius:14px;
                        background:#FCE9F2;border:1.5px solid #F6CFE3;margin-bottom:14px;">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#D6218C"
                   stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"
                   style="flex-shrink:0;margin-top:1px;">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="16" x2="12" y2="12"/>
                <line x1="12" y1="8" x2="12.01" y2="8"/>
              </svg>
              <p style="margin:0;font-size:13.5px;line-height:1.6;color:#B0186F;
                        font-weight:600;{FNT}">
                Copy prompt bên dưới rồi dán vào
                <a href="https://chatgpt.com" target="_blank"
                   style="color:#D6218C;text-decoration:underline;">ChatGPT</a>
                hoặc
                <a href="https://gemini.google.com" target="_blank"
                   style="color:#D6218C;text-decoration:underline;">Gemini</a>
                để tạo ảnh miễn phí cho campaign.
              </p>
            </div>
            """, unsafe_allow_html=True)

            # Prompt display
            prompt_safe = (r["image_prompt"]
                           .replace("&", "&amp;")
                           .replace("<", "&lt;")
                           .replace(">", "&gt;"))
            st.markdown(f"""
            <div style="background:#FAFAFC;border-radius:14px;padding:15px 18px;
                        border:1.5px solid #ECECEF;margin-bottom:0;">
              <div style="font-size:11px;font-weight:700;color:#8A8A8F;
                          text-transform:uppercase;letter-spacing:.6px;margin-bottom:8px;{FNT}">
                Prompt tạo ảnh
              </div>
              <code style="display:block;font-family:'JetBrains Mono',monospace;
                           font-size:13px;line-height:1.65;color:#3A3A3C;
                           white-space:pre-wrap;">{prompt_safe}</code>
            </div>
            """, unsafe_allow_html=True)

            # Refresh image prompt button
            if st.button("🔄 Tạo lại prompt ảnh (khác bản này)", use_container_width=True,
                         key="refresh_prompt"):
                with st.spinner("Đang tạo prompt mới..."):
                    brief = pipeline.refresh_image_prompt(
                        r["insight"], r["product_name"],
                        prev_prompt=r.get("image_prompt", ""),
                        campaign_context=st.session_state.get("campaign_context_used", ""),
                    )
                st.session_state["result"]["image_prompt"] = brief["image_prompt"]
                st.session_state["result"]["caption"] = brief["caption"]
                st.rerun()

            # Functional copy button via iframe (not sanitized)
            prompt_js = (r["image_prompt"]
                         .replace("\\", "\\\\")
                         .replace("`", "\\`")
                         .replace("${", "\\${"))
            components.html(f"""<!DOCTYPE html><html><head>
<link href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@700&display=swap" rel="stylesheet">
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ background: transparent; padding: 14px 0 0 0; }}
#btn {{
  width: 100%;
  display: flex; align-items: center; justify-content: center; gap: 8px;
  font-family: 'Be Vietnam Pro', sans-serif; font-size: 15px; font-weight: 700;
  color: #fff; padding: 15px; border: none; border-radius: 13px; cursor: pointer;
  background: #D6218C; box-shadow: 0 4px 12px rgba(214,33,140,.32);
  transition: background .18s, box-shadow .18s;
}}
#btn:hover {{ background: #B0186F; }}
</style></head><body>
<button id="btn" onclick="doCopy()">
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor"
       stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">
    <rect x="9" y="9" width="11" height="11" rx="2"/><path d="M5 15V5a2 2 0 0 1 2-2h10"/>
  </svg>
  Nhấn vào đây để copy prompt
</button>
<script>
const TEXT = `{prompt_js}`;
function doCopy() {{
  const b = document.getElementById('btn');
  navigator.clipboard.writeText(TEXT).then(() => {{
    b.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" stroke-width="2.2" stroke-linecap="round"
      stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg> Đã copy prompt!`;
    b.style.background = '#12B886';
    b.style.boxShadow = '0 4px 12px rgba(18,184,134,.32)';
    clearTimeout(b._t);
    b._t = setTimeout(() => {{
      b.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none"
        stroke="currentColor" stroke-width="1.9" stroke-linecap="round"
        stroke-linejoin="round"><rect x="9" y="9" width="11" height="11" rx="2"/>
        <path d="M5 15V5a2 2 0 0 1 2-2h10"/></svg> Nhấn vào đây để copy prompt`;
      b.style.background = '#D6218C';
      b.style.boxShadow = '0 4px 12px rgba(214,33,140,.32)';
    }}, 2000);
  }}, () => {{ b.textContent = 'Lỗi — thử lại'; }});
}}
</script></body></html>""", height=70, scrolling=False)

        with tab3:
            st.markdown(f"""
            <div style="font-size:15px;font-weight:700;color:#1C1C1E;
                        margin-bottom:8px;{FNT}">1. Market Research Agent</div>
            """, unsafe_allow_html=True)
            st.markdown(r["insight"])
            st.markdown(f"""
            <div style="font-size:15px;font-weight:700;color:#1C1C1E;
                        margin:20px 0 8px;{FNT}">3. Copywriter Agent</div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
            <div style="background:#FAFAFC;border:1.5px solid #ECECEF;border-radius:14px;
                        padding:15px 18px;margin-bottom:12px;">
              <div style="font-size:11px;font-weight:700;color:#8A8A8F;
                          text-transform:uppercase;letter-spacing:.6px;margin-bottom:6px;{FNT}">
                Slogan đề xuất
              </div>
              <p style="margin:0 0 6px;font-size:16px;font-weight:700;color:#1C1C1E;
                        line-height:1.4;{FNT}">{r['quote']}</p>
              <p style="margin:0;font-size:13px;color:#6B6B70;line-height:1.5;{FNT}">
                {r['justification']}
              </p>
            </div>
            """, unsafe_allow_html=True)

            if st.button("🔄 Tạo lại slogan (khác bản này)", use_container_width=True,
                         key="refresh_slogan"):
                with st.spinner("Đang tạo slogan mới..."):
                    new_copy = pipeline.refresh_slogan(
                        r["insight"], r.get("caption", ""), r["product_name"],
                        prev_quote=r.get("quote", ""),
                        campaign_context=st.session_state.get("campaign_context_used", ""),
                    )
                st.session_state["result"]["quote"] = new_copy["quote"]
                st.session_state["result"]["justification"] = new_copy["justification"]
                st.session_state["result"]["report_md"] = new_copy["report_md"]
                st.rerun()

st.markdown(f"""
<p style="text-align:center;margin:20px 0 0;font-size:12px;color:#8A8A8F;{FNT}">
  Powered by MoMo Design System
</p>
""", unsafe_allow_html=True)
