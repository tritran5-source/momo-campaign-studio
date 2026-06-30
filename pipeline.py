"""
pipeline.py — 4 agent chạy tuần tự: research → design → copy → packaging.
Mỗi hàm trả về dữ liệu thuần, không liên quan UI.
"""

import os
import re
import json
import time

import openai
from openai import OpenAI

import tools  # catalog sản phẩm MoMo

# Deploy public: key nên đặt trong Streamlit Secrets hoặc biến môi trường OPENAI_API_KEY.
# Không push hardcode key lên repo public.
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY") or ""

BRAND_PINK = "#D6218C"
BRAND = ("photorealistic lifestyle advertising photo of a REAL Vietnamese person (authentic, "
         "natural skin and expression, NOT AI-looking, NOT cartoon, NOT illustration); warm natural "
         "lighting; modern everyday Vietnamese setting; the person holds a smartphone showing the MoMo "
         "app UI in brand magenta #D6218C on a clean light interface; MoMo magenta accents; clean "
         "negative space on one side for a headline; high-end commercial campaign photography")

client = OpenAI(api_key=OPENAI_API_KEY)


def _parse_json(text: str) -> dict:
    m = re.search(r"\{.*\}", text, re.DOTALL)
    return json.loads(m.group(0)) if m else {"error": "no json", "raw": text}


def _chat(messages: list, model: str = "gpt-4o", temperature: float = 0.7,
          max_retries: int = 4) -> str:
    """Standard chat completions — retry khi gặp 429/503."""
    for attempt in range(max_retries):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
            )
            return resp.choices[0].message.content.strip()
        except openai.RateLimitError:
            if attempt < max_retries - 1:
                time.sleep(30)
                continue
            raise
        except openai.APIStatusError as e:
            if e.status_code in (503, 529) and attempt < max_retries - 1:
                time.sleep(15)
                continue
            raise


def _search(prompt: str, max_retries: int = 4) -> str:
    """Web-search-enabled chat via gpt-4o-search-preview — không truyền temperature."""
    for attempt in range(max_retries):
        try:
            resp = client.chat.completions.create(
                model="gpt-4o-search-preview",
                messages=[{"role": "user", "content": prompt}],
            )
            return resp.choices[0].message.content.strip()
        except openai.RateLimitError:
            if attempt < max_retries - 1:
                time.sleep(30)
                continue
            raise
        except openai.APIStatusError as e:
            if e.status_code in (503, 529) and attempt < max_retries - 1:
                time.sleep(15)
                continue
            raise


def _context_for(product_name: str):
    """Trả về context nội bộ nếu khớp catalog, None nếu không."""
    name = product_name.strip().lower()
    for pid in tools.list_products():
        rec = tools.product_catalog_tool(pid)
        if name == pid.lower() or name in rec["display_name"].lower() or rec["display_name"].lower() in name:
            return rec
    return None


def market_research_agent(product_name: str, campaign_context: str = "") -> str:
    from datetime import datetime
    ctx = _context_for(product_name)
    if ctx:
        background = (f"Bối cảnh nội bộ:\n"
                      f"- Đối thủ chính: {', '.join(ctx['competitors'])}\n"
                      f"- Lưu ý ngành: {ctx['context']}\n"
                      f"- Từ khóa gợi ý: {', '.join(ctx['search_terms'])}\n"
                      f"- Persona: {ctx['persona_hint']}")
    else:
        background = "Bối cảnh nội bộ: (không có sẵn — hãy tự nghiên cứu đối thủ & persona từ web)."

    context_block = f"\nBối cảnh campaign từ operator:\n{campaign_context.strip()}\n" if campaign_context.strip() else ""

    prompt = (
        f"Bạn là chuyên viên market research của MoMo. Hôm nay {datetime.now():%Y-%m-%d}.\n"
        f"Tìm hiểu xu hướng và đối thủ thực tế tại thị trường Việt Nam cho sản phẩm/tính năng \"{product_name}\".\n\n"
        f"{background}\n"
        f"{context_block}\n"
        "Chỉ dùng bằng chứng từ nguồn web công khai hiện tại. Thiếu bằng chứng thì ghi \"[Chưa đủ bằng chứng]\".\n"
        "Tổng hợp NGẮN GỌN bằng tiếng Việt:\n"
        "1. Top 2-3 xu hướng đang diễn ra (kèm vì sao).\n"
        "2. 1-2 khoảng trống thị trường MoMo có thể khai thác.\n"
        "3. Góc campaign đề xuất + persona mục tiêu + cảm xúc cần chạm."
    )
    return _search(prompt)


def designer_brief(insight: str, product_name: str, campaign_context: str = "") -> dict:
    system = "Bạn là Senior Graphic Designer tại MoMo, thiết kế cho mobile-first Việt Nam. Brand DNA bắt buộc: " + BRAND
    context_note = f"\nBối cảnh campaign: {campaign_context.strip()}" if campaign_context.strip() else ""
    user = (
        f"Insight thị trường:\n\"\"\"{insight}\"\"\"\n"
        f"Sản phẩm: {product_name}.{context_note}\n"
        "Trả về DUY NHẤT một JSON:\n"
        "{\"image_prompt\": \"100-150 từ tiếng Anh, mô tả 1 ảnh PHOTOREALISTIC: một NGƯỜI VIỆT NAM THẬT đúng persona "
        "(nêu rõ tuổi, giới tính, biểu cảm, trang phục), ánh sáng tự nhiên, bối cảnh đời thường Việt Nam. "
        f"NHẤN MẠNH BỐ CỤC: người đưa smartphone RÕ và GẦN về phía máy ảnh; MÀN HÌNH ĐIỆN THOẠI TO, SẮC NÉT, "
        f"LẤY NÉT vào màn hình, chiếm khoảng 30-40 phần trăm một bên khung hình; đọc rõ UI app MoMo (số dư, các thẻ chức năng) "
        f"màu hồng {BRAND_PINK} trên nền sáng; người ở trung cảnh hơi sau, không che màn hình. "
        "Khoảnh khắc cảm xúc gắn use case; chừa khoảng trống cho headline; phong cách ảnh quảng cáo thương mại cao cấp; "
        "KHÔNG hoạt hình, KHÔNG flat illustration, KHÔNG trông giả AI\", "
        "\"caption\": \"1 câu caption marketing tiếng Việt, ngắn và punchy\"}"
    )
    text = _chat(
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.8,
    )
    parsed = _parse_json(text)
    return {"image_prompt": parsed.get("image_prompt", ""), "caption": parsed.get("caption", "")}


def copywriter_agent(insight: str, caption: str = "") -> dict:
    instruction = (
        f"Insight thị trường:\n\"\"\"{insight}\"\"\"\n"
        f"Caption nháp: {caption}\n"
        "Trả về DUY NHẤT một JSON:\n"
        "{\"quote\": \"slogan campaign tiếng Việt, tối đa 12 từ\", "
        "\"justification\": \"1-2 câu vì sao slogan khớp insight\"}"
    )
    text = _chat(
        messages=[{"role": "user", "content": instruction}],
        temperature=0.7,
    )
    p = _parse_json(text)
    return {"quote": p.get("quote", ""), "justification": p.get("justification", "")}


def packaging_agent(insight: str, quote: str, justification: str,
                    product_name: str, image_note: str = "") -> str:
    from datetime import datetime
    system = ("Bạn là Senior Marketing Strategy Consultant, viết báo cáo executive-ready "
              "bằng tiếng Việt: ngắn gọn, bám dữ liệu, không bịa số, định hướng hành động.")
    refined = _chat(
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": f'Viết lại insight sau cho mạch lạc, chuyên nghiệp, dành cho lãnh đạo MoMo:\n"""{insight.strip()}"""'},
        ],
        temperature=0.4,
    )
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


def refresh_image_prompt(insight: str, product_name: str,
                         prev_prompt: str = "", campaign_context: str = "") -> dict:
    """Tạo lại image prompt + caption — khác với bản prev_prompt."""
    system = "Bạn là Senior Graphic Designer tại MoMo, thiết kế cho mobile-first Việt Nam. Brand DNA bắt buộc: " + BRAND
    avoid = (f"\n\nQUAN TRỌNG: Prompt sau đây là bản CŨ — KHÔNG được lặp lại concept, góc chụp, "
             f"persona, hay bối cảnh giống bản cũ:\n\"\"\"{prev_prompt}\"\"\"\n"
             "Hãy chọn một persona khác (tuổi/giới tính/trang phục khác), "
             "bối cảnh đời thường hoàn toàn khác, và khoảnh khắc cảm xúc khác.") if prev_prompt else ""
    context_note = f"\nBối cảnh campaign: {campaign_context.strip()}" if campaign_context.strip() else ""
    user = (
        f"Insight thị trường:\n\"\"\"{insight}\"\"\"\n"
        f"Sản phẩm: {product_name}.{context_note}{avoid}\n"
        "Trả về DUY NHẤT một JSON:\n"
        "{\"image_prompt\": \"100-150 từ tiếng Anh, mô tả 1 ảnh PHOTOREALISTIC: "
        "NGƯỜI VIỆT NAM THẬT đúng persona (tuổi, giới tính, biểu cảm, trang phục KHÁC bản cũ), "
        f"smartphone RÕ gần máy ảnh, màn hình MoMo {BRAND_PINK} chiếm 30-40%, "
        "không che màn hình, ánh sáng tự nhiên, khoảng trống cho headline, "
        "ảnh quảng cáo thương mại cao cấp, KHÔNG hoạt hình KHÔNG giả AI\", "
        "\"caption\": \"1 câu caption marketing tiếng Việt, ngắn và punchy, KHÁC bản cũ\"}"
    )
    text = _chat(
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.95,
    )
    parsed = _parse_json(text)
    return {"image_prompt": parsed.get("image_prompt", ""), "caption": parsed.get("caption", "")}


def refresh_slogan(insight: str, caption: str, product_name: str,
                   prev_quote: str = "", campaign_context: str = "") -> dict:
    """Tạo lại slogan + report — khác với bản prev_quote."""
    avoid = (f"\n\nQUAN TRỌNG: Slogan sau là bản CŨ — KHÔNG dùng lại từ khóa, "
             f"ý tưởng hay cấu trúc tương tự:\n\"{prev_quote}\"\n"
             "Hãy chọn một góc nhìn cảm xúc khác, một từ khóa trung tâm khác.") if prev_quote else ""
    instruction = (
        f"Insight thị trường:\n\"\"\"{insight}\"\"\"\n"
        f"Caption nháp: {caption}{avoid}\n"
        "Trả về DUY NHẤT một JSON:\n"
        "{\"quote\": \"slogan campaign tiếng Việt, tối đa 12 từ, PHẢI KHÁC bản cũ\", "
        "\"justification\": \"1-2 câu vì sao slogan này khớp insight\"}"
    )
    text = _chat(
        messages=[{"role": "user", "content": instruction}],
        temperature=0.95,
    )
    p = _parse_json(text)
    copy = {"quote": p.get("quote", ""), "justification": p.get("justification", "")}
    report_md = packaging_agent(insight, copy["quote"], copy["justification"], product_name)
    return {**copy, "report_md": report_md}


def run_pipeline(product_name: str, campaign_context: str = "") -> dict:
    name = product_name.strip()

    insight = market_research_agent(name, campaign_context)
    brief = designer_brief(insight, name, campaign_context)
    copy = copywriter_agent(insight, brief["caption"])
    report_md = packaging_agent(insight, copy["quote"], copy["justification"], name)

    return {
        "product_name": name,
        "insight": insight,
        "image_prompt": brief["image_prompt"],
        "caption": brief["caption"],
        "quote": copy["quote"],
        "justification": copy["justification"],
        "report_md": report_md,
    }
