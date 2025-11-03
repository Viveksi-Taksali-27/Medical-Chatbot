from flask import Flask, render_template, request
import google.generativeai as genai
from src.helper import download_embeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from dotenv import load_dotenv
from src.prompt import *
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)

# 🔑 Get keys
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not PINECONE_API_KEY:
    raise ValueError("Missing PINECONE_API_KEY in .env file")

if not GEMINI_API_KEY:
    raise ValueError("Missing GEMINI_API_KEY in .env file")

# ✅ Configure Gemini (Google’s official SDK)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")  

# ✅ Setup Pinecone retriever
embeddings = download_embeddings()
index_name = "medical-chatbot"
docsearch = PineconeVectorStore.from_existing_index(
    index_name=index_name,
    embedding=embeddings
)
retriever = docsearch.as_retriever(search_type="similarity", search_kwargs={"k": 3})

# ✅ Prompt Template
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}")
])

# 🔄 Manual RAG chain using Gemini
def generate_answer(user_input):
    try:
        # Retrieve similar docs using the new method
        result = retriever.invoke(user_input)
        if isinstance(result, list):
            docs = result
        elif hasattr(result, "documents"):
            docs = result.documents
        else:
            docs = []

        if not docs:
            print("No documents found for:", user_input)
            return "Sorry, I couldn't find relevant medical information for that."

        # Combine context
        context = "\n\n".join([doc.page_content for doc in docs])

        print(f"\nRetrieved {len(docs)} documents for '{user_input}'")

        # Build final prompt
        final_prompt = f"{system_prompt}\n\nContext:\n{context}\n\nUser: {user_input}\nAnswer:"

        # Call Gemini
        response = model.generate_content(final_prompt)
        if response and hasattr(response, "text"):
            return response.text.strip()
        else:
            return "Sorry, I couldn’t generate a response."
    except Exception as e:
        print("Error in generate_answer:", e)
        return "Error: Unable to fetch answer. Check console."

@app.route("/")
def index():
    return render_template("chat.html")

@app.route("/get", methods=["GET", "POST"])
def chat():
    try:
        msg = request.form.get("msg") or request.args.get("msg")
        if not msg:
            return "Please enter a message."

        print("User Input:", msg)
        answer = generate_answer(msg)
        print("Bot Response:", answer)
        return answer
    except Exception as e:
        print("Error:", e)
        return "Something went wrong! Check console for details."

if __name__ == "__main__":
    print("Flask app started from:", os.path.abspath(__file__))
    print("Registered routes:", app.url_map)
    app.run(host="0.0.0.0", port=8080, debug=True, use_reloader=False)

