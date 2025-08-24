import streamlit as st
from src.types import CodeSnippet
from src.agents import review_code

st.set_page_config(page_title="AI Code Review", layout="wide")
st.title("📝 AI Code Review Assistant")

# Language selection
language = st.selectbox(
    "Select Programming Language",
    ["python", "javascript", "java", "c", "cpp", "csharp"]
)

uploaded_file = st.file_uploader("Upload code file", type=["py", "js", "java", "c", "cpp", "cs"])

if uploaded_file:
    code_content = uploaded_file.read().decode("utf-8")
    snippet = CodeSnippet(
        id=uploaded_file.name,
        path=uploaded_file.name,
        code=code_content,
        language=language
    )

    st.subheader("📄 Uploaded Code")
    st.code(code_content, language=language)

    if st.button("Run Code Review"):
        with st.spinner("Generating suggestions..."):
            result = review_code(snippet)
        st.success("✅ Suggestions Generated!")
        st.subheader("💡 Suggestions")
        st.text(result.response)
        st.subheader("📖 Reasoning")
        st.text(result.reasoning)
