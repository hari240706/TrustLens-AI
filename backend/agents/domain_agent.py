from .base import BaseAgent
from schemas import AgentScore
import whois
from urllib.parse import urlparse
from datetime import datetime
import asyncio

class DomainIntelligenceAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "domain_agent"

    def _get_whois(self, domain: str):
        try:
            return whois.whois(domain)
        except Exception:
            return None

    async def analyze(self, url: str) -> AgentScore:
        score = 0
        reasons = []
        details = {}
        
        # Ensure it has a scheme for proper parsing
        if not url.startswith(('http://', 'https://')):
            parse_url = 'http://' + url
        else:
            parse_url = url
            
        parsed = urlparse(parse_url)
        domain = parsed.netloc if parsed.netloc else url
        if ':' in domain:
            domain = domain.split(':')[0]
            
        if not domain:
            return AgentScore(risk_score=0, reasoning=["Could not parse domain."], details={})

        loop = asyncio.get_running_loop()
        w = await loop.run_in_executor(None, self._get_whois, domain)
        
        if not w:
            return AgentScore(
                risk_score=10, 
                reasoning=["Failed to retrieve WHOIS data. Domain might be a ccTLD or privacy-protected."], 
                details={"domain": domain}
            )
            
        creation_date = w.creation_date
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
            
        # Handle cases where WHOIS returns a string instead of a datetime
        if isinstance(creation_date, str):
            try:
                creation_date = datetime.strptime(creation_date, "%Y-%m-%d")
            except ValueError:
                creation_date = None

        if creation_date and isinstance(creation_date, datetime):
            if hasattr(creation_date, 'tzinfo') and creation_date.tzinfo is not None:
                creation_date = creation_date.replace(tzinfo=None)
            age_days = (datetime.now() - creation_date).days
            details["age_days"] = age_days
            if age_days < 30:
                score += 50
                reasons.append(f"Domain is very new (created {age_days} days ago).")
            elif age_days < 180:
                score += 20
                reasons.append(f"Domain is relatively new (created {age_days} days ago).")
            else:
                reasons.append(f"Domain is established ({age_days} days old).")
        else:
            score += 15
            reasons.append("Domain creation date is hidden or unparseable.")

        score = min(max(score, 0), 100)
        
        return AgentScore(
            risk_score=score,
            reasoning=reasons,
            details=details
        )
