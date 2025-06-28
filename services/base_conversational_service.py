

import time
import requests
import json
import logging
from typing import Dict, List, Any

from config import GEMINI_API_KEY
from mongodb import db
from services.store_service import get_active_store

logger = logging.getLogger(__name__)

class BaseConversationalService:
    def __init__(self, model_name="gemini-1.5-flash"):
        self.api_key = GEMINI_API_KEY
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={self.api_key}"
        self.headers = {"Content-Type": "application/json"}

    def _call_llm(self, prompt: str, messages: List[Dict] = None) -> str:
        """Call the Gemini API"""
        try:
            if not self.api_key or self.api_key.startswith("your-"):
                return "I'm sorry, but I'm not properly configured to help with orders right now. Please contact our support team."

            if messages:
                full_prompt = ""
                for msg in messages:
                    role = msg.get("role")
                    content = msg.get("content", "")
                    if role == "system":
                        full_prompt += f"{content}\n\n"
                    elif role == "user":
                        full_prompt += f"User: {content}\n"
                    elif role == "assistant":
                        full_prompt += f"Assistant: {content}\n"
                if prompt:
                    full_prompt += f"User: {prompt}\nAssistant:"
                else:
                    full_prompt += "Assistant:"
            else:
                full_prompt = prompt

            data = {
                "contents": [{"parts": [{"text": full_prompt}]}],
                "generationConfig": {"maxOutputTokens": 500, "temperature": 0.7},
            }

            response = requests.post(self.api_url, headers=self.headers, json=data, timeout=30)

            if response.status_code == 429:
                logger.warning("Rate limit hit. Waiting 5 seconds...")
                time.sleep(5)
                return self._call_llm(prompt, messages)

            response.raise_for_status()
            result = response.json()

            if "candidates" in result and len(result["candidates"]) > 0:
                return result["candidates"][0]["content"]["parts"][0]["text"]
            else:
                return "I'm sorry, I couldn't generate a response at the moment."

        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")
            return "I'm sorry, I'm having trouble processing your request right now. Please try again in a moment."

    def _get_product_context(self) -> str:
        raise NotImplementedError

    def _create_system_prompt(self, user_name: str) -> str:
        raise NotImplementedError

    def _get_welcome_message(self, user_name: str) -> str:
        raise NotImplementedError

    def process_message(self, user_id: int, message: str, conversation_history: List[Dict]) -> Dict[str, Any]:
        raise NotImplementedError

