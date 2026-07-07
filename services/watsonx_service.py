"""
services/watsonx_service.py — IBM watsonx.ai API integration
Handles all communication with IBM Granite models.
"""

import os
import json
import requests
from config import WATSONX_CONFIG
import logging

logger = logging.getLogger(__name__)


class WatsonxService:
    """
    Service class for IBM watsonx.ai API.
    Manages authentication tokens and model inference requests.
    """

    IAM_TOKEN_URL = "https://iam.cloud.ibm.com/identity/token"

    def __init__(self):
        self.api_key = WATSONX_CONFIG["api_key"]
        self.project_id = WATSONX_CONFIG["project_id"]
        self.url = WATSONX_CONFIG["url"]
        self.model_id = WATSONX_CONFIG["model_id"]
        self.parameters = WATSONX_CONFIG["parameters"]
        self._access_token = None
        self._token_expiry = 0

    # ----------------------------------------------------------
    # Authentication
    # ----------------------------------------------------------
    def _get_access_token(self) -> str:
        """Obtain IBM Cloud IAM access token using API key."""
        import time
        if self._access_token and time.time() < self._token_expiry:
            return self._access_token

        try:
            response = requests.post(
                self.IAM_TOKEN_URL,
                data={
                    "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
                    "apikey": self.api_key,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30,
            )
            response.raise_for_status()
            token_data = response.json()
            self._access_token = token_data["access_token"]
            self._token_expiry = time.time() + token_data.get("expires_in", 3600) - 60
            return self._access_token
        except Exception as e:
            logger.error(f"Failed to get IBM IAM token: {e}")
            raise ConnectionError(f"IBM Authentication failed: {e}")

    # ----------------------------------------------------------
    # Core Generation Method
    # ----------------------------------------------------------
    def generate(self, prompt: str, system_prompt: str = "", max_tokens: int = None) -> str:
        """
        Send a prompt to IBM Granite model and return the response.

        Args:
            prompt: The user/content prompt
            system_prompt: Optional system instruction
            max_tokens: Override default max tokens

        Returns:
            Generated text string
        """
        if not self.api_key or not self.project_id:
            return self._demo_response(prompt)

        try:
            token = self._get_access_token()
            endpoint = f"{self.url}/ml/v1/text/generation?version=2023-05-29"

            full_prompt = self._build_prompt(system_prompt, prompt)
            params = dict(self.parameters)
            if max_tokens:
                params["max_new_tokens"] = max_tokens

            payload = {
                "model_id": self.model_id,
                "input": full_prompt,
                "parameters": params,
                "project_id": self.project_id,
            }

            response = requests.post(
                endpoint,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=60,
            )
            response.raise_for_status()
            result = response.json()
            generated = result.get("results", [{}])[0].get("generated_text", "")
            return generated.strip()

        except Exception as e:
            logger.error(f"watsonx generation error: {e}")
            return self._demo_response(prompt)

    def _build_prompt(self, system_prompt: str, user_prompt: str) -> str:
        """Build a structured prompt for Granite Instruct models."""
        if system_prompt:
            return (
                f"<|system|>\n{system_prompt}\n"
                f"<|user|>\n{user_prompt}\n"
                f"<|assistant|>\n"
            )
        return f"<|user|>\n{user_prompt}\n<|assistant|>\n"

    # ----------------------------------------------------------
    # Chat (multi-turn)
    # ----------------------------------------------------------
    def chat(self, messages: list, system_prompt: str = "") -> str:
        """
        Multi-turn chat with conversation history.

        Args:
            messages: List of {"role": "user"/"assistant", "content": "..."}
            system_prompt: System instruction

        Returns:
            Assistant response string
        """
        prompt_parts = []
        if system_prompt:
            prompt_parts.append(f"<|system|>\n{system_prompt}\n")

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            tag = "<|user|>" if role == "user" else "<|assistant|>"
            prompt_parts.append(f"{tag}\n{content}\n")

        prompt_parts.append("<|assistant|>\n")
        full_prompt = "".join(prompt_parts)

        if not self.api_key or not self.project_id:
            return self._demo_chat_response(messages[-1]["content"] if messages else "")

        try:
            token = self._get_access_token()
            endpoint = f"{self.url}/ml/v1/text/generation?version=2023-05-29"
            payload = {
                "model_id": self.model_id,
                "input": full_prompt,
                "parameters": self.parameters,
                "project_id": self.project_id,
            }
            response = requests.post(
                endpoint,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=60,
            )
            response.raise_for_status()
            result = response.json()
            return result.get("results", [{}])[0].get("generated_text", "").strip()
        except Exception as e:
            logger.error(f"watsonx chat error: {e}")
            return self._demo_chat_response(messages[-1]["content"] if messages else "")

    # ----------------------------------------------------------
    # Demo mode (when API keys not configured)
    # ----------------------------------------------------------
    def _demo_response(self, prompt: str) -> str:
        """Return a structured demo response when API is not configured."""
        return (
            "⚠️ **Demo Mode** — IBM watsonx.ai credentials not configured.\n\n"
            "**To enable AI features:**\n"
            "1. Copy `.env.example` to `.env`\n"
            "2. Add your IBM Cloud API Key and Project ID\n"
            "3. Restart the application\n\n"
            "**For now, displaying sample AI analysis:**\n\n"
            "📊 **Health Assessment Summary**\n"
            "Based on the provided health metrics, here is a comprehensive analysis:\n\n"
            "• **Blood Pressure**: Slightly elevated — monitor closely and reduce sodium intake\n"
            "• **Blood Glucose**: Above target range — consider reviewing meal timing\n"
            "• **Heart Rate**: Within normal range — continue current activity level\n"
            "• **Oxygen Saturation**: Normal — good respiratory function\n\n"
            "🎯 **Risk Level**: Medium\n"
            "⚕️ **Recommendation**: Schedule follow-up with your physician within 2 weeks.\n\n"
            "*This is AI-generated guidance, not a substitute for professional medical advice.*"
        )

    def _demo_chat_response(self, user_message: str) -> str:
        """Return a contextual demo chat response."""
        msg_lower = user_message.lower()
        if any(w in msg_lower for w in ["blood pressure", "bp", "hypertension"]):
            return (
                "**Blood Pressure Management** 💙\n\n"
                "Normal blood pressure is below 120/80 mmHg. Here are key tips:\n\n"
                "• **Reduce sodium** to less than 2,300 mg daily\n"
                "• **Exercise regularly** — 30 minutes of moderate activity most days\n"
                "• **Manage stress** through deep breathing or meditation\n"
                "• **Monitor at home** with a validated BP monitor\n"
                "• **Take medications** as prescribed — never skip doses\n\n"
                "If your BP is consistently above 140/90, contact your doctor promptly.\n\n"
                "*⚠️ Demo Mode: Configure IBM watsonx credentials for full AI responses.*"
            )
        if any(w in msg_lower for w in ["sugar", "glucose", "diabetes"]):
            return (
                "**Diabetes & Blood Sugar Management** 🩸\n\n"
                "Target blood glucose levels:\n"
                "• **Fasting**: 80–130 mg/dL\n"
                "• **Post-meal (2hr)**: Less than 180 mg/dL\n\n"
                "**Key strategies:**\n"
                "• Eat consistent meals at regular times\n"
                "• Choose low glycemic index foods\n"
                "• Exercise after meals to lower glucose\n"
                "• Stay well hydrated\n"
                "• Monitor glucose as recommended\n\n"
                "*⚠️ Demo Mode: Configure IBM watsonx credentials for full AI responses.*"
            )
        return (
            "Hello! I'm **CareBot**, your AI health companion powered by IBM Granite. 👋\n\n"
            "I can help you with:\n"
            "• Understanding your chronic disease\n"
            "• Medication guidance\n"
            "• Diet and lifestyle advice\n"
            "• Interpreting your health data\n"
            "• Emergency recognition\n\n"
            "Please ask me anything about your health!\n\n"
            "*⚠️ Demo Mode: Add IBM watsonx credentials in `.env` for full AI capabilities.*"
        )

    @property
    def is_configured(self) -> bool:
        """Check if IBM credentials are properly configured."""
        return bool(self.api_key and self.project_id)
