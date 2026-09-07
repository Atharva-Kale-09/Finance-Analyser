# ---------------------------------------------------------
# CSV COLUMN MAPPINGS
# ---------------------------------------------------------

BANK_CONFIGS = {
    "axis": {
        "date": "Tran Date",
        "description": "PARTICULARS",
        "debit": "DR",
        "credit": "CR"
    },
    "boi": {
        "date": "Date",
        "description": "Remarks",
        "debit": "Debit",
        "credit": "Credit"
    },
    "generic": {
        "date": "Date",
        "description": "Description",
        "amount": "Amount"
    }
}

# ---------------------------------------------------------
# CLEANUP CONFIGURATIONS
# ---------------------------------------------------------

# Prefixes that clutter descriptions but add no value to classification.
# Note: "ATM" and "POS" are intentionally excluded as they are useful signals.
TRANSACTION_PREFIXES = [
    "UPI/", "IMPS/", "NEFT/", "RTGS/", "MBK/", "INF/", 
    "MMT/", "BIL/", "TPT/", "ECOM/"
]

# Common bank codes/identifiers to remove if they appear as standalone words.
COMMON_BANK_CODES = [
    "HDFC", "ICIC", "SBIN", "UTIB", "CNRB", "KKBK", 
    "PYTM", "OKICICI", "OKAXIS", "OKHDFC", "YBL", "AXIS", "UBIN"
]