from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class AgentScore(BaseModel):
    risk_score: int = Field(0, description="Risk score from 0-100")
    reasoning: List[str] = Field(default_factory=list, description="List of reasons for the score")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional agent-specific details")

class AgentBreakdown(BaseModel):
    url_agent: Optional[AgentScore] = None
    domain_agent: Optional[AgentScore] = None
    ssl_agent: Optional[AgentScore] = None
    content_agent: Optional[AgentScore] = None
    threat_agent: Optional[AgentScore] = None
    memory_agent: Optional[AgentScore] = None

class TrustLensResponse(BaseModel):
    url: str
    verdict: str = Field(..., description="Safe | Suspicious | Malicious")
    risk_score: int = Field(..., description="Aggregated risk score 0-100")
    intent: str
    reasoning_trace: List[str]
    why_this_matters: str
    agent_breakdown: AgentBreakdown

class AnalysisRequest(BaseModel):
    url: str
