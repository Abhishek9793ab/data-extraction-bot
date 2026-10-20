
import json
import os
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

from extractor import ExtractionError, extract
from schemas import SCHEMAS


load_dotenv()

st.set_page_config(
    page_title="ExtractIQ | AI Data Extraction",
    page_icon="🧾",
    layout="wide",
)

SAMPLES = {
    "Resume": """Rahul Sharma
Email: rahul@example.com
Phone: +91 98765 43210
Skills: Python, SQL, LangChain, Streamlit
Education: B.Tech Computer Science, JECRC Jaipur, 2024
Experience: Built two LLM projects during an internship at XYZ Tech.""",

    "Invoice": """INVOICE #INV-2026-045
Date: 15 Oct 2026
From: Pink City Supplies
Bill to: Aman Traders
2 x Laptop Stand @ 1500 = 3000
5 x USB Cable @ 200 = 1000
Total: INR 4000""",
}

st.markdown("""
<style>
.block-container {
    max-width: 1250px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}
.hero {
    background: linear-gradient(120deg, #171b3b, #5145cd);
    padding: 28px;
    border-radius: 18px;
    color: white;
    margin-bottom: 24px;
}
.hero h1 {
    color: white;
    margin-bottom: 8px;
}
.hero p {
    color: #e2e4ff;
    margin-bottom: 0;
}
div[data-testid="stMetric"] {
    border: 1px solid rgba(128,128,150,.25);
    border-radius: 12px;
    padding: 12px;
}
</style>
""", unsafe_allow_html=True)


with st.sidebar:
    st.header("⚙️ Settings")

    api_key = st.text_input(
        "Gemini API key",
        value=os.getenv("GEMINI_API_KEY", ""),
        type="password",
        help="Never commit your API key to GitHub.",
    )

    model = st.text_input(
        "Gemini model",
        value=os.getenv("GEMINI_MODEL", "gemini-3.8-flash"),
    )

    doc_type = st.radio(
        "Document type",
        list(SCHEMAS.keys()),
    )

    st.divider()
    st.caption("Your API key should be configured privately on Render.")


st.markdown("""
<div class="hero">
    <h1>🧾 ExtractIQ</h1>
    <p>Transform unstructured text into structured, validated JSON using AI.</p>
</div>
""", unsafe_allow_html=True)


m1, m2, m3 = st.columns(3)
m1.metric("Document types", "2")
m2.metric("Output", "Validated JSON")
m3.metric("Workflow", "Extract · Review · Download")


left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("① Input document")

    use_sample = st.toggle("Use example text", value=True)

    text = st.text_area(
        "Document content",
        value=SAMPLES[doc_type] if use_sample else "",
        height=320,
        placeholder="Paste resume or invoice text here...",
    )

    st.caption(f"Characters: {len(text):,}")

    extract_clicked = st.button(
        "✨ Extract structured data",
        type="primary",
        use_container_width=True,
    )


with right:
    st.subheader("② Extracted JSON")

    if extract_clicked:

        if not api_key.strip():
            st.error("Enter your Gemini API key in the sidebar.")

        elif not model.strip():
            st.error("Enter a Gemini model name.")

        elif not text.strip():
            st.error("Please enter some document text.")

        elif len(text) > 100_000:
            st.error("Input is too long. Maximum length is 100,000 characters.")

        else:
            try:
                with st.spinner("Extracting and validating data..."):
                    result = extract(
                        api_key=api_key,
                        text=text,
                        schema=SCHEMAS[doc_type],
                        model=model,
                    )

                data = result.model_dump(mode="json")

                st.session_state["result"] = data
                st.session_state["result_type"] = doc_type
                st.session_state["result_model"] = model
                st.session_state["result_time"] = (
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )

                st.success("Extraction completed.")

            except ExtractionError as exc:
                st.error(str(exc))

            except Exception:
                st.error(
                    "Unexpected error occurred. Check your terminal or "
                    "Render logs for details."
                )

    if "result" in st.session_state:
        data = st.session_state["result"]

        st.json(data)

        st.download_button(
            "⬇️ Download JSON",
            data=json.dumps(data, indent=2, ensure_ascii=False),
            file_name=f"{st.session_state['result_type'].lower()}_extracted.json",
            mime="application/json",
            use_container_width=True,
        )

        with st.expander("Extraction details"):
            st.write("Document type:", st.session_state["result_type"])
            st.write("Model:", st.session_state["result_model"])
            st.write("Completed:", st.session_state["result_time"])

    else:
        st.info("Your extracted data will appear here after extraction.")

        st.code(
            '{\n  "name": "Rahul Sharma",\n'
            '  "email": "rahul@example.com",\n'
            '  "skills": ["Python", "SQL"]\n}',
            language="json",
        )


st.divider()

st.markdown(
    "<div style='text-align:center;color:#85889b'>"
    "ExtractIQ · Streamlit · Google Gemini · Pydantic"
    "</div>",
    unsafe_allow_html=True,
)
