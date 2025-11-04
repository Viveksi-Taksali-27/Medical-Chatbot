# Medical-Chatbot
This is an AI-powered Medical Chatbot built with Flask, Google Gemini API, and Pinecone Vector Database.
It uses Retrieval-Augmented Generation (RAG) to provide accurate, context-based answers from a custom medical dataset.

Users can ask medical-related questions, and the chatbot retrieves the most relevant context from Pinecone and generates human-like answers using Gemini 2.5 Flash.

---

## 🚀 Features
- ✅ Conversational **AI medical assistant**  
- ✅ **Gemini 2.5 Flash** for fast and accurate responses  
- ✅ **RAG pipeline** (Retriever + LLM integration)  
- ✅ **Pinecone Vector Store** for semantic search  
- ✅ **Flask web interface** with AJAX chat frontend  

---

## 🏗️ Tech Stack
| Component | Technology |
|------------|-------------|
| **Frontend** | HTML, CSS, JavaScript (AJAX) |
| **Backend** | Flask |
| **LLM** | Google Gemini 2.5 Flash |
| **Vector Database** | Pinecone |
| **Embeddings** | Sentence Transformers |

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the repository
```bash
git clone https://github.com/yourusername/Medical-Chatbot.git
cd Medical-Chatbot
```
### 2️⃣ Create a virtual environment
```bash
python -m venv venv
venv\Scripts\activate       # For Windows
# OR
source venv/bin/activate    # For Mac/Linux
```
### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```
### 4️⃣ Create a .env file
```bash
GEMINI_API_KEY=your_gemini_api_key
PINECONE_API_KEY=your_pinecone_api_key
```
### 5️⃣ Run the Flask app
```bash
python app.py
```
#### Open your browser and visit:
🌐 http://127.0.0.1:8080

---

## 🧩 Example Query

#### User:

What are the symptoms of diabetes?

#### Chatbot:

Common symptoms of diabetes include frequent urination, increased thirst, unexplained weight loss, fatigue, and blurred vision.

---
## Screenshot
![Medical Chatbot](https://github.com/Viveksi-Taksali-27/Medical-Chatbot/blob/72bbe6aae6b68e0cd814db021248122df7a0151d/Screenshot%202025-11-04%20173150.png)

---

## 👩‍💻 Author

Viveksi Taksali
📧 viveksitaksali@gmail.com
📍 GitHub: Viveksi-Taksali-27

---
