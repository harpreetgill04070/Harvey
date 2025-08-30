

from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from vector_database import get_vectorstore

llm_model = ChatGroq(model="deepseek-r1-distill-llama-70b")

def retrieve_docs(query, k=4):
    try:
        print(f"🔍 Querying Pinecone for: {query}")
        vectorstore = get_vectorstore()
        results = vectorstore.similarity_search(query, k=k)
        print(f"✅ Retrieved {len(results)} relevant chunks.")
        return results
    except Exception as e:
        print(f"❌ Retrieval failed: {e}")
        return []

def get_context(documents):
    return "\n\n".join([doc.page_content for doc in documents])

custom_prompt_template = """
Use only the context below to answer the question.
If the context doesn't contain the answer, say "I don't know".

Question: {question}
Context: {context}
Answer:
"""

def answer_query(documents, model, query):
    context = get_context(documents)
    if not context.strip():
        return "⚠️ No context found. Try re-uploading your file."
    prompt = ChatPromptTemplate.from_template(custom_prompt_template)
    chain = prompt | model
    return chain.invoke({"question": query, "context": context})
