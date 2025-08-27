



# # frontend.py

# import streamlit as st
# import time
# from rag_pipeline import answer_query, retrieve_docs, llm_model

# # -------------------------
# # App Intro
# # -------------------------
# st.title("🧑‍⚖️ AI Lawyer Chatbot")
# st.write("Upload a PDF and chat with your AI Lawyer! ⚖️")

# # -------------------------
# # File uploader
# # -------------------------
# uploaded_file = st.file_uploader("📄 Upload a PDF", type="pdf", accept_multiple_files=False)

# if not uploaded_file:
#     st.warning("Please upload a PDF first to start chatting.")
# else:
#     st.success(f"PDF uploaded: {uploaded_file.name}")

# # -------------------------
# # Initialize chat history
# # -------------------------
# if "messages" not in st.session_state:
#     st.session_state.messages = [
#         {"role": "assistant", "content": "Hello! I am your AI Lawyer. Upload a PDF and ask me anything from it 👇"}
#     ]

# # -------------------------
# # Display chat history
# # -------------------------
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])

# # -------------------------
# # Chat Input
# # -------------------------
# if prompt := st.chat_input("Ask a question about your PDF..."):
#     if not uploaded_file:
#         st.error("⚠️ You must upload a PDF before asking questions!")
#     else:
#         # Add user message to history
#         st.session_state.messages.append({"role": "user", "content": prompt})

#         # Display user message
#         with st.chat_message("user"):
#             st.markdown(prompt)

#         # Process query using RAG pipeline
#         with st.chat_message("assistant"):
#             message_placeholder = st.empty()
#             full_response = ""

#             retrieved_docs = retrieve_docs(prompt)
#             response = answer_query(documents=retrieved_docs, model=llm_model, query=prompt)

#             # ✅ Ensure response is plain text (AIMessage -> str)
#             if hasattr(response, "content"):
#                 response_text = response.content
#             else:
#                 response_text = str(response)

#             # Simulate typing effect
#             for chunk in response_text.split():
#                 full_response += chunk + " "
#                 time.sleep(0.03)
#                 message_placeholder.markdown(full_response + "▌")
#             message_placeholder.markdown(full_response)

#         # Add assistant response to history
#         st.session_state.messages.append({"role": "assistant", "content": full_response})




# frontend.py

import streamlit as st
import time
from rag_pipeline import answer_query, retrieve_docs, llm_model

# -------------------------
# Page Config
# -------------------------
st.set_page_config(page_title="AI Lawyer Chatbot", layout="wide")

# -------------------------
# Sidebar (History)
# -------------------------
st.sidebar.title("📜 Chat History")

if "history" not in st.session_state:
    st.session_state.history = []  # store past conversations

# Show history in sidebar
for i, chat in enumerate(st.session_state.history):
    if st.sidebar.button(f"Chat {i+1}"):
        st.session_state.messages = chat

# Button to start a new chat
if st.sidebar.button("➕ New Chat"):
    st.session_state.history.append(st.session_state.get("messages", []))
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am your AI Lawyer. Upload a PDF and ask me anything from it 👇"}
    ]

# -------------------------
# Initialize Chat Messages
# -------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am your AI Lawyer. Upload a PDF and ask me anything from it 👇"}
    ]

# -------------------------
# Chat UI
# -------------------------
st.title("🧑‍⚖️ AI Lawyer Chatbot")

# Display chat history (above input)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# -------------------------
# File Upload (inline like ChatGPT + button)
# -------------------------
uploaded_file = st.file_uploader(
    "📄 Upload a PDF", 
    type="pdf", 
    accept_multiple_files=False,
    label_visibility="collapsed",
    key="file_uploader"
)

if uploaded_file and "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = uploaded_file.name
    st.session_state.messages.append({"role": "user", "content": f"📎 Uploaded file: {uploaded_file.name}"})
    with st.chat_message("user"):
        st.markdown(f"📎 Uploaded file: **{uploaded_file.name}**")
    st.success(f"PDF uploaded: {uploaded_file.name}")

# -------------------------
# Chat Input (ALWAYS at bottom)
# -------------------------
prompt = st.chat_input("Ask a question about your PDF...")

# -------------------------
# Handle Chat Input
# -------------------------
if prompt:
    if not uploaded_file:
        st.error("⚠️ You must upload a PDF before asking questions!")
    else:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate assistant response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

            retrieved_docs = retrieve_docs(prompt)
            response = answer_query(documents=retrieved_docs, model=llm_model, query=prompt)

            # ✅ Extract text if AIMessage
            if hasattr(response, "content"):
                response_text = response.content
            else:
                response_text = str(response)

            # Simulate typing effect
            for chunk in response_text.split():
                full_response += chunk + " "
                time.sleep(0.03)
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)

        # Save assistant response
        st.session_state.messages.append({"role": "assistant", "content": full_response})
