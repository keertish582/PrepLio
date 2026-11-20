"""
core/llm.py — LLM adapter using Ollama
"""
import ollama
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

DEFAULT_MODEL = os.getenv("PREPLIO_MODEL", "qwen3:4b")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
TIMEOUT = 30


def check_ollama() -> dict:
    """Returns {"available": bool, "model_ready": bool, "message": str}"""
    try:
        client = ollama.Client(host=OLLAMA_HOST)
        models = client.list()
        model_names = [m.model for m in models.models]
        model_ready = any(DEFAULT_MODEL in m for m in model_names)
        if model_ready:
            return {"available": True, "model_ready": True, "message": f"Ready — {DEFAULT_MODEL}"}
        else:
            return {
                "available": True,
                "model_ready": False,
                "message": f"Ollama running but {DEFAULT_MODEL} not downloaded. Run: ollama pull {DEFAULT_MODEL}",
            }
    except Exception as e:
        return {
            "available": False,
            "model_ready": False,
            "message": f"Ollama unavailable at {OLLAMA_HOST}. Run: ollama serve",
        }


def chat(prompt: str, system: str = "", model: str = None) -> Optional[str]:
    """Single-turn chat. Returns None on failure. Never raises."""
    try:
        client = ollama.Client(host=OLLAMA_HOST)
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        resp = client.chat(model=model or DEFAULT_MODEL, messages=messages)
        return resp.message.content
    except Exception as e:
        logger.warning("LLM call failed: %s", str(e)[:200])
        return None
