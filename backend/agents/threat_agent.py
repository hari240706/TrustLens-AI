import asyncio
import socket
from urllib.parse import urlparse
from .base import BaseAgent
from schemas import AgentScore

class ThreatIntelligenceAgent(BaseAgent):
    """
    Checks a URL's domain against real-time DNS Blackhole Lists (DNSBLs) such as Spamhaus.
    """
    @property
    def name(self) -> str:
        return "threat_agent"

    def __init__(self):
        # Using a few reliable, free DNSBL providers
        self.dnsbl_providers = [
            "zen.spamhaus.org",
            "b.barracudacentral.org",
            "bl.spamcop.net"
        ]
        
    def _check_dnsbl(self, domain: str) -> tuple[bool, str]:
        """
        Synchronously check a domain against DNSBLs by first resolving to IP,
        then doing a reverse IP lookup on the DNSBL provider.
        """
        try:
            # First, get the IP address of the domain
            ip = socket.gethostbyname(domain)
        except socket.gaierror:
            return False, "Could not resolve domain to IP."

        # Reverse the IP for DNSBL query
        reversed_ip = '.'.join(reversed(ip.split('.')))
        
        for provider in self.dnsbl_providers:
            query = f"{reversed_ip}.{provider}"
            try:
                # If this resolves, the IP is blacklisted by this provider
                socket.gethostbyname(query)
                return True, f"Domain IP ({ip}) is blacklisted by {provider}."
            except socket.gaierror:
                # Not listed by this provider
                continue
                
        return False, "Domain IP not found in tested threat intelligence blacklists."

    async def analyze(self, url: str) -> AgentScore:
        score = 0
        reasons = []
        details = {}

        if not url.startswith(('http://', 'https://')):
            parse_url = 'http://' + url
        else:
            parse_url = url
            
        parsed = urlparse(parse_url)
        domain = parsed.netloc
        if ':' in domain:
            domain = domain.split(':')[0]
            
        if domain.startswith("www."):
            clean_domain = domain[4:]
        else:
            clean_domain = domain

        loop = asyncio.get_running_loop()
        
        # Run the blocking DNS lookups in an executor
        is_malicious, result_msg = await loop.run_in_executor(None, self._check_dnsbl, clean_domain)

        details["dnsbl_query"] = result_msg

        if is_malicious:
            score = 100
            reasons.append(f"Threat detected: {result_msg}")
        else:
            score = 10
            reasons.append("URL not found in threat intelligence feeds (Neutral).")
            
        return AgentScore(
            risk_score=score,
            reasoning=reasons,
            details=details
        )
