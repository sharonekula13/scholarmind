import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="ScholarMind", page_icon="🧠", layout="wide")
if st.sidebar.button("🗑️ Clear All Documents"):
    requests.post(f"{API_URL}/clear")
    st.session_state["uploaded"] = []
    st.session_state["messages"] = []
    st.rerun()
st.title("🧠 ScholarMind")
st.subheader("AI Research Paper Assistant")
st.markdown("Upload academic papers and ask questions. Get citation-backed answers.")

st.sidebar.header("📄 Upload Papers")
uploaded_files = st.sidebar.file_uploader(
    "Upload PDF files",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:
    for file in uploaded_files:
        if file.name not in st.session_state.get("uploaded", []):
            with st.sidebar.status(f"Processing {file.name}..."):
                response = requests.post(
                    f"{API_URL}/upload",
                    files={"file": (file.name, file.getvalue(), "application/pdf")}
                )
                if response.status_code == 200:
                    result = response.json()
                    st.sidebar.success(f"✅ {file.name}: {result['chunks']} chunks indexed")
                    if "uploaded" not in st.session_state:
                        st.session_state["uploaded"] = []
                    st.session_state["uploaded"].append(file.name)
                else:
                    st.sidebar.error(f"❌ Failed to process {file.name}")

st.sidebar.divider()
doc_response = requests.get(f"{API_URL}/documents")
if doc_response.status_code == 200:
    docs = doc_response.json()
    st.sidebar.metric("Total Chunks Indexed", docs["total_chunks"])
    if docs["uploaded_files"]:
        st.sidebar.write("**Uploaded files:**")
        for f in docs["uploaded_files"]:
            st.sidebar.write(f"📄 {f}")

st.divider()

if "messages" not in st.session_state:
    st.session_state["messages"] = []

for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

question = st.chat_input("Ask a question about your papers...")

if question:
    st.session_state["messages"].append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching papers and generating answer..."):
            response = requests.post(
                f"{API_URL}/query",
                json={"question": question, "top_k": 5}
            )
            if response.status_code == 200:
                result = response.json()
                answer = result["answer"]
                sources = result["sources"]
                full_response = f"{answer}\n\n📖 **Sources:** Pages {sources}"
                st.markdown(full_response)
                st.session_state["messages"].append({"role": "assistant", "content": full_response})
            else:
                st.error("Failed to get answer. Is the API running?")