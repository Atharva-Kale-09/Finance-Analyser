import pandas as pd
import re
from backend.config.bank_configs import BANK_CONFIGS, TRANSACTION_PREFIXES, COMMON_BANK_CODES

def detect_bank(df: pd.DataFrame):
    """
    Identifies the bank format based on the presence of specific columns.
    """
    columns = set(df.columns.str.strip())

    if {"Tran Date", "PARTICULARS", "DR", "CR"}.issubset(columns):
        return "axis"
    elif {"Date", "Remarks", "Debit", "Credit"}.issubset(columns):
        return "boi"
    elif {"Date", "Description", "Amount"}.issubset(columns):
        return "generic"
    else:
        raise ValueError("Unsupported bank format. Please check column headers.")

def clean_description(text):
    """
    Sanitizes description by removing known bank artifacts and prefixes.
    """
    if not isinstance(text, str):
        return ""
        
    original_text = text.upper()
    clean_text = original_text
    
    # 1. Remove standard bank prefixes
    for p in TRANSACTION_PREFIXES:
        clean_text = clean_text.replace(p, " ")

    # 2. Remove common Bank Codes if they appear as standalone words
    for code in COMMON_BANK_CODES:
        clean_text = re.sub(r'\b' + code + r'\b', ' ', clean_text)
        
    # 3. Remove "DR" or "CR" only if standalone
    clean_text = re.sub(r'\b(DR|CR)\b', ' ', clean_text)
    
    # 4. Remove pure numeric tokens (Transaction IDs)
    tokens = clean_text.split()
    final_tokens = []
    
    for token in tokens:
        if token.isdigit() and len(token) > 4:
            continue
        
        # Remove special chars but keep spaces
        cleaned_token = re.sub(r'[^A-Z0-9]', '', token)
        if len(cleaned_token) > 1:
            final_tokens.append(cleaned_token)
            
    result = " ".join(final_tokens).strip()
    return result if result else original_text


def normalize_dataframe(df: pd.DataFrame, bank_name: str):
    """
    Standardizes dataframe columns and types.
    """
    df.columns = df.columns.str.strip()
    config = BANK_CONFIGS[bank_name]

    df = df.rename(columns={
        config["date"]: "Date",
        config["description"]: "Description"
    })

    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors='coerce')

    # Handle Debit/Credit columns vs single Amount column
    if "debit" in config and "credit" in config:
        def clean_money(val):
            if pd.isna(val): return 0.0
            val = str(val).replace(",", "").replace("₹", "").strip()
            if val == "": return 0.0
            return float(val)

        df["Debit"] = df[config["debit"]].apply(clean_money)
        df["Credit"] = df[config["credit"]].apply(clean_money)
        df["Amount"] = df["Credit"] - df["Debit"]
    
    elif "amount" in config:
        df["Amount"] = pd.to_numeric(
            df[config["amount"]].astype(str).str.replace(",", ""), 
            errors='coerce'
        ).fillna(0)

    df["Clean_Description"] = df["Description"].apply(clean_description)
    df["Description"] = df["Description"].fillna("Unknown")
    df["Clean_Description"] = df["Clean_Description"].fillna("Unknown")
    df = df.dropna(subset=["Date"])

    return df[["Date", "Description", "Clean_Description", "Amount"]]