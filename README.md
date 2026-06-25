# MapacheSecure Backend

API REST para el sistema de autorregulación digital **MapacheSecure**, una plataforma que permite a padres e hijos gestionar el uso responsable de tecnología mediante desafíos, recompensas y control parental inteligente.

## Tecnologías

- **Python 3.11** + **FastAPI 0.135**
- **Supabase** — base de datos y autenticación
- **Google GenAI / Groq / Anthropic** — generación de desafíos con IA
- **Firebase Admin** — notificaciones push
- **Resend** — envío de correos transaccionales
- **Render** — despliegue en producción
- **GitHub Actions** — CI/CD con tests automáticos

## Estructura del proyecto

```
app/
├── main.py              # Punto de entrada FastAPI
├── database.py          # Conexión Supabase
├── dependencies.py      # Autenticación JWT
├── routers/             # Endpoints por módulo
│   ├── auth.py          # Registro, login, recuperación de contraseña
│   ├── usuarios.py      # Gestión de usuarios (padres e hijos)
│   ├── desafios.py      # CRUD de desafíos
│   ├── recompensas.py   # Sistema de recompensas
│   ├── canjes.py        # Canje de recompensas
│   ├── apps.py          # Gestión de aplicaciones monitoreadas
│   ├── bloqueos.py      # Control parental / bloqueo de apps
│   ├── ia.py            # Generación de desafíos con IA
│   ├── notificaciones.py# Push notifications vía Firebase
│   └── actividad.py     # Registro de actividad del hijo
├── services/            # Lógica de negocio
└── repositories/        # Acceso a datos (Supabase)
```

## Instalación local

### 1. Clonar el repositorio

```bash
git clone https://github.com/<org>/mapachesecure-backend.git
cd mapachesecure-backend
```

### 2. Crear entorno virtual e instalar dependencias

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
SUPABASE_URL=https://<tu-proyecto>.supabase.co
SUPABASE_KEY=<tu-service-role-key>
GOOGLE_API_KEY=<clave-google-genai>
ANTHROPIC_API_KEY=<clave-anthropic>
GROQ_API_KEY=<clave-groq>
FIREBASE_CREDENTIALS=<json-credenciales-firebase>
RESEND_API_KEY=<clave-resend>
```

### 4. Ejecutar el servidor

```bash
uvicorn app.main:app --reload
```

La API quedará disponible en `http://localhost:8000`.  
Documentación interactiva: `http://localhost:8000/docs`

## Endpoints principales

| Módulo | Ruta base | Descripción |
|---|---|---|
| Autenticación | `/auth` | Registro, login, logout, recuperación de contraseña, verificación de identidad |
| Usuarios | `/usuarios` | Gestión de perfiles de padres e hijos |
| Desafíos | `/desafios` | CRUD de desafíos asignados |
| Recompensas | `/recompensas` | Definición y gestión de recompensas |
| Canjes | `/canjes` | Canje de recompensas por puntos |
| Apps | `/apps` | Registro de aplicaciones monitoreadas |
| Bloqueos | `/bloqueos` | Control parental de aplicaciones |
| IA | `/ia` | Generación personalizada de desafíos con IA |
| Notificaciones | `/notificaciones` | Envío de push notifications |
| Actividad | `/actividad` | Historial de actividad digital del hijo |

## Tests

```bash
pip install -r requirements-test.txt
pytest tests/ -v
```

Los tests se ejecutan automáticamente en GitHub Actions en cada push a `main` o `dev`.

## Despliegue

El proyecto está configurado para desplegarse en **Render** (`render.yaml`).

```bash
# Build
pip install -r requirements.txt

# Start
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Las variables de entorno `SUPABASE_URL` y `SUPABASE_KEY` deben configurarse en el panel de Render.

## Seguridad

- Dependencias auditadas sin vulnerabilidades conocidas (`pip-audit`)
- Autenticación mediante JWT validado en cada endpoint protegido
- Variables sensibles gestionadas exclusivamente por variables de entorno

## Versión

**v1.1.6**
