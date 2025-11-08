from flask import Flask, render_template, request, redirect, url_for, session, flash
import google.generativeai as genai
from src.helper import download_embeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from dotenv import load_dotenv
from src.prompt import *
import os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash


# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("app.secret_key")
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

# ===================== DATABASE FUNCTIONS =====================
def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_chat_history(user_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        "SELECT user_message, bot_response FROM chat_history WHERE user_id = ? ORDER BY id",
        (user_id,)
    )
    chats = c.fetchall()
    conn.close()
    return chats


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
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # ✅ Fetch chat history for logged-in user
    history = get_chat_history(session['user_id'])
    return render_template("chat.html", chat_history=history, username=session.get('username'))


@app.route("/get", methods=["GET", "POST"])
def chat():
    try:
        msg = request.form.get("msg") or request.args.get("msg")
        if not msg:
            return "Please enter a message."

        print("User Input:", msg)
        answer = generate_answer(msg)
        print("Bot Response:", answer)

        # ✅ Save chat to database only if user is logged in
        if 'user_id' in session:
            conn = get_db_connection()
            c = conn.cursor()
            c.execute(
                "INSERT INTO chat_history (user_id, user_message, bot_response) VALUES (?, ?, ?)",
                (session['user_id'], msg, answer)
            )
            conn.commit()
            conn.close()

        return answer
    except Exception as e:
        print("Error:", e)
        return "Something went wrong! Check console for details."


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                      (username, email, hashed_password))
            conn.commit()
            flash("Account created successfully! Please log in.", "success")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Username or email already exists.", "error")
        finally:
            conn.close()

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash("Logged in successfully!", "success")
            return redirect(url_for('index'))  # main chat page
        else:
            flash("Invalid username or password", "error")

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully!", "info")
    return redirect(url_for('login'))


# ===================== CHAT HISTORY =====================

@app.route('/history')
def history():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        SELECT user_message, bot_response, timestamp
        FROM chat_history
        WHERE user_id = ?
        ORDER BY timestamp DESC
    """, (session['user_id'],))
    chats = c.fetchall()
    conn.close()

    return render_template('history.html', chats=chats)

if __name__ == "__main__":
    print("Flask app started from:", os.path.abspath(__file__))
    print("Registered routes:", app.url_map)
    app.run(host="0.0.0.0", port=8080, debug=True, use_reloader=False)

