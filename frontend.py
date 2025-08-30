

import os
import streamlit as st
import time
from vector_database import upload_pdf, load_pdf, create_chunks, store_in_pinecone
from rag_pipeline import answer_query, retrieve_docs, llm_model

st.set_page_config(page_title="AI Lawyer Chatbot", layout="wide")
st.sidebar.title("📜 Chat History")

if "history" not in st.session_state:
    st.session_state.history = []

for i, chat in enumerate(st.session_state.history):
    if st.sidebar.button(f"Chat {i+1}"):
        st.session_state.messages = chat

if st.sidebar.button("➕ New Chat"):
    st.session_state.history.append(st.session_state.get("messages", []))
    st.session_state.messages = [
        {"role": "assistant", "content": "New chat started. Upload a PDF and ask me anything 👇"}
    ]

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am your AI Lawyer. Upload a PDF and ask me anything from it 👇"}
    ]

st.title("🧑‍⚖️ AI Lawyer Chatbot")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

uploaded_file = st.file_uploader("📄 Upload a PDF", type="pdf", accept_multiple_files=False)

if uploaded_file and "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = uploaded_file.name
    upload_pdf(uploaded_file)
    file_path = os.path.join("pdfs", uploaded_file.name)

    with st.spinner("🔄 Processing and indexing PDF... This should be quick now!"):
        docs = load_pdf(file_path)
        chunks = create_chunks(docs)
        store_in_pinecone(chunks)

    st.session_state.messages.append({"role": "user", "content": f"📎 Uploaded file: {uploaded_file.name}"})
    with st.chat_message("user"):
        st.markdown(f"📎 Uploaded file: **{uploaded_file.name}**")
    st.success(f"✅ PDF processed and indexed!")

prompt = st.chat_input("Ask a question about your PDF...")

if prompt:
    if "uploaded_file_name" not in st.session_state:
        st.error("⚠️ Please upload a PDF first!")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            placeholder = st.empty()
            full_response = ""

            docs = retrieve_docs(prompt)
            if not docs:
                placeholder.markdown("⚠️ No results found. Try re-uploading your PDF.")
            else:
                response = answer_query(docs, llm_model, prompt)
                response_text = response.content if hasattr(response, "content") else str(response)

                for word in response_text.split():
                    full_response += word + " "
                    time.sleep(0.01)  # faster streaming
                    placeholder.markdown(full_response + "▌")
                placeholder.markdown(full_response)

                st.session_state.messages.append({"role": "assistant", "content": full_response})
