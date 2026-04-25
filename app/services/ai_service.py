from google import genai
from app.config import settings
import json
import re

client = genai.Client(api_key=settings.GEMINI_API_KEY)

system_prompt = """
You are a senior penetration tester analyzing reconnaissance scan results.
Respond ONLY in this exact JSON format with no extra text or markdown:

{
    "threat_narrative": "3-5 sentence human readable attack surface summary",
    "risk_score": 0,
    "risk_level": "Critical/High/Medium/Low",
    "key_findings": [
        {"severity": "High", "finding": "description here"},
        {"severity": "Medium", "finding": "description here"},
        {"severity": "Low", "finding": "description here"}
    ]
}
"""

def generate_ai_summery(nmap_output: str, harvester_output: str, subfinder_output: str) -> dict:

    prompt = f"""
    {system_prompt}

    === NMAP OUTPUT ===
    {nmap_output or "No nmap data available"}

    === THEHARVESTER OUTPUT ===
    {harvester_output or "No theHarvester data available"}

    === SUBFINDER OUTPUT ===
    {subfinder_output or "No subfinder data available"}
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    raw = response.text
    # strip markdown code blocks if Gemini wraps in ```json
    raw = re.sub(r'```json|```', '', raw).strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            return json.loads(match.group())
        return {"error": "Failed to parse AI response"}



