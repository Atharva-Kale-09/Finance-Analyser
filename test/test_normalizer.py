import pytest
import pandas as pd
from backend.services.normalizer import detect_bank, clean_description

def test_detect_bank_axis():
    """Happy Path: Detects Axis bank columns."""
    df = pd.DataFrame(columns=["Tran Date", "PARTICULARS", "DR", "CR"])
    assert detect_bank(df) == "axis"

def test_detect_bank_unsupported():
    """Sad Path: Raises error for unknown column headers."""
    df = pd.DataFrame(columns=["Unknown", "Column"])
    with pytest.raises(ValueError, match="Unsupported bank format"):
        detect_bank(df)

def test_clean_description_logic():
    """Happy Path: Verifies removal of bank artifacts like 'UPI/'."""
    raw = "UPI/12345/ZOMATO/BANGALORE"
    cleaned = clean_description(raw)
    assert "UPI/" not in cleaned
    assert "ZOMATO" in cleaned