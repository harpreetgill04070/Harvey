# vector_database.py

import os
import concurrent.futures
from dotenv import load_dotenv
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = "ai-lawyer-index"
pdfs_directory = "pdfs/"

# 🔧 Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)

# 🔧 Setup Embedding Model
ollama_model_name = "deepseek-r1:1.5b"
embedding_model = OllamaEmbeddings(model=ollama_model_name)

print("🔎 Detecting embedding dimension...")
test_vector = embedding_model.embed_query("ping")
EMBEDDING_DIM = len(test_vector)
print(f"✅ Embedding dimension detected: {EMBEDDING_DIM}")

# 🔧 Ensure Pinecone index exists
existing_indexes = [i["name"] for i in pc.list_indexes()]
if INDEX_NAME not in existing_indexes:
    print(f"📌 Creating Pinecone index: {INDEX_NAME}")
    pc.create_index(
        name=INDEX_NAME,
        dimension=EMBEDDING_DIM,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )
else:
    print(f"✅ Pinecone index '{INDEX_NAME}' already exists.")

# ---- PDF & Chunk Handling ----
def upload_pdf(file):
    os.makedirs(pdfs_directory, exist_ok=True)
    with open(os.path.join(pdfs_directory, file.name), "wb") as f:
        f.write(file.getbuffer())

def load_pdf(file_path):
    loader = PDFPlumberLoader(file_path)
    return loader.load()

def create_chunks(documents):
    """Optimized: creates chunks faster by using fewer overlaps & smaller chunk size."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,  # ✅ slightly smaller chunks = faster embedding + good recall
        chunk_overlap=50,
        add_start_index=True
    )
    return splitter.split_documents(documents)

# ---- Optimized Embedding + Upsert ----
def store_in_pinecone(documents):
    print(f"🔄 Generating embeddings for {len(documents)} chunks...")

    texts = [doc.page_content for doc in documents]

    # ✅ ThreadPoolExecutor for parallel embeddings
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        embeddings = list(executor.map(embedding_model.embed_query, texts))

    vectors = [
        {"id": f"doc-{i}", "values": emb, "metadata": {"text": doc.page_content}}
        for i, (doc, emb) in enumerate(zip(documents, embeddings))
    ]

    print(f"🚀 Uploading {len(vectors)} vectors to Pinecone...")
    index = pc.Index(INDEX_NAME)

    # ✅ Batch upload for faster throughput
    batch_size = 100
    for i in range(0, len(vectors), batch_size):
        index.upsert(vectors=vectors[i:i+batch_size])

    print("✅ All vectors uploaded to Pinecone.")

def get_vectorstore():
    return PineconeVectorStore(index_name=INDEX_NAME, embedding=embedding_model)
