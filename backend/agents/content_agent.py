from .base import BaseAgent
from schemas import AgentScore
import httpx
from bs4 import BeautifulSoup
import os
import asyncio
from google import genai

class ContentIntelligenceAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "content_agent"

    async def _scrape(self, url: str) -> str:
        try:
            if not url.startswith("http"):
                url = "http://" + url
                
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            async with httpx.AsyncClient(timeout=5.0, follow_redirects=True) as client:
                resp = await client.get(url, headers=headers)
                
            soup = BeautifulSoup(resp.content, "html.parser")
            text = soup.get_text(separator=' ', strip=True)
            return text[:2000]
        except Exception as e:
            return f"Scraping failed: {e}"

    async def analyze(self, url: str) -> AgentScore:
        score = 0
        reasons = []
        details = {}

        content = await self._scrape(url)
        details["scraped_length"] = len(content)

        if "Scraping failed" in content:
            return AgentScore(
                risk_score=30,
                reasoning=["Failed to scrape webpage content.", content],
                details=details
            )

        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return AgentScore(
                risk_score=0,
                reasoning=["Gemini API key missing. Skipping content analysis."],
                details=details
            )

        client = genai.Client(api_key=api_key)
        
        prompt = f"""
Analyze the following webpage content from the URL: {url}
Identify if the content shows signs of:
- Fake login forms (asking for passwords unexpectedly)
- Urgency or scam language ("Your account is suspended", "Win an iPhone")
- Malware distribution
- Credential theft

Webpage Text:
{content}

Respond EXACTLY in this format:
RISK_SCORE: [0-100]
INTENT: [Credential theft | Payment scam | Malware | Legitimate | Suspicious]
REASON: [Short 1 sentence reason]
"""
        
        try:
            # Run the blocking Gemini client in a thread with a short timeout,
            # so that network issues do not block the whole request.
            async def _call_llm():
                return await asyncio.to_thread(
                    client.models.generate_content,
                    # Use lighter flash model for faster responses
                    model="gemini-1.5-flash",
                    contents=prompt,
                    config=genai.types.GenerateContentConfig(
                        temperature=0.0
                    ),
                )

            # Keep content analysis fast; if it takes too long we fall back
            # to structural checks only.
            response = await asyncio.wait_for(_call_llm(), timeout=5)
            llm_text = response.text.strip()
            
            import re
            
            score_line = [L for L in llm_text.split('\n') if "RISK_SCORE:" in L]
            intent_line = [L for L in llm_text.split('\n') if "INTENT:" in L]
            reason_line = [L for L in llm_text.split('\n') if "REASON:" in L]
            
            if score_line:
                match = re.search(r'\d+', score_line[0])
                if match:
                    s = int(match.group())
                    score = min(max(s, 0), 100)
            if reason_line:
                # Handle cases where REASON might have colons inside it
                parts = reason_line[0].split(":", 1)
                if len(parts) > 1:
                    reasons.append(parts[1].strip())
            if intent_line:
                parts = intent_line[0].split(":", 1)
                if len(parts) > 1:
                    details["intent"] = parts[1].strip()
            
        except asyncio.TimeoutError:
            reasons.append("Content LLM was too slow; relying only on structural URL and page signals.")
        except Exception:
            reasons.append("Content LLM was unavailable; relying only on structural URL and page signals.")

        return AgentScore(
            risk_score=score,
            reasoning=reasons,
            details=details
        )
