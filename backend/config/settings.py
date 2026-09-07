import os
from dotenv import load_dotenv

# Load the variables from .env into the system environment
load_dotenv()

# --- SYSTEM SETTINGS ---
# Now we fetch the key from the environment, not the code
GENAI_API_KEY = os.getenv("GENAI_API_KEY")

MODEL_NAME = "gemini-3.5-flash-lite"
CHUNK_SIZE = 35
API_BASE_URL = "http://127.0.0.1:8000"

# --- PROMPT TEMPLATES ---
CATEGORIZATION_PROMPT = """
You are a financial intelligence engine. 
Categorize these transactions into: {categories}

TASK:
For each transaction, provide:
1. The Category.
2. A 'Remark' identifying the specific Entity (Brand, Merchant, or Person) and a brief context.

EXAMPLES:
Input: "HEGANWALK 1499 (EXPENSE)"
Output: {{"category": "Shopping", "remark": "Entity: HEGANWALK (Fashion/Clothing Brand)"}}

Input: "ZOMATO*123 (EXPENSE)"
Output: {{"category": "Food", "remark": "Entity: Zomato (Food Delivery)"}}

Input: "KUNAL SHARMA (INCOME)"
Output: {{"category": "Transfer-In", "remark": "Entity: KUNAL SHARMA (Person)"}}

OUTPUT FORMAT:
Return ONLY a JSON list of objects.
Example: [{{"category": "Shopping", "remark": "Entity: HEGANWALK"}}, {{"category": "Food", "remark": "Entity: Zomato"}}]

DATA:
{batch_text}
"""