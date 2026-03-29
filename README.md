# TrustLens: Multi-Agent AI System for Detecting Malicious Websites

TrustLens is a production-ready AI-powered cybersecurity system that analyzes a given URL and determines whether it is Safe, Suspicious, or Malicious using a robust multi-agent architecture with explainable reasoning.

## 🌟 Features
- **Orchestrator Agent**: Dynamically determines which underlying agents to execute, handles conflict resolution, and aggregates a final risk score (0-100).
- **URL Intelligence Agent**: Analyzes string-level features (length, formatting, suspicious characters) locally without making requests.
- **Domain Intelligence Agent**: Uses WHOIS lookups to verify domain age, registration history, and detect fresh domains often used in phishing.
- **SSL Certificate Agent**: Validates SSL/TLS certificates by initiating a secure socket connection to confirm validity.
- **Content & Intent Agent**: Scrapes webpage contents and uses an LLM (OpenAI) to detect deceptive intent, urgency (e.g. "Account suspended"), or credential theft.
- **Memory Agent**: Retains historical execution traces to detect repeated offending domains.
- **Threat Intelligence Agent**: Checks against a built-in mock database of known safe and malicious sites.
- **Explainability Agent**: Correlates the output of all underlying agents and translates them into a simple, human-readable logic trace and summary.

## 🛠️ Architecture
- **Backend**: FastAPI (Python) for asynchronous agent execution and orchestration.
- **Frontend**: React (Vite) with a bespoke sleek dark-mode glassmorphism design.
- **LLM**: OpenAI `gpt-4o-mini` for intent classification and explainability.

## 🚀 Getting Started

### 1. Backend Setup

Prerequisites: Python 3.9+
1. Navigate to the `backend` folder:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install fastapi uvicorn pydantic python-whois beautifulsoup4 requests openai python-dotenv
   ```
4. Configure OpenAI:
   Open the `.env` file in the `backend` folder and add your API key:
   ```env
   OPENAI_API_KEY=your_real_api_key_here
   ```
5. Run the API server:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

### 2. Frontend Setup

Prerequisites: Node.js 18+
1. Navigate to the `frontend` folder:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```

## 🎯 Usage
1. Open the frontend URL (usually `http://localhost:5173`).
2. Enter a URL (e.g., `google.com` or `evil-phishing-site.com`).
3. Watch the multi-agent system analyze the site in real-time.
4. Review the final verdict, risk score, logic trace, and detailed individual agent breakdown.
