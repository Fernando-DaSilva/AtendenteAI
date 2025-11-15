import json
import logging
from typing import Optional, Dict, Any
import httpx
from config import settings

logger = logging.getLogger(__name__)

# OpenRouter API endpoint
OPENROUTER_URL = "https://openrouter.io/api/v1/chat/completions"
OPENAI_URL = "https://api.openai.com/v1/chat/completions"


async def analyze_message(text: str, use_openrouter: bool = True) -> Dict[str, Any]:
    """
    Analyze incoming message and extract structured data using LLM.
    
    Args:
        text: Message text to analyze
        use_openrouter: Whether to use OpenRouter (default) or OpenAI
        
    Returns:
        Dictionary with extracted data (name, service, preferred_date, preferred_time, missing_slots, confidence)
    """
    prompt = f"""Extraia em JSON estruturado a seguinte informação da mensagem do cliente:
{{
  "name": "nome do cliente (se mencionado)",
  "service": "tipo de serviço desejado",
  "preferred_date": "data preferida em YYYY-MM-DD (se mencionada)",
  "preferred_time": "hora preferida em HH:MM (se mencionada)",
  "missing_slots": ["lista de campos faltantes para completar o agendamento"],
  "confidence": "nível de confiança 0-100"
}}

Mensagem: {text}

Retorne APENAS JSON válido, sem markdown ou comentários."""

    try:
        if use_openrouter:
            return await _call_openrouter(prompt)
        else:
            return await _call_openai(prompt)
    except Exception as e:
        logger.error(f"Error analyzing message: {e}")
        return {
            "name": "",
            "service": "",
            "preferred_date": "",
            "preferred_time": "",
            "missing_slots": ["error"],
            "confidence": 0
        }


async def _call_openrouter(prompt: str) -> Dict[str, Any]:
    """Call OpenRouter API for LLM inference."""
    if not settings.OPENROUTER_API_KEY:
        logger.warning("OpenRouter API key not configured, returning empty response")
        return {"error": "OpenRouter API key not set"}
    
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://myraos.ai",
        "X-Title": "AtendenteIA"
    }
    
    payload = {
        "model": "openrouter/auto",  # Auto-selects best available model
        "messages": [
            {"role": "system", "content": "Você é um especialista em extração de dados para agendamentos. Responda APENAS em JSON válido."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 500
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(OPENROUTER_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # Extract JSON from response
        content = data["choices"][0]["message"]["content"]
        try:
            result = json.loads(content)
            return result
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON response: {content}")
            return {"error": "Invalid JSON from API", "raw": content}


async def _call_openai(prompt: str) -> Dict[str, Any]:
    """Call OpenAI API for LLM inference (modern API, not deprecated)."""
    if not settings.OPENAI_API_KEY:
        logger.warning("OpenAI API key not configured, returning empty response")
        return {"error": "OpenAI API key not set"}
    
    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "gpt-4o-mini",  # Modern model that exists
        "messages": [
            {"role": "system", "content": "Você é um especialista em extração de dados para agendamentos. Responda APENAS em JSON válido."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 500
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(OPENAI_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # Extract JSON from response
        content = data["choices"][0]["message"]["content"]
        try:
            result = json.loads(content)
            return result
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON response: {content}")
            return {"error": "Invalid JSON from API", "raw": content}


def generate_reply(intent: str, data: Any) -> str:
    """
    Generate appropriate WhatsApp reply based on intent and data.
    
    Args:
        intent: Type of reply ('ask_slot', 'confirm', 'error')
        data: Supporting data for the reply
        
    Returns:
        Text message to send via WhatsApp
    """
    if intent == "ask_slot":
        missing = data.get("missing_slots", []) if isinstance(data, dict) else []
        if "service" in missing:
            return "Qual serviço você gostaria de agendar? 😊"
        elif "preferred_date" in missing:
            return "Qual data você prefere? 📅"
        elif "preferred_time" in missing:
            return "Que horário é melhor para você? ⏰"
        return "Só preciso de mais um detalhe. Qual informação está faltando?"
    elif intent == "confirm":
        slots = data if isinstance(data, list) else [str(data)]
        return f"Perfeito! Seu agendamento está marcado para {slots[0]}. Confirmado! ✅"
    elif intent == "error":
        return "Desculpe, houve um erro ao processar sua solicitação. Por favor, tente novamente. 🙏"
    else:
        return "Obrigado pelo contato! 🚀"
