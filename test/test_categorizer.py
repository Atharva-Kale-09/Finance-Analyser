import pytest
import pandas as pd
from backend.services.categorizer import apply_rules

def test_apply_rules_food():
    """Happy Path: Standard keyword matching."""
    row = {"Description": "ZOMATO order", "Clean_Description": "ZOMATO", "Amount": -450}
    assert apply_rules(row) == "Food"

def test_apply_rules_salary():
    """Happy Path: Income with company keyword."""
    row = {"Description": "ACH CREDIT PAYROLL PVT LTD", "Clean_Description": "PAYROLL", "Amount": 50000}
    assert apply_rules(row) == "Salary"

def test_apply_rules_unknown_short_word():
    """Sad Path: Ensures 'XYZ' is NOT misidentified as a person name (4+ char rule)."""
    row = {"Description": "XYZ STORE", "Clean_Description": "XYZ", "Amount": -100}
    # Should return None so it can be passed to AI
    assert apply_rules(row) is None

def test_apply_rules_valid_name():
    """Happy Path: Verifies that valid names (4+ chars) are caught."""
    row = {"Description": "UPI/KUNAL/PAYMENT", "Clean_Description": "KUNAL", "Amount": -500}
    assert apply_rules(row) == "Transfer-Out"