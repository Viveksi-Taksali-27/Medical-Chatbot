from langchain_pinecone import PineconeVectorStore
from pinecone import ServerlessSpec, Pinecone
from dotenv import load_dotenv
import os
from src.helper import load_pdf_files, filter_to_minimal_docs, text_split, download_embeddings

#  Load environment variables
load_dotenv()

#  Get keys
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not PINECONE_API_KEY:
    raise ValueError("Missing PINECONE_API_KEY in .env file")

if not GEMINI_API_KEY:
    raise ValueError("Missing GEMINI_API_KEY in .env file")

# Set environment variables for Pinecone and Gemini
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY
os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY  # <--- Gemini uses GOOGLE_API_KEY

# Import Gemini SDK
from google import genai

# Initialize Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)

# Start processing
print("Loading PDF files...")
extracted_data = load_pdf_files(data='data/')

print("Cleaning and filtering document metadata...")
filtered_data = filter_to_minimal_docs(extracted_data)

print("Splitting documents into chunks...")
text_chunks = text_split(filtered_data)

print("Downloading HuggingFace embeddings...")
embeddings = download_embeddings()

print("Connecting to Pinecone...")
pc = Pinecone(api_key=PINECONE_API_KEY)
index_name = "medical-chatbot"

if not any(idx["name"] == index_name for idx in pc.list_indexes()):
    print(f"Creating new index: {index_name}")
    pc.create_index(
        name=index_name,
        dimension=384,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )
else:
    print(f"Index '{index_name}' already exists.")

# Create or connect to the index
index = pc.Index(index_name)

# Store documents in Pinecone
print(" Uploading documents to Pinecone...")
docsearch = PineconeVectorStore.from_documents(
    documents=text_chunks,
    embedding=embeddings,
    index_name=index_name
)

print("Vector store created successfully and data uploaded to Pinecone!")

