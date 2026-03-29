import os
from google import genai
import json


class ExplainabilityAgent:
    """
    Takes the raw outputs from all other agents and the Orchestrator's final verdict,
    and uses an LLM to generate a clean, simple explanation and "Why this matters".
    Falls back to a deterministic, local explanation if the LLM is unavailable or slow.
    """

    def _fallback_explanation(self, url: str, verdict: str, final_score: int, agent_breakdowns: dict) -> dict:
        """
        Build a clear explanation directly from agent scores/reasons without calling the LLM.
        This ensures we always have a good explanation even if Gemini is unreachable.
        """
        reasoning_trace = [f"Final verdict for {url}: {verdict} with risk score {final_score}/100."]

        for agent_key, data in agent_breakdowns.items():
            if not data:
                continue
            # agent_key like "url_agent" -> "URL"
            name = agent_key.replace("_agent", "").upper()
            score = data.get("risk_score", 0)
            reasons = data.get("reasoning", [])
            if reasons:
                reasoning_trace.append(f"{name} score {score}/100: {reasons[0]}")
            else:
                reasoning_trace.append(f"{name} score {score}/100: no detailed reasons available.")

        if verdict == "Malicious":
            why = (
                "This website shows multiple high‑risk signals across the agents, "
                "so it is treated as malicious and should not be trusted with any sensitive information."
            )
        elif verdict == "Suspicious":
            why = (
                "Some agents detected warning signs; while not conclusively malicious, "
                "this site should be treated with caution and avoided for logins or payments."
            )
        else:
            why = (
                "The combined signals from all agents do not show strong evidence of phishing or malware, "
                "so the site is considered generally safe under normal use."
            )

        return {
            "reasoning_trace": reasoning_trace,
            "why_this_matters": why,
        }

    async def generate_explanation(self, url: str, verdict: str, final_score: int, agent_traces: list, agent_breakdowns: dict) -> dict:
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            # No key configured – always fall back to deterministic explanation.
            return self._fallback_explanation(url, verdict, final_score, agent_breakdowns)

        client = genai.Client(api_key=api_key)
        
        prompt = f"""
You are the Explainability Agent for TrustLens Cybersecurity System.
A user analyzed the URL: {url}
The final verdict is: {verdict}
The final risk score is: {final_score}/100

Here are the raw agent reports:
{json.dumps(agent_breakdowns, indent=2)}

Task:
1. Create a step-by-step reasoning trace suitable for an end-user. Each step should be actionable and clear.
2. Provide a "Why this matters" single paragraph explaining the risk or safety of the URL in simple terms.

Format your output EXACTLY as this JSON structure:
{{
  "reasoning_trace": [
    "Step 1: Analyzed URL length - unusually long.",
    "Step 2: Checked SSL - valid certificate found."
  ],
  "why_this_matters": "This site uses an invalid certificate and requests a login, indicating a strong likelihood of credential theft."
}}
"""
        
        try:
            # We use the standard gemini-1.5-flash model, running it in a thread since it is synchronous locally.
            import asyncio

            async def _call_llm():
                return await asyncio.to_thread(
                    client.models.generate_content,
                    # Use the lighter flash model for faster responses
                    model="gemini-1.5-flash",
                    contents=prompt,
                    config=genai.types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.3,
                    ),
                )

            # Time-box explainability so it cannot hang the whole request.
            # Short timeout to keep responses snappy; on timeout we fall back to local explanation.
            response = await asyncio.wait_for(_call_llm(), timeout=5)
            
            result = json.loads(response.text)
            return {
                "reasoning_trace": result.get("reasoning_trace", []),
                "why_this_matters": result.get("why_this_matters", "No explanation provided.")
            }
        except Exception:
            # Any timeout or LLM error: use deterministic local explanation instead of exposing errors to the user.
            return self._fallback_explanation(url, verdict, final_score, agent_breakdowns)
