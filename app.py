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

# ── Global CSS + Fonts ──────────────────────────────────────────────────────
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after { box-sizing: border-box; }
  ::selection { background: #FCE9F2; color: #B0186F; }

  /* App shell */
  html, body, .stApp { font-family: 'Be Vietnam Pro', sans-serif !important; }
  .stApp { background: #F1F1F3 !important; }
  #MainMenu, header[data-testid="stHeader"], footer { display: none !important; }
  .block-container { padding: 32px 28px !important; max-width: 1120px !important; }

  /* Headings inside st.markdown */
  h1, h2, h3, h4 { font-family: 'Be Vietnam Pro', sans-serif !important; }

  /* Inputs */
  .stTextInput input,
  .stTextArea textarea {
    font-family: 'Be Vietnam Pro', sans-serif !important;
    font-size: 15px !important; font-weight: 500 !important;
    color: #1C1C1E !important;
    border-radius: 12px !important;
    border: 1.5px solid #ECECEF !important;
    background: #FAFAFC !important;
    transition: border-color .15s, box-shadow .15s !important;
  }
  .stTextInput input:focus,
  .stTextArea textarea:focus {
    border-color: #D6218C !important;
    box-shadow: 0 0 0 4px rgba(214,33,140,.12) !important;
    outline: none !important;
  }
  .stTextInput label, .stTextArea label {
    font-size: 13px !important; font-weight: 700 !important;
    color: #1C1C1E !important; font-family: 'Be Vietnam Pro', sans-serif !important;
  }
  textarea::placeholder, input::placeholder { color: #8A8A8F !important; }

  /* Primary button */
  .stButton > button[kind="primary"] {
    font-family: 'Be Vietnam Pro', sans-serif !important;
    font-size: 15px !important; font-weight: 700 !important;
    color: #fff !important; background: #D6218C !important;
    border: none !important; border-radius: 12px !important;
    padding: 14px 20px !important;
    box-shadow: 0 4px 12px rgba(214,33,140,.32) !important;
    transition: background .15s, transform .1s !important;
  }
  .stButton > button[kind="primary"]:hover { background: #B0186F !important; }
  .stButton > button[kind="primary"]:active { transform: translateY(1px) !important; }

  /* Download button */
  .stDownloadButton > button {
    font-family: 'Be Vietnam Pro', sans-serif !important;
    font-weight: 600 !important; border-radius: 12px !important;
  }

  /* Tabs */
  .stTabs [data-baseweb="tab-list"] {
    gap: 0 !important;
    border-bottom: 1.5px solid #ECECEF !important;
    background: transparent !important;
  }
  .stTabs [data-baseweb="tab"] {
    font-family: 'Be Vietnam Pro', sans-serif !important;
    font-size: 14px !important; font-weight: 500 !important;
    color: #9AA0A6 !important; background: none !important;
    border: none !important; border-bottom: 2.5px solid transparent !important;
    padding: 9px 14px 11px !important; margin-bottom: -1.5px !important;
    transition: color .15s !important;
  }
  .stTabs [aria-selected="true"] {
    font-weight: 700 !important; color: #D6218C !important;
    border-bottom-color: #D6218C !important;
  }
  .stTabs [data-baseweb="tab-highlight"] { display: none !important; }

  /* Spinner */
  .stSpinner p { font-family: 'Be Vietnam Pro', sans-serif !important; color: #D6218C !important; }

  /* Success / warning / error */
  .stSuccess, .stWarning, .stError {
    border-radius: 12px !important;
    font-family: 'Be Vietnam Pro', sans-serif !important;
  }
</style>
""", unsafe_allow_html=True)


# ── Header ──────────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex;align-items:center;gap:14px;margin-bottom:8px;">
  <div style="width:48px;height:48px;border-radius:13px;background:#D6218C;display:flex;align-items:center;justify-content:center;box-shadow:0 8px 24px rgba(80,0,48,.16);flex-shrink:0;">
    <span style="font-size:26px;font-weight:800;color:#fff;line-height:1;font-family:'Be Vietnam Pro',sans-serif;">M</span>
  </div>
  <h1 style="margin:0;font-size:28px;font-weight:800;letter-spacing:-.5px;color:#1C1C1E;font-family:'Be Vietnam Pro',sans-serif;">MoMo Campaign Studio</h1>
  <span style="font-size:11px;font-weight:700;color:#B0186F;background:#FCE9F2;padding:5px 11px;border-radius:999px;letter-spacing:.3px;white-space:nowrap;">v1</span>
</div>
<p style="margin:0 0 24px 0;font-size:15px;color:#6B6B70;line-height:1.5;font-family:'Be Vietnam Pro',sans-serif;">
  Gõ tên sản phẩm/tính năng MoMo → nhận research thị trường, slogan và báo cáo campaign.
</p>
""", unsafe_allow_html=True)


# ── 2-Column Layout ──────────────────────────────────────────────────────────
col_left, col_right = st.columns([1, 1.75], gap="large")


# ── LEFT: Setup panel ────────────────────────────────────────────────────────
with col_left:
    st.markdown("""
    <div style="background:#fff;border-radius:20px;padding:24px 24px 20px;
                box-shadow:0 4px 16px rgba(0,0,0,.05);border:1px solid #ECECEF;">
      <div style="font-size:16px;font-weight:800;color:#1C1C1E;margin-bottom:18px;
                  font-family:'Be Vietnam Pro',sans-serif;">Thiết lập campaign</div>
    </div>
    """, unsafe_allow_html=True)

    # NOTE: inputs rendered outside the HTML div (Streamlit limitation),
    # styled via CSS above to match the card design.
    product_name = st.text_input(
        "Tên sản phẩm / tính năng MoMo",
        placeholder="VD: Ví Trả Sau, Chuyển tiền, Túi Thần Tài, Đầu tư...",
    )
    campaign_context = st.text_area(
        "Bối cảnh campaign (tùy chọn)",
        placeholder="VD: Campaign dịp Tết cho Gen Z, ngân sách 500M, kênh push + in-app, tone vui tươi...",
        height=110,
    )
    run_clicked = st.button("Tạo Campaign", type="primary", use_container_width=True)

    # Agent status (shown after a successful run)
    r_prev = st.session_state.get("result")
    if r_prev:
        st.markdown(f"""
        <div style="margin-top:18px;padding-top:18px;border-top:1px solid #F0F0F2;">
          <div style="display:flex;align-items:center;gap:9px;margin-bottom:12px;">
            <div style="width:22px;height:22px;border-radius:50%;background:#12B886;
                        display:flex;align-items:center;justify-content:center;flex-shrink:0;">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#fff"
                   stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
            </div>
            <span style="font-size:13.5px;font-weight:700;color:#0E7A53;
                         font-family:'Be Vietnam Pro',sans-serif;">
              Hoàn tất: {r_prev['product_name']}
            </span>
          </div>
          {''.join([
            f'''<div style="display:flex;align-items:center;gap:9px;padding:5px 0;">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#12B886"
                   stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0;">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
              <span style="font-size:13px;font-weight:500;color:#3A3A3C;flex:1;
                           font-family:'Be Vietnam Pro',sans-serif;">{name}</span>
              <span style="font-size:11px;font-weight:600;color:#8A8A8F;
                           font-family:'Be Vietnam Pro',sans-serif;">Hoàn tất</span>
            </div>'''
            for name in ["Nghiên cứu thị trường", "Sáng tạo slogan & caption", "Báo cáo campaign"]
          ])}
        </div>
        """, unsafe_allow_html=True)


# ── Run pipeline ─────────────────────────────────────────────────────────────
if run_clicked:
    if not product_name.strip():
        st.warning("Hãy nhập tên sản phẩm trước đã.")
    else:
        try:
            with st.spinner("Đang chạy 4 agent: research → design → copywriter → packaging ..."):
                st.session_state["result"] = pipeline.run_pipeline(
                    product_name, campaign_context=campaign_context
                )
            st.session_state["error"] = None
            st.rerun()
        except Exception as e:
            st.session_state["error"] = str(e)
            st.session_state["result"] = None

if st.session_state.get("error"):
    st.error(f"Có lỗi khi gọi OpenAI: {st.session_state['error'][:300]}")


# ── RIGHT: Results panel ──────────────────────────────────────────────────────
with col_right:
    r = st.session_state.get("result")

    if not r:
        # Empty state
        st.markdown("""
        <div style="background:#fff;border-radius:20px;padding:72px 28px;
                    box-shadow:0 4px 16px rgba(0,0,0,.05);border:1px solid #ECECEF;
                    text-align:center;">
          <div style="font-size:52px;margin-bottom:16px;">🎯</div>
          <p style="font-size:16px;font-weight:700;color:#3A3A3C;margin:0 0 8px;
                    font-family:'Be Vietnam Pro',sans-serif;">
            Nhập tên sản phẩm và bấm "Tạo Campaign"
          </p>
          <p style="font-size:14px;color:#8A8A8F;margin:0;
                    font-family:'Be Vietnam Pro',sans-serif;">
            4 agent AI sẽ tự động research, thiết kế và đóng gói campaign cho bạn.
          </p>
        </div>
        """, unsafe_allow_html=True)

    else:
        slug = re.sub(r"[^a-z0-9]+", "-", r["product_name"].lower()).strip("-") or "campaign"

        st.markdown("""
        <div style="background:#fff;border-radius:20px;padding:24px 26px 28px;
                    box-shadow:0 4px 16px rgba(0,0,0,.05);border:1px solid #ECECEF;">
        </div>
        """, unsafe_allow_html=True)

        tab1, tab2, tab3 = st.tabs(["📊 Báo cáo cuối", "🖼️ Tạo ảnh (free)", "🔍 Chi tiết từng agent"])

        # ── Tab 1: Report ────────────────────────────────────────────────────
        with tab1:
            st.markdown(r["report_md"])
            st.download_button(
                "⬇️ Tải báo cáo (.md)",
                data=r["report_md"],
                file_name=f"campaign_{slug}.md",
                mime="text/markdown",
                use_container_width=True,
            )

        # ── Tab 2: Image prompt ──────────────────────────────────────────────
        with tab2:
            # Caption card
            st.markdown(f"""
            <div style="background:#FAFAFC;border:1.5px solid #ECECEF;border-radius:14px;
                        padding:15px 18px;margin-bottom:16px;">
              <div style="font-size:11px;font-weight:700;color:#8A8A8F;
                          text-transform:uppercase;letter-spacing:.6px;margin-bottom:6px;
                          font-family:'Be Vietnam Pro',sans-serif;">Caption đề xuất</div>
              <p style="margin:0;font-size:15px;font-weight:600;color:#1C1C1E;
                        line-height:1.5;font-family:'Be Vietnam Pro',sans-serif;">
                {r['caption']}
              </p>
            </div>
            """, unsafe_allow_html=True)

            # Info hint (pink box)
            st.markdown("""
            <div style="display:flex;gap:10px;padding:13px 16px;border-radius:14px;
                        background:#FCE9F2;border:1.5px solid #F6CFE3;margin-bottom:14px;">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#D6218C"
                   stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"
                   style="flex-shrink:0;margin-top:1px;">
                <circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/>
                <line x1="12" y1="8" x2="12.01" y2="8"/>
              </svg>
              <p style="margin:0;font-size:13.5px;line-height:1.6;color:#B0186F;font-weight:600;
                        font-family:'Be Vietnam Pro',sans-serif;">
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

            # Prompt display box
            prompt_safe = r["image_prompt"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            st.markdown(f"""
            <div style="background:#FAFAFC;border-radius:14px;padding:15px 18px;
                        border:1.5px solid #ECECEF;margin-bottom:0;">
              <div style="font-size:11px;font-weight:700;color:#8A8A8F;
                          text-transform:uppercase;letter-spacing:.6px;margin-bottom:8px;
                          font-family:'Be Vietnam Pro',sans-serif;">Prompt tạo ảnh</div>
              <code style="display:block;font-family:'JetBrains Mono',monospace;
                           font-size:13px;line-height:1.65;color:#3A3A3C;
                           white-space:pre-wrap;">{prompt_safe}</code>
            </div>
            """, unsafe_allow_html=True)

            # ── Functional copy button (JS) ──────────────────────────────────
            prompt_js = (
                r["image_prompt"]
                .replace("\\", "\\\\")
                .replace("`", "\\`")
                .replace("${", "\\${")
            )
            components.html(f"""
            <link href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@700&display=swap" rel="stylesheet">
            <style>
              #copy-btn {{
                width: 100%; margin-top: 14px;
                display: flex; align-items: center; justify-content: center; gap: 8px;
                font-family: 'Be Vietnam Pro', sans-serif;
                font-size: 15px; font-weight: 700; color: #fff;
                padding: 15px; border: none; border-radius: 13px; cursor: pointer;
                background: #D6218C;
                box-shadow: 0 4px 12px rgba(214,33,140,.32);
                transition: background .18s, box-shadow .18s;
              }}
              #copy-btn:hover {{ background: #B0186F; }}
            </style>
            <button id="copy-btn" onclick="copyPrompt()">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                   stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">
                <rect x="9" y="9" width="11" height="11" rx="2"/>
                <path d="M5 15V5a2 2 0 0 1 2-2h10"/>
              </svg>
              Nhấn vào đây để copy prompt
            </button>
            <script>
            const PROMPT_TEXT = `{prompt_js}`;
            function copyPrompt() {{
              const btn = document.getElementById('copy-btn');
              navigator.clipboard.writeText(PROMPT_TEXT).then(function() {{
                btn.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none"
                  stroke="currentColor" stroke-width="2.2" stroke-linecap="round"
                  stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
                  Đã copy prompt!`;
                btn.style.background = '#12B886';
                btn.style.boxShadow = '0 4px 12px rgba(18,184,134,.32)';
                clearTimeout(btn._t);
                btn._t = setTimeout(function() {{
                  btn.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none"
                    stroke="currentColor" stroke-width="1.9" stroke-linecap="round"
                    stroke-linejoin="round"><rect x="9" y="9" width="11" height="11" rx="2"/>
                    <path d="M5 15V5a2 2 0 0 1 2-2h10"/></svg>
                    Nhấn vào đây để copy prompt`;
                  btn.style.background = '#D6218C';
                  btn.style.boxShadow = '0 4px 12px rgba(214,33,140,.32)';
                }}, 2000);
              }}, function() {{
                btn.textContent = 'Nhấn lại — có lỗi clipboard';
              }});
            }}
            </script>
            """, height=68, scrolling=False)

        # ── Tab 3: Agent details ─────────────────────────────────────────────
        with tab3:
            st.markdown("""
            <div style="font-size:15px;font-weight:700;color:#1C1C1E;margin-bottom:10px;
                        font-family:'Be Vietnam Pro',sans-serif;">1. Market Research Agent</div>
            """, unsafe_allow_html=True)
            st.markdown(r["insight"])

            st.markdown("""
            <div style="font-size:15px;font-weight:700;color:#1C1C1E;
                        margin:20px 0 10px;font-family:'Be Vietnam Pro',sans-serif;">
              3. Copywriter Agent
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"**Slogan:** {r['quote']}")
            st.caption(r["justification"])

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown("""
<p style="text-align:center;margin:24px 0 0;font-size:12px;color:#8A8A8F;
          font-family:'Be Vietnam Pro',sans-serif;">
  Powered by MoMo Design System
</p>
""", unsafe_allow_html=True)
