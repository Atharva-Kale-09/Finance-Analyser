from fastapi.testclient import TestClient
from backend.main import app
import io

client = TestClient(app)

def test_upload_valid_csv():
    """Integration Test: Happy Path for full file processing."""
    # Create a minimal Axis-style CSV
    content = "Tran Date,PARTICULARS,DR,CR\n01-09-2023,ZOMATO,450,0"
    file = io.BytesIO(content.encode("utf-8"))
    
    response = client.post(
        "/upload/",
        files={"file": ("test.csv", file, "text/csv")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["detected_bank"] == "axis"
    assert data["rows"] == 1
    assert "report" in data
    assert "kpis" in data["report"]

def test_upload_malformed_csv():
    """Integration Test: Sad Path for bad file content."""
    content = "Wrong,Headers,Only"
    file = io.BytesIO(content.encode("utf-8"))
    
    response = client.post(
        "/upload/",
        files={"file": ("test.csv", file, "text/csv")}
    )
    
    # Should return a 400 Validation Error because headers don't match any bank
    assert response.status_code == 400
    assert "Unsupported bank format" in response.json()["detail"]