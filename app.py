import streamlit as st
import os
import fitz
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.title("HIPAA Compliance Simplifier")

st.subheader("Option 1: Paste Text")
input_text = st.text_area("Paste HIPAA or healthcare policy text:")

st.subheader("Option 2: Upload a File (.txt or .pdf)")
uploaded_file = st.file_uploader("Upload a .txt or .pdf file", type=["txt", "pdf"])

if uploaded_file is not None:
    file_type = uploaded_file.name.split(".")[-1]
    if file_type == "txt":
        input_text = uploaded_file.read().decode("utf-8")
    elif file_type == "pdf":
        pdf_reader = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        pdf_text = ""
        for page in pdf_reader:
            pdf_text += page.get_text()
        input_text = pdf_text

summary = ""

if st.button("Summarize"):
    if input_text.strip() == "":
        st.warning("Please paste text or upload a file.")
    else:
        with st.spinner("Summarizing with GPT-4..."):
            try:
                response = client.chat.completions.create(
                   model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a helpful assistant that simplifies complex HIPAA and healthcare policy text. "
                                "Provide clear, concise summaries in plain language."
                            ),
                        },
                        {
                            "role": "user",
                            "content": f"Summarize the following text:\n\n{input_text}",
                        },
                    ],
                    max_tokens=500,
                    temperature=0.5,
                )
                summary = response.choices[0].message.content
                st.success("Summary:")
                st.write(summary)
            except Exception as e:
                st.error(f"Error: {str(e)}")

if summary:
    summary_bytes = summary.encode("utf-8")
    st.download_button(
        label="Download Summary as .txt",
        data=summary_bytes,
        file_name="hipaa_summary.txt",
        mime="text/plain"
    )
