from schemas import TrustLensResponse, AgentBreakdown, AgentScore
from agents.url_agent import URLIntelligenceAgent
from agents.domain_agent import DomainIntelligenceAgent
from agents.ssl_agent import SSLCertificateAgent
from agents.threat_agent import ThreatIntelligenceAgent
from agents.memory_agent import MemoryAgent
from agents.content_agent import ContentIntelligenceAgent
from agents.explainability_agent import ExplainabilityAgent
import asyncio

class OrchestratorAgent:
    def __init__(self):
        # Initialize sub-agents
        self.url_agent = URLIntelligenceAgent()
        self.domain_agent = DomainIntelligenceAgent()
        self.ssl_agent = SSLCertificateAgent()
        self.threat_agent = ThreatIntelligenceAgent()
        self.memory_agent = MemoryAgent()
        self.content_agent = ContentIntelligenceAgent()
        self.explainability_agent = ExplainabilityAgent()

    async def _run_agent_safe(self, coro, name: str) -> AgentScore:
        """
        Run a single agent with a timeout and error handling so that
        one slow or failing agent cannot block the whole analysis.
        """
        try:
            return await asyncio.wait_for(coro, timeout=10)
        except Exception as e:
            return AgentScore(
                risk_score=0,
                reasoning=[f"{name} failed: {str(e)}"],
                details={}
            )
        
    async def analyze_url(self, url: str) -> TrustLensResponse:
        """
        Dynamically execute agents. Some can run in parallel for speed.
        """
        
        # We can run these in parallel as they don't depend on each other initially.
        # Each agent is wrapped with _run_agent_safe so a single failure/timeout
        # does not prevent a response from being returned.
        results = await asyncio.gather(
            self._run_agent_safe(self.url_agent.analyze(url), "url_agent"),
            self._run_agent_safe(self.domain_agent.analyze(url), "domain_agent"),
            self._run_agent_safe(self.ssl_agent.analyze(url), "ssl_agent"),
            self._run_agent_safe(self.threat_agent.analyze(url), "threat_agent"),
            self._run_agent_safe(self.memory_agent.analyze(url), "memory_agent"),
            self._run_agent_safe(self.content_agent.analyze(url), "content_agent"),
        )
        
        url_res, dom_res, ssl_res, thr_res, mem_res, cnt_res = results
        
        # Base weight distribution
        weights = {
            "url": 0.15,
            "domain": 0.15,
            "ssl": 0.20,
            "threat": 0.25,
            "memory": 0.05,
            "content": 0.20
        }
        
        # If Threat Intelligence explicitly flags it, it overrides everything
        if thr_res.risk_score >= 90:
            raw_score = 100
            final_score = 100
            verdict = "Malicious"
            
        # If SSL is missing and domain is super new, that's incredibly suspicious
        elif ssl_res.risk_score > 50 and dom_res.risk_score > 40:
            raw_score = 85
            final_score = 85
            verdict = "Malicious"
            
        else:
            # Otherwise, use the weighted combination matrix
            raw_score = (
                url_res.risk_score * weights["url"] + 
                dom_res.risk_score * weights["domain"] + 
                ssl_res.risk_score * weights["ssl"] + 
                thr_res.risk_score * weights["threat"] + 
                mem_res.risk_score * weights["memory"] + 
                cnt_res.risk_score * weights["content"]
            )
            
            # Ensure it never drops below 0 or goes above 100
            final_score = min(max(int(raw_score), 0), 100)
            verdict = "Safe"
            if final_score >= 65:
                verdict = "Malicious"
            elif final_score >= 35:
                verdict = "Suspicious"
            
        # Update Memory Agent cache
        self.memory_agent.add_record(url, final_score)
        
        # Compile breakdown
        breakdown_dict = {
            "url_agent": url_res.model_dump(),
            "domain_agent": dom_res.model_dump(),
            "ssl_agent": ssl_res.model_dump(),
            "threat_agent": thr_res.model_dump(),
            "memory_agent": mem_res.model_dump(),
            "content_agent": cnt_res.model_dump()
        }
        
        # Explainability Generation
        explanation = await self.explainability_agent.generate_explanation(
            url=url,
            verdict=verdict,
            final_score=final_score,
            agent_traces=[], # Handled via breakdown_dict in explainability
            agent_breakdowns=breakdown_dict
        )
        
        breakdown = AgentBreakdown(
            url_agent=url_res,
            domain_agent=dom_res,
            ssl_agent=ssl_res,
            threat_agent=thr_res,
            memory_agent=mem_res,
            content_agent=cnt_res
        )
        
        predicted_intent = cnt_res.details.get("intent", "Legitimate" if verdict == "Safe" else "Unknown")
        
        return TrustLensResponse(
            url=url,
            verdict=verdict,
            risk_score=final_score,
            intent=predicted_intent,
            reasoning_trace=explanation["reasoning_trace"],
            why_this_matters=explanation["why_this_matters"],
            agent_breakdown=breakdown
        )
