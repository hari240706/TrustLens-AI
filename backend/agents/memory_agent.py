from .base import BaseAgent
from schemas import AgentScore
from urllib.parse import urlparse

class MemoryAgent(BaseAgent):
    """
    Stores history of analyzed URLs to detect repeated patterns.
    """
    def __init__(self):
        self.history = {} # url -> risk_score

    @property
    def name(self) -> str:
        return "memory_agent"

    async def analyze(self, url: str) -> AgentScore:
        score = 0
        reasons = []
        details = {}
        
        parsed = urlparse(url)
        domain = parsed.netloc if parsed.netloc else url
        
        if domain in self.history:
            prev_score = self.history[domain]
            reasons.append(f"Domain previously analyzed with a score of {prev_score}.")
            if prev_score > 50:
                score += (prev_score // 2) # Add partial penalty for repeat offender
                reasons.append("Historically risky domain.")
            details["previous_score"] = prev_score
        else:
            reasons.append("First time seeing this domain.")
            
        return AgentScore(
            risk_score=score,
            reasoning=reasons,
            details=details
        )
        
    def add_record(self, url: str, final_score: int):
        parsed = urlparse(url)
        domain = parsed.netloc if parsed.netloc else url
        self.history[domain] = final_score
