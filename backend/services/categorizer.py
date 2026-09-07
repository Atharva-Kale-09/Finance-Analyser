import pandas as pd
import json
import math
import re
import logging
from google import genai

from backend.config.settings import (
    GENAI_API_KEY, MODEL_NAME, CHUNK_SIZE, CATEGORIZATION_PROMPT
)
from backend.config.category_rules import (
    KEYWORD_RULES, REGEX_RULES, TRANSACTION_CATEGORIES, 
    MERCHANT_BLOCKWORDS, COMPANY_KEYWORDS, GENERIC_BUSINESS_WORDS
)

logger = logging.getLogger(__name__)

client = genai.Client(
    api_key=GENAI_API_KEY,
    http_options={'api_version': 'v1'}
)

def clean_json_response(response_text: str) -> str:
    """Extracts JSON from LLM markdown code blocks."""
    text = response_text.strip()
    text = re.sub(r'^```json\s*|```$', '', text, flags=re.MULTILINE)
    return text.strip()

def extract_person_candidate(clean_desc: str):
    """Heuristic for Person detection. Requires 4+ letters to avoid 'XYZ' bug."""
    if not clean_desc or not isinstance(clean_desc, str): return None
    words = clean_desc.split()
    for w in words:
        w = re.sub(r'UPI$|\d+', '', w.strip())
        if w.isalpha() and 4 <= len(w) <= 15:
            if w.lower() not in GENERIC_BUSINESS_WORDS: return w
    return None

def apply_rules(row):
    """Stage 1: Fast Rule-based matching."""
    desc = str(row["Description"]).lower()
    tx_type = "INCOME" if row["Amount"] > 0 else "EXPENSE"

    for category, keywords in KEYWORD_RULES.items():
        if any(k in desc for k in keywords): return category
    
    for category, patterns in REGEX_RULES.items():
        if any(re.search(p, desc) for p in patterns): return category
    
    if tx_type == "INCOME" and any(word in desc for word in COMPANY_KEYWORDS):
        return "Salary"

    person = extract_person_candidate(str(row["Clean_Description"]))
    if person and not any(block in desc for block in MERCHANT_BLOCKWORDS):
        return "Transfer-In" if tx_type == "INCOME" else "Transfer-Out"
    return None

def categorize_transactions(df: pd.DataFrame):
    df["Category"] = None
    if "Remarks" not in df.columns:
        df["Remarks"] = ""

    # Phase 1: Local Rules
    logger.info("Executing Rule Engine...")
    df["Category"] = df.apply(apply_rules, axis=1)
    df.loc[df["Category"].notnull(), "Remarks"] = "Identified by Rule"

    missing_mask = df["Category"].isnull()
    if not missing_mask.any(): return df

    # Phase 2: Joint AI Extraction (Category + Remarks)
    to_predict = df.loc[missing_mask].copy()
    to_predict["Tx_Type"] = to_predict["Amount"].apply(lambda x: "INCOME" if x > 0 else "EXPENSE")
    unique_pairs = to_predict[["Clean_Description", "Tx_Type"]].drop_duplicates()
    inputs = list(zip(unique_pairs["Clean_Description"], unique_pairs["Tx_Type"]))
    
    logger.info(f"Using Joint AI Extraction for {len(inputs)} transactions...")
    
    ai_map = {}
    total_chunks = math.ceil(len(inputs) / CHUNK_SIZE)

    for i in range(total_chunks):
        batch = inputs[i*CHUNK_SIZE : (i+1)*CHUNK_SIZE]
        batch_text = [f"{desc} ({tx_type})" for desc, tx_type in batch]

        prompt = CATEGORIZATION_PROMPT.format(
            categories=TRANSACTION_CATEGORIES,
            batch_text="\n".join(batch_text)
        )

        try:
            response = client.models.generate_content(model=f"models/{MODEL_NAME}", contents=prompt)
            batch_results = json.loads(clean_json_response(response.text))
            
            for (desc, tx_type), res in zip(batch, batch_results):
                if isinstance(res, dict):
                    ai_map[(desc, tx_type)] = (res.get("category", "Other"), res.get("remark", ""))
                else:
                    ai_map[(desc, tx_type)] = (res, "AI categorized")
        except Exception as e:
            logger.error(f"AI Error in batch {i}: {e}")
            for (desc, tx_type) in batch: ai_map[(desc, tx_type)] = ("Other", "AI processing failed")

    # Mapping AI results back
    def map_ai_results(row):
        if pd.isna(row["Category"]):
            key = (row["Clean_Description"], "INCOME" if row["Amount"] > 0 else "EXPENSE")
            res = ai_map.get(key, ("Other", ""))
            return pd.Series([res[0], res[1]])
        return pd.Series([row["Category"], row["Remarks"]])

    df[["Category", "Remarks"]] = df.apply(map_ai_results, axis=1)
    return df