from .base import BaseAgent
from schemas import AgentScore
import re
from urllib.parse import urlparse

class URLIntelligenceAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "url_agent"

    async def analyze(self, url: str) -> AgentScore:
        score = 0
        reasons = []
        
        # Ensure it has a scheme for proper parsing
        if not url.startswith(('http://', 'https://')):
            parse_url = 'http://' + url
        else:
            parse_url = url
            
        parsed = urlparse(parse_url)
        domain = parsed.netloc if parsed.netloc else url
        if ':' in domain:
            domain = domain.split(':')[0]
            
        path = parsed.path
        query = parsed.query

        # 1. Length check (Tiered penalties)
        total_len = len(url)
        if total_len > 100:
            score += 30
            reasons.append(f"URL is excessively long ({total_len} characters).")
        elif total_len > 75:
            score += 15
            reasons.append(f"URL is unusually long ({total_len} characters).")
        
        # 2. Suspicious elements
        suspicious_chars = {'@': 30, '-': 5, '_': 5}
        for char, penalty in suspicious_chars.items():
            if url.count(char) > 2:
                score += penalty
                reasons.append(f"URL contains multiple suspicious characters ({char}).")
                
        if "//" in path:
            score += 30
            reasons.append("Path contains multiple slashes (potential open redirect/obfuscation).")

        # 3. IP Address instead of domain
        if re.match(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$", domain):
            score += 60
            reasons.append("URL uses an IP address instead of a domain name.")
            
        # 4. Suspicious TLDs
        suspicious_tlds = {'.xyz', '.top', '.pw', '.cc', '.club', '.tk', '.ml'}
        if any(domain.endswith(tld) for tld in suspicious_tlds):
            score += 30
            reasons.append("Domain uses a TLD commonly associated with spam/phishing.")

        # 5. Suspicious Keywords in Path/Query
        keywords = {'login', 'verify', 'update', 'secure', 'account', 'banking', 'billing', 'confirm'}
        url_lower = url.lower()
        found_keywords = [kw for kw in keywords if kw in url_lower and kw not in domain]
        if found_keywords:
            score += 35
            reasons.append(f"URL contains deceptive keywords in path/query ({', '.join(found_keywords)}).")

        score = min(max(score, 0), 100)
        
        return AgentScore(
            risk_score=score,
            reasoning=reasons,
            details={"length": len(url), "domain": domain}
        )
