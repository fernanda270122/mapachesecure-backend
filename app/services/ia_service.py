import os
import json
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generar_desafios(categoria: str, edad: int, dificultad: str, cantidad: int = 2):
    prompt = f"""Eres un asistente educativo para niños de {edad} años.
    Genera exactamente {cantidad} desafíos de categoría "{categoria}" con dificultad "{dificultad}".

    Los puntos deben seguir esta escala según la dificultad:
    - facil: entre 5 y 15 puntos
    - medio: entre 20 y 35 puntos
    - dificil: entre 40 y 50 puntos

    Responde SOLO con un JSON válido con este formato, sin texto extra:
    {{
    "desafios": [
        {{
        "titulo": "Título corto del desafío",
        "descripcion": "Instrucción clara de qué debe hacer el niño",
        "puntos": 10,
        "tiempo_estimado_minutos": 5
        }}
    ]
    }}"""

    respuesta = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    texto = respuesta.choices[0].message.content
    return json.loads(texto)