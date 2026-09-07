# 💰 Finance Analyzer

A decoupled, full-stack application designed to automate the normalization and categorization of messy bank statements using a hybrid Rule-Engine and AI approach.

## 🏛 Architecture
This project follows a **Service-Oriented Architecture (SOA)**:
- **Backend (FastAPI):** Orchestrates the data pipeline (Normalization -> Categorization -> Analysis).
- **Services Layer:** Modular logic for parsing bank-specific formats and calculating financial KPIs.
- **Frontend (Streamlit):** A thin client focused purely on data visualization and user experience.
- **AI Integration:** Leveraging Google Gemini (Flash-Lite) for non-deterministic transaction classification.

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- A Google Gemini API Key

### 2. Environment Setup
Clone the repository and create a virtual environment:
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

### 3. Configuration
Create a .env file in the project root to securely manage secrets:
GENAI_API_KEY=your_api_key_here

### 4. Running the Application
The application requires two concurrent processes:
Terminal 1: Backend (Uvicorn)
uvicorn backend.main:app --reload

Terminal 2: Frontend (Streamlit)
streamlit run frontend/app.py

