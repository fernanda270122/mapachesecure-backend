import os
import json
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generar_desafios(categoria: str, edad: int, dificultad: str, cantidad: int = 2,                                                                                                                              
                     sexo: str = None, nivel_escolar: str = None,
                    intereses: list = None, personalidad: str = None):                                                                                                                   
    contexto = f"un niño de {edad} años"
    if sexo and sexo != "prefiero no decir":
        contexto = f"una {'niña' if sexo == 'femenino' else 'niño'} de {edad} años"
    if nivel_escolar:
        contexto += f", nivel escolar {nivel_escolar}"
    if intereses:
        contexto += f", con intereses en {', '.join(intereses)}"
    if personalidad:
        contexto += f", personalidad {personalidad}"

    prompt = f"""Eres un asistente educativo para niños chilenos.
Genera exactamente {cantidad} desafíos de categoría "{categoria}" con dificultad "{dificultad}" para {contexto}.

Los puntos deben seguir esta escala según la dificultad:
- facil: entre 5 y 15 puntos
- medio: entre 20 y 35 puntos
- dificil: entre 40 y 50 puntos

Adapta el lenguaje y las actividades al contexto chileno.
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

    texto = respuesta.choices[0].message.content.strip()
    if texto.startswith("```"):
        texto = texto.split("```")[1]
        if texto.startswith("json"):
            texto = texto[4:]
        texto = texto.strip()
    return json.loads(texto)