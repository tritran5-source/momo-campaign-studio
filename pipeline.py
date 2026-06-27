"""
pipeline.py — 4 agent thuần (không dính UI/notebook), dùng chung cho app.py và notebook.

Mỗi agent TRẢ VỀ DỮ LIỆU (không print/display), để app web hiển thị tùy ý.
Backend: Gemini free tier (gemini-2.5-flash + google_search). Ảnh = prompt manual (free tier không sinh ảnh).
"""

import os
import re
import json
import time

from google import genai
from google.genai import types

import tools  # catalog sản phẩm MoMo

# ⚠️ Key hardcode để demo nhanh — đã lộ, NÊN ROTATE. Thực tế nên đọc os.environ["GEMINI_API_KEY"].
# Deploy public: đặt key vào Streamlit Secrets / biến môi trường GEMINI_API_KEY.
# Chạy local thì dùng fallback bên dưới. KHI PUSH REPO PUBLIC -> XOÁ chuỗi fallback để không lộ key.
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")  # đặt trong Streamlit Secrets, KHÔNG hardcode
TEXT_MODEL = "gemini-2.5-flash"          # free tier, hỗ trợ google_search

BRAND_PINK = "#D6218C"                    # accent Home Mới (memory/momo-design-system.md)
BRAND = ("photorealistic lifestyle advertising photo of a REAL Vietnamese person (authentic, "
         "natural skin and expression, NOT AI-looking, NOT cartoon, NOT illustration); warm natural "
         "lighting; modern everyday Vietnamese setting; the person holds a smartphone showing the MoMo "
         "app UI in brand magenta #D6218C on a clean light interface; MoMo magenta accents; clean "
         "negative space on one side for a headline; high-end commercial campaign photography")

client = genai.Client(api_key=GEMINI_API_KEY)


def _parse_json(text: str) -> dict:
    m = re.search(r"\{.*\}", text, re.DOTALL)
    return json.loads(m.group(0)) if m else {"error": "no json", "raw": text}


def _generate(contents, config=None, max_retries: int = 4):
    """Gọi Gemini có retry. Gặp 429 (rate limit / hết quota tạm) hoặc 503 (quá tải)
    thì đợi theo gợi ý của server rồi thử lại. Hết retry vẫn lỗi -> raise để app báo."""
    for attempt in range(max_retries):
        try:
            return client.models.generate_content(model=TEXT_MODEL, contents=contents, config=config)
        except Exception as e:
            msg = str(e)
            transient = any(k in msg for k in ("429", "503", "RESOURCE_EXHAUSTED", "UNAVAILABLE"))
            if transient and attempt < max_retries - 1:
                m = re.search(r"retry in ([0-9.]+)s", msg) or re.search(r"['\"]?([0-9]+)s['\"]?", msg)
                wait = float(m.group(1)) if m else 30.0
                time.sleep(min(wait + 2, 60))   # đợi rồi thử lại (tối đa ~60s/lần)
                continue
            raise


def _context_for(product_name: str):
    """Nếu user gõ trùng 1 sản phẩm có trong catalog (theo id hoặc tên) -> trả context nội bộ.
    Không trùng (sản phẩm tự nhập) -> None, agent sẽ tự research từ web."""
    name = product_name.strip().lower()
    for pid in tools.list_products():
        rec = tools.product_catalog_tool(pid)
        if name == pid.lower() or name in rec["display_name"].lower() or rec["display_name"].lower() in name:
            return rec
    return None


# 1) MARKET RESEARCH — Gemini + google_search. Nhận TÊN sản phẩm tự do.
def market_research_agent(product_name: str) -> str:
    from datetime import datetime
    ctx = _context_for(product_name)
    if ctx:   # có trong catalog -> nhồi bối cảnh nội bộ
        background = (f"""Bối cảnh nội bộ:
- Đối thủ chính: {", ".join(ctx['competitors'])}
- Lưu ý ngành: {ctx['context']}
- Từ khóa gợi ý: {", ".join(ctx['search_terms'])}
- Persona: {ctx['persona_hint']}""")
    else:     # sản phẩm tự nhập -> để model tự tìm
        background = "Bối cảnh nội bộ: (không có sẵn — hãy tự nghiên cứu đối thủ & persona từ web)."

    prompt = f"""Bạn là chuyên viên market research của MoMo. Hôm nay {datetime.now():%Y-%m-%d}.
Dùng google_search để tìm xu hướng và đối thủ thực tế tại thị trường Việt Nam cho sản phẩm/tính năng "{product_name}".

{background}

Chỉ dùng bằng chứng từ nguồn web công khai hiện tại. Thiếu bằng chứng thì ghi "[Chưa đủ bằng chứng]".
Tổng hợp NGẮN GỌN bằng tiếng Việt:
1. Top 2-3 xu hướng đang diễn ra (kèm vì sao).
2. 1-2 khoảng trống thị trường MoMo có thể khai thác.
3. Góc campaign đề xuất + persona mục tiêu + cảm xúc cần chạm."""
    search_tool = types.Tool(google_search=types.GoogleSearch())
    resp = _generate(prompt, config=types.GenerateContentConfig(temperature=0.4, tools=[search_tool]))
    return resp.text.strip()


# 2) GRAPHIC DESIGNER (brief) — Gemini viết image_prompt + caption (ảnh tạo thủ công ở ChatGPT/Gemini)
def designer_brief(insight: str, product_name: str) -> dict:
    system = "Bạn là Senior Graphic Designer tại MoMo, thiết kế cho mobile-first Việt Nam. Brand DNA bắt buộc: " + BRAND
    user = f"""Insight thị trường:
\"\"\"{insight}\"\"\"
Sản phẩm: {product_name}.
Trả về DUY NHẤT một JSON:
{{"image_prompt": "100-150 từ tiếng Anh, mô tả 1 ảnh PHOTOREALISTIC: một NGƯỜI VIỆT NAM THẬT đúng persona (nêu rõ tuổi, giới tính, biểu cảm, trang phục), ánh sáng tự nhiên, bối cảnh đời thường Việt Nam. NHẤN MẠNH BỐ CỤC: người đưa smartphone RÕ và GẦN về phía máy ảnh; MÀN HÌNH ĐIỆN THOẠI TO, SẮC NÉT, LẤY NÉT vào màn hình, chiếm khoảng 30-40 phần trăm một bên khung hình; đọc rõ UI app MoMo (số dư, các thẻ chức năng) màu hồng {BRAND_PINK} trên nền sáng; người ở trung cảnh hơi sau, không che màn hình. Khoảnh khắc cảm xúc gắn use case; chừa khoảng trống cho headline; phong cách ảnh quảng cáo thương mại cao cấp; KHÔNG hoạt hình, KHÔNG flat illustration, KHÔNG trông giả AI", "caption": "1 câu caption marketing tiếng Việt, ngắn và punchy"}}"""
    resp = _generate(user, config=types.GenerateContentConfig(system_instruction=system, temperature=0.8))
    parsed = _parse_json(resp.text)
    return {"image_prompt": parsed.get("image_prompt", ""), "caption": parsed.get("caption", "")}


# 3) COPYWRITER — Gemini, từ insight (+caption). Ảnh là deliverable song song nên không bắt buộc.
def copywriter_agent(insight: str, caption: str = "") -> dict:
    instruction = f"""Insight thị trường:
\"\"\"{insight}\"\"\"
Caption nháp: {caption}
Trả về DUY NHẤT một JSON:
{{"quote": "slogan campaign tiếng Việt, tối đa 12 từ", "justification": "1-2 câu vì sao slogan khớp insight"}}"""
    resp = _generate(instruction, config=types.GenerateContentConfig(temperature=0.7))
    p = _parse_json(resp.text)
    return {"quote": p.get("quote", ""), "justification": p.get("justification", "")}


# 4) PACKAGING — Gemini viết lại insight executive + ghép thành markdown (trả về STRING, app tự tải/hiển thị)
def packaging_agent(insight: str, quote: str, justification: str,
                    product_name: str, image_note: str = "") -> str:
    from datetime import datetime
    system = ("Bạn là Senior Marketing Strategy Consultant, viết báo cáo executive-ready "
              "bằng tiếng Việt: ngắn gọn, bám dữ liệu, không bịa số, định hướng hành động.")
    resp = _generate(
        f'Viết lại insight sau cho mạch lạc, chuyên nghiệp, dành cho lãnh đạo MoMo:\n"""{insight.strip()}"""',
        config=types.GenerateContentConfig(system_instruction=system, temperature=0.4),
    )
    refined = resp.text.strip()
    img_md = image_note or "*(Ảnh: dùng Image Prompt bên dưới tạo tại ChatGPT hoặc Gemini rồi chèn vào)*"
    return f"""# 🎯 MoMo {product_name} - Tóm tắt Campaign (Executive)

## 📊 Insight thị trường
{refined}

## 🖼️ Concept hình ảnh
{img_md}

## ✍️ Slogan đề xuất
**{quote.strip()}**

## ✅ Vì sao hiệu quả
{justification.strip()}

---
*Báo cáo tạo ngày {datetime.now():%Y-%m-%d}*
"""


# ===== Nhạc trưởng: chạy trọn 4 agent, trả về dict cho UI =====
def run_pipeline(product_name: str) -> dict:
    name = product_name.strip()

    insight = market_research_agent(name)                     # 1
    brief = designer_brief(insight, name)                     # 2
    copy = copywriter_agent(insight, brief["caption"])        # 3
    report_md = packaging_agent(insight, copy["quote"],
                                copy["justification"], name)   # 4

    return {
        "product_name": name,
        "insight": insight,
        "image_prompt": brief["image_prompt"],
        "caption": brief["caption"],
        "quote": copy["quote"],
        "justification": copy["justification"],
        "report_md": report_md,
    }
