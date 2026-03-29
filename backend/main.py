from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from schemas import AnalysisRequest, TrustLensResponse
from agents.orchestrator import OrchestratorAgent
import traceback

app = FastAPI(title="TrustLens API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize a global Orchestrator to persist MemoryAgent states
orchestrator = OrchestratorAgent()

@app.get("/")
def root():
    return {"message": "TrustLens API is running"}

@app.post("/api/analyze", response_model=TrustLensResponse)
async def analyze_domain(request: AnalysisRequest):
    try:
        url = request.url.strip()
        if not url:
            raise HTTPException(status_code=400, detail="URL cannot be empty")
            
        print(f"Starting analysis for: {url}")
        response = await orchestrator.analyze_url(url)
        return response
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
