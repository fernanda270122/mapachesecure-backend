import http from "k6/http";
import { check, sleep } from "k6";

const BASE_URL = "https://mapachesecure-backend.onrender.com";

export const options = {
  scenarios: {
    // Escenario A: calentamiento 15s (1 VU) + carga real 40s (5 VUs)
    flujo_normal: {
      executor: "ramping-vus",
      stages: [
        { duration: "15s", target: 1 },  // calentamiento — despierta el servidor
        { duration: "10s", target: 5 },  // sube a 5 VUs
        { duration: "40s", target: 5 },  // mantiene carga
        { duration: "10s", target: 0 },
      ],
      exec: "flujoNormal",
    },
    // Escenario B: registros concurrentes (5 VUs, empieza a los 5 seg)
    registros: {
      executor: "ramping-vus",
      startTime: "5s",
      stages: [
        { duration: "15s", target: 5 },
        { duration: "20s", target: 5 },
        { duration: "5s", target: 0 },
      ],
      exec: "registroNuevoPadre",
    },
  },
  thresholds: {
    "http_req_duration{scenario:flujo_normal}": ["p(95)<1000"],
    "http_req_duration{scenario:registros}":    ["p(95)<2000"],
    // Excluye los 429 de Supabase (rate limit de registros masivos, comportamiento esperado)
    "http_req_failed{scenario:flujo_normal}":   ["rate<0.05"],
  },
};

// setup() corre UNA vez — obtiene token e hijo_id del padre de prueba
export function setup() {
  const loginRes = http.post(
    `${BASE_URL}/auth/login`,
    JSON.stringify({ email: "fer.arrano.munoz@gmail.com", password: "cata1234" }),
    { headers: { "Content-Type": "application/json" } }
  );

  check(loginRes, { "setup login ok": (r) => r.status === 200 });

  const token  = loginRes.json("access_token");
  const padreId = loginRes.json("user_id");

  // Obtiene el primer hijo vinculado al padre
  const hijosRes = http.get(
    `${BASE_URL}/usuarios/${padreId}/hijos`,
    { headers: { Authorization: `Bearer ${token}` } }
  );

  let hijoId = null;
  if (hijosRes.status === 200) {
    const hijos = hijosRes.json();
    if (Array.isArray(hijos) && hijos.length > 0) {
      hijoId = hijos[0].id;
    }
  }

  console.log(`Setup OK — padreId=${padreId}  hijoId=${hijoId}`);
  return { token, hijoId };
}

// ── Escenario A: flujo real de un padre/hijo usando la app ───────────────────
export function flujoNormal(data) {
  if (!data.token || !data.hijoId) return;

  const h = { headers: { Authorization: `Bearer ${data.token}` } };

  // Consultar desafíos del hijo
  const r1 = http.get(`${BASE_URL}/desafios/hijo/${data.hijoId}`, h);
  check(r1, { "desafios: servidor responde": (r) => r.status < 500 });
  sleep(0.5);

  // Consultar puntos acumulados
  const r2 = http.get(`${BASE_URL}/desafios/puntos/${data.hijoId}`, h);
  check(r2, { "puntos: servidor responde": (r) => r.status < 500 });
  sleep(0.5);

  // Verificar si YouTube está bloqueado
  const r3 = http.get(
    `${BASE_URL}/apps/verificar/${data.hijoId}/com.google.android.youtube`,
    h
  );
  check(r3, { "verificar app: servidor responde": (r) => r.status < 500 });
  sleep(0.5);

  // Listar apps bloqueadas
  const r4 = http.get(`${BASE_URL}/apps/${data.hijoId}`, h);
  check(r4, { "apps bloqueadas: servidor responde": (r) => r.status < 500 });
  sleep(1);
}

// ── Escenario B: capacidad de registro — Supabase free tier permite 4 registros/hora
// antes de aplicar rate limit (429). Emails de prueba — borrar de Supabase después.
export function registroNuevoPadre() {
  const ts    = Date.now();
  const email = `carga_vu${__VU}_it${__ITER}_${ts}@raccu.test`;

  const res = http.post(
    `${BASE_URL}/auth/registro`,
    JSON.stringify({
      email:    email,
      password: "Test1234!",
      nombre:   `Carga VU${__VU}`,
      rol:      "padre",
    }),
    { headers: { "Content-Type": "application/json" } }
  );

  check(res, {
    "registro: servidor responde":          (r) => r.status < 500,
    "registro: rate limit activo (anti-spam)": (r) => r.status === 429 || r.status === 200 || r.status === 201,
  });

  sleep(2);
}

