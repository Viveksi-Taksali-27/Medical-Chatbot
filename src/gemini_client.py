from google import genai
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Initialize Gemini client
def init_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in .env file.")
    genai.configure(api_key=api_key)
    client = genai.Client()
    return client


def generate_answer_from_prompt(prompt: str, model: str = "gemini-2.0-flash"):
    """
    Generate a response from the Gemini model for the given prompt.
    """
    client = init_gemini_client()
    response = client.models.generate_content(
        model=model,
        contents=prompt
    )
    return response.text
