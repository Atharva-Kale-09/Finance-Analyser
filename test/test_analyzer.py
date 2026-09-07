import pytest
import pandas as pd
from backend.services.analyzer import generate_report

def test_analyzer_math_accuracy():
    """Happy Path: Verifies basic financial math logic."""
    data = [
        {"Date": "2023-01-01", "Amount": 1000.0, "Category": "Salary"}, # Income
        {"Date": "2023-01-02", "Amount": -200.0, "Category": "Food"},   # Expense
        {"Date": "2023-01-03", "Amount": -300.0, "Category": "Other"}  # Expense
    ]
    df = pd.DataFrame(data)
    df["Date"] = pd.to_datetime(df["Date"])
    
    report = generate_report(df)
    
    assert report["kpis"]["income"] == 1000.0
    assert report["kpis"]["expense"] == 500.0
    assert report["kpis"]["net_cashflow"] == 500.0
    assert report["kpis"]["savings_rate"] == 50.0

def test_analyzer_no_income():
    """Sad Path: Ensures no division by zero when income is 0."""
    data = [{"Date": "2023-01-01", "Amount": -100.0, "Category": "Food"}]
    df = pd.DataFrame(data)
    df["Date"] = pd.to_datetime(df["Date"])
    
    report = generate_report(df)
    assert report["kpis"]["savings_rate"] == 0.0

def test_analyzer_empty_dataframe():
    """Sad Path: Verifies robustness when no data is provided."""
    df = pd.DataFrame(columns=["Date", "Amount", "Category"])
    report = generate_report(df)
    
    assert "kpis" in report
    assert report["kpis"]["income"] == 0.0
    assert report["insights"]["total_transactions"] == 0