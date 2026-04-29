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

    system_message = """Eres un asistente que crea desafíos divertidos para niños y adolescentes chilenos.
Reglas que SIEMPRE debes seguir:
- Usa lenguaje simple, como si le hablaras a un amigo. NUNCA uses palabras técnicas o científicas sueltas como nombres de actividad.
- La descripción SIEMPRE debe tener al menos 2 pasos concretos que expliquen QUÉ hacer, CÓMO hacerlo y con QUÉ materiales (si aplica).
- NUNCA escribas una sola palabra o frase corta como descripción. Si la actividad se puede resumir en una palabra, NO es válida — desglósala en pasos.
- Las actividades deben ser realizables en casa o en el barrio, sin equipos especiales.
- Adapta todo al contexto chileno."""
    prompt = f"""Genera exactamente {cantidad} desafíos de categoría "{categoria}" con dificultad "{dificultad}" para {contexto}

Los puntos deben seguir esta escala según la dificultad:
- facil: entre 5 y 15 puntos
- medio: entre 20 y 35 puntos
- dificil: entre 40 y 50 puntos

EJEMPLOS de descripción CORRECTA e INCORRECTA:
❌ MAL: "Practica flotabilidad en el agua"
✅ BIEN: "Llena un balde con agua. Busca 5 objetos de la casa y prueba uno por uno si flotan o se hunden. Anota los resultados y cuéntaselos a alguien de tu familia."

❌ MAL: "Haz ejercicio físico"
✅ BIEN: "Pon una canción que te guste y haz 10 saltos en el lugar, 10 sentadillas y 10 flexiones de brazos. Descansa 30 segundos y repite 2 veces."

La descripcion SIEMPRE debe tener minimo 2 oraciones con pasos claros.
Responde SOLO con un JSON válido con este formato, sin texto extra:
{{
"desafios": [
    {{
    "titulo": "Título corto del desafío",
    "descripcion": "Paso 1: ... Paso 2: ... (mínimo 2 pasos concretos)",
    "puntos": 10,
    "tiempo_estimado_minutos": 5
    }}
]
}}"""

    respuesta = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}]
    )

    texto = respuesta.choices[0].message.content.strip()
    if texto.startswith("```"):
        texto = texto.split("```")[1]
        if texto.startswith("json"):
            texto = texto[4:]
        texto = texto.strip()
    return json.loads(texto)