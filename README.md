# MoMo Campaign Studio

App Streamlit tạo campaign (research + slogan + báo cáo) bằng Gemini.

## Deploy (Streamlit Community Cloud)
1. share.streamlit.io → Create app → chọn repo này, Main file `app.py`.
2. Advanced → Secrets → dán: `GEMINI_API_KEY = "AQ.key-cua-ban"`.
3. Deploy → có URL `xxx.streamlit.app`.

## Chạy local
`pip install -r requirements.txt` rồi `GEMINI_API_KEY=... streamlit run app.py`
