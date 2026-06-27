"""
tools.py — internal data source for the MoMo campaign team.

Mirrors the role of `product_catalog_tool` in M5_UGL_2: a small, reliable
internal catalog the agents can read. External web trends are handled by the
Gemini google_search grounding tool inside the notebook's research agent.

Each product is a flat dict — no schema classes, no registry auto-discovery.
To add a product, append one entry to CATALOG.
"""

CATALOG = {
    "bnpl": {
        "display_name": "Ví Trả Sau (BNPL)",
        "momo_urls": [
            "https://www.momo.vn/vi-tra-sau",
            "https://www.momo.vn/hoi-dap/vi-tra-sau-la-gi",
        ],
        "competitors": [
            "ZaloPay Tài Khoản Trả Sau", "Fundiin", "Kredivo",
            "Muadee by HDBank", "bePayLater", "Home Credit",
            "Shopee SPayLater", "TikTok Shop trả sau",
        ],
        "context": (
            "Trả góp 0%, duyệt eKYC nhanh, hạn mức nhỏ, nhắc lịch thanh toán là "
            "baseline — KHÔNG coi là differentiator nếu thiếu bằng chứng. Lợi thế "
            "cần kiểm chứng của MoMo: hệ sinh thái thanh toán hằng ngày (hóa đơn, "
            "tiện ích, mua sắm, bảo hiểm, giáo dục) và cá nhân hóa hạn mức theo hành vi."
        ),
        "search_terms": [
            "Ví Trả Sau MoMo", "Mua trước trả sau", "BNPL Việt Nam",
            "phí trả chậm ví trả sau", "ví trả sau có bị lên CIC không",
            "Shopee SPayLater", "Fundiin trả sau",
        ],
        "persona_hint": "Gen Z 22-27 đi làm, cần chia nhỏ chi phí mua sắm; nhạy cảm với phí và rủi ro trả chậm.",
    },
    "money_transfer": {
        "display_name": "Chuyển tiền (Money Transfer)",
        "momo_urls": [
            "https://www.momo.vn/chuyen-tien",
        ],
        "competitors": [
            "ZaloPay", "ShopeePay", "Viettel Money",
            "MB Bank", "Techcombank", "Vietcombank", "VNPAY",
        ],
        "context": (
            "Chuyển tiền 24/7 qua NAPAS 247 và quét QR VietQR là baseline trên mọi "
            "app ngân hàng/ví — KHÔNG coi là differentiator. Khác biệt phải đến từ "
            "use case cụ thể, UX, tích hợp hệ sinh thái, chính sách phí, chia tiền "
            "nhóm, yêu cầu chuyển tiền, hoặc trải nghiệm cảm xúc (lì xì, theme)."
        ),
        "search_terms": [
            "Chuyển tiền MoMo", "Chuyển tiền bằng số điện thoại", "VietQR",
            "Chia tiền nhóm", "Lì xì online", "NAPAS 247",
        ],
        "persona_hint": "Người dùng chuyển tiền cho gia đình/bạn bè; coi trọng sự tiện và cảm xúc trong giao dịch.",
    },
}


def product_catalog_tool(product_id: str) -> dict:
    """Return the internal product record. Raises KeyError with available ids."""
    if product_id not in CATALOG:
        raise KeyError(
            f"Product '{product_id}' not in catalog. Available: {list(CATALOG)}"
        )
    return CATALOG[product_id]


def list_products() -> list:
    return list(CATALOG)
