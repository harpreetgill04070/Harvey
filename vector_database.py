
# vector_database.py

import os
import asyncio
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
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,  # smaller chunks -> more embeddings -> better recall
        chunk_overlap=100,
        add_start_index=True
    )
    return splitter.split_documents(documents)

# ---- Optimized Embedding + Upsert ----
async def async_embed_and_store(documents):
    # Generate embeddings concurrently
    print(f"🔄 Generating embeddings for {len(documents)} chunks...")
    loop = asyncio.get_event_loop()
    texts = [doc.page_content for doc in documents]

    # Run embedding generation in parallel
    embeddings = await asyncio.gather(*[
        loop.run_in_executor(None, embedding_model.embed_query, text)
        for text in texts
    ])

    # Prepare vectors for Pinecone
    vectors = []
    for i, (doc, emb) in enumerate(zip(documents, embeddings)):
        vectors.append({"id": f"doc-{i}", "values": emb, "metadata": {"text": doc.page_content}})

    # Upsert to Pinecone in batches
    print(f"🚀 Uploading {len(vectors)} vectors to Pinecone...")
    index = pc.Index(INDEX_NAME)
    batch_size = 100
    for i in range(0, len(vectors), batch_size):
        index.upsert(vectors=vectors[i:i+batch_size])
    print("✅ All vectors uploaded to Pinecone.")

def store_in_pinecone(documents):
    asyncio.run(async_embed_and_store(documents))

def get_vectorstore():
    return PineconeVectorStore(index_name=INDEX_NAME, embedding=embedding_model)
