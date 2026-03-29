from .base import BaseAgent
from schemas import AgentScore
import ssl
import socket
from urllib.parse import urlparse
import asyncio

class SSLCertificateAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "ssl_agent"

    async def _check_ssl(self, hostname: str):
        context = ssl.create_default_context()
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(hostname, 443, ssl=context),
                timeout=5.0
            )
            cert = writer.get_extra_info('peercert')
            writer.close()
            await writer.wait_closed()
            return {"valid": True, "cert": cert}
        except Exception as e:
            return {"valid": False, "error": str(e)}

    async def analyze(self, url: str) -> AgentScore:
        score = 0
        reasons = []
        details = {}

        # Ensure it has a scheme for proper parsing
        if not url.startswith(('http://', 'https://')):
            parse_url = 'https://' + url
        else:
            parse_url = url
            
        parsed = urlparse(parse_url)
        scheme = parsed.scheme or "https"
        domain = parsed.netloc if parsed.netloc else url
        if ':' in domain:
            domain = domain.split(':')[0]
            
        if scheme == "http":
            score += 60
            reasons.append("Connection uses unencrypted HTTP.")
            return AgentScore(risk_score=score, reasoning=reasons, details={"scheme": "http"})
            
        ssl_result = await self._check_ssl(domain)
        
        if not ssl_result["valid"]:
            score += 80
            reasons.append(f"Invalid or missing SSL certificate ({ssl_result.get('error', 'unknown error')}).")
            details["ssl_error"] = ssl_result.get("error")
        else:
            reasons.append("Valid SSL certificate found.")
            cert = ssl_result["cert"]
            issuer = dict(x[0] for x in cert.get('issuer', []))
            issuer_org = issuer.get('organizationName', 'Unknown')
            details["issuer"] = issuer_org
            
            # Penalize Let's Encrypt for certain known risky combinations?
            # Normally LE is fine, but combined with new domains it's a signal. We'll let orchestrator handle combinations, or just flag it as neutral.

        score = min(score, 100)
        
        return AgentScore(
            risk_score=score,
            reasoning=reasons,
            details=details
        )
