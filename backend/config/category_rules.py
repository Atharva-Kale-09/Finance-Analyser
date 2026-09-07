import re

# ---------------------------------------------------------
# CATEGORY DEFINITIONS
# ---------------------------------------------------------

TRANSACTION_CATEGORIES = [
    "Food", "Travel", "Transport", "Utilities",
    "Rent", "Shopping", "Healthcare", "Salary",
    "Investment", "Entertainment",
    "Withdrawal",
    "Transfer-In",
    "Transfer-Out",
    "Bank Charges",
    "Other"
]

# ---------------------------------------------------------
# RULE ENGINE CONFIGURATIONS
# ---------------------------------------------------------

# 1. Simple Keyword Matching
KEYWORD_RULES = {
    "Food": [
        "swiggy", "zomato", "mcdona", "kfc", "domino", "pizza", 
        "burger", "subway", "starbucks", "cafe", "restaurant",
        "tea", "coffee", "mcdonald"
    ],
    "Transport": [
        "bmtc", "ksrtc", "uber", "ola", "rapido", "chalo", 
        "metro", "rail", "irctc", "toll", "fastag"
    ],
    "Travel": [
        "indigo", "air india", "vistara", "akasa", "spicejet", 
        "makemytrip", "easemytrip", "hotel", "airbnb", "booking.com",
        "redbus", "irctc", "railway", "train", "bus booking"
    ],
    "Shopping": [
        "amazon", "flipkart", "myntra", "ajio", "decathlon", 
        "ikea", "zudio", "reliance", "mart", "mall", "ecom"
    ],
    "Investment": [
        "zerodha", "groww", "kuvera", "sip", "mutual fund", "ppf"
    ],
    "Withdrawal": [
        "atm", "cash", "withdrawal", "nfs"
    ]
}

# 2. Regex Patterns
REGEX_RULES = {
    "Transport": [
        r"ka\d{2}[a-z]",       # Matches KA01 (Bus numbers)
        r"ka\s?\d{2}\s?[a-z]"
    ],
    "Salary": [
        r"salary", 
        r"ach credit",
        r"payroll"
    ]
}

# 3. Merchant Aliases (Fuzzy Matching)
MERCHANT_ALIASES = {
    "Travel": ["goibibo", "goibib", "ibibo", "cleartrip", "cleart"],
    "Food": ["district", "digihaat", "sai foods", "saifoods"],
    "Shopping": ["zepto", "coolz", "cool z"],
    "Healthcare": ["dalvko", "dalvkot"],
    "Transport": ["indian rail", "railway", "indian"]
}

# 4. Blockwords (Prevent misclassification as P2P Transfer)
MERCHANT_BLOCKWORDS = [
    "google", "gpay",
    "recharge", "electricity", "bill",
    "broadband", "insurance"
]

# ---------------------------------------------------------
# HELPER LISTS
# ---------------------------------------------------------

# Words indicating a corporate entity (Used for Salary/Income detection)
COMPANY_KEYWORDS = [
    "pvt", "ltd", "llp", "private", "limited",
    "technologies", "tech", "solutions",
    "systems", "software", "infotech"
]

# Words that look like names but are actually businesses
GENERIC_BUSINESS_WORDS = [
    "store", "mart", "hotel", "restaurant",
    "services", "solutions", "tech", "technologies",
    "enterprises", "traders"
]

# ---------------------------------------------------------
# FINANCIAL HEALTH GROUPINGS (Used in Frontend/Analytics)
# ---------------------------------------------------------

CATEGORY_GROUPS = {
    "Essential": ["Food", "Utilities", "Rent", "Healthcare", "Transport"],
    "Lifestyle": ["Shopping", "Entertainment", "Travel"],
    "Investment": ["Investment"],
    "Leakage": ["Bank Charges", "Withdrawal"]
}