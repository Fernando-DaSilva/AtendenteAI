import openai
from config import settings

openai.api_key = settings.OPENAI_API_KEY


def analyze_message(text: str):
    prompt = f"""
Extraia em JSON:
{{
  "name": "",
  "service": "",
  "preferred_date": "",
  "preferred_time": "",
  "missing_slots": [],
  "confidence": 0
}}
Mensagem: {text}
"""

    response = openai.ChatCompletion.create(
        model="gpt-4.1",
        messages=[{"role": "system", "content": "Você extrai dados para agendamento."},
                  {"role": "user", "content": prompt}]
    )
    return response.choices[0].message["content"]


def generate_reply(intent: str, data):
    if intent == "ask_slot":
        return "Só preciso de mais um detalhe: qual serviço você gostaria?"
    return "Perfeito! Já estou finalizando seu agendamento."
