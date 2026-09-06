"""Dual-mode LLM client: Google Gemini API + built-in Semantic Reasoning Engine."""
from __future__ import annotations
import os
import json
import logging
from typing import Dict, Any, List, Optional
import requests

logger = logging.getLogger(__name__)


class LLMClient:
    """Client for generating intelligent natural language responses."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.5-flash"):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.model = model

    def query_gemini(self, prompt: str, system_instruction: str) -> Optional[str]:
        """Calls Google Gemini REST API if an API key is available."""
        if not self.api_key:
            return None

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}]
                }
            ],
            "systemInstruction": {
                "parts": [{"text": system_instruction}]
            },
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 2048,
            }
        }

        try:
            resp = requests.post(url, json=payload, timeout=20)
            if resp.status_code == 200:
                data = resp.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return parts[0].get("text", "")
            logger.warning(f"Gemini API returned status {resp.status_code}: {resp.text}")
            return None
        except Exception as e:
            logger.warning(f"Failed to query Gemini API: {e}. Falling back to internal engine.")
            return None
