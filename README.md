# Laboratorio SQL Injection (Flask + SQLite)

Práctica 4 – Seguridad Informática · Universidad Estatal de Milagro (UNEMI)
Carrera de Tecnologías de la Información (en línea) · 2026

> **Aviso:** este proyecto es **intencionalmente vulnerable** y tiene fines **exclusivamente educativos**.
> Ejecútalo solo en `localhost`. No lo despliegues en Internet ni ataques sistemas sin autorización.

## ¿Qué contiene?

| Archivo | Descripción |
|---|---|
| `init_db.py` | Crea `usuarios.db` (SQLite) con datos ficticios |
| `app_vulnerable.py` | Servidor Flask vulnerable a SQLi (puerto 5000) |
| `ataque_sql_i.py` | Pruebas de inyección controladas (solo localhost) |
| `ui.py` | Interfaz HTML/CSS compartida por ambas apps |
| `app_segura.py` | Versión mitigada con consultas parametrizadas (puerto 5001) |
| `escaneo_red.py` | Escáner básico de puertos/servicios (solo red privada) |
| `hardening_bd.py` | Auditoría y endurecimiento de la base de datos |
| `MANUAL_USO.md` | Guía paso a paso de instalación, ataque y validación |
| `capturas/` | Capturas de pantalla de evidencia |

## Obtener el proyecto

```bash
git clone https://github.com/sramirezd2-tech/seguridad-sqli-lab.git
cd seguridad-sqli-lab
```

## Inicio rápido

```bash
pip install -r requirements.txt
python init_db.py
python app_vulnerable.py        # terminal 1  -> http://127.0.0.1:5000
python app_segura.py            # terminal 2  -> http://127.0.0.1:5001
python ataque_sql_i.py --url http://127.0.0.1:5000   # terminal 3 (ataque)
python ataque_sql_i.py --url http://127.0.0.1:5001   # validar parche
```

Detalles en [`MANUAL_USO.md`](MANUAL_USO.md).

## Resumen técnico

- **Vulnerabilidad:** CWE-89 / OWASP Top 10 (A03:2021 – Injection). Consultas SQL armadas por concatenación.
- **Mitigación:** sentencias preparadas (`?`), mensajes de error genéricos, validación de longitud, cabeceras HTTP de seguridad.
- **Resultado:** 6/6 ataques exitosos en la app vulnerable; 0/6 en la segura.

## Integrantes

JENNIFER BETANIA ALMEIDA CEDEÑO 
ALEX LEANDRO CEDEÑO JIMENEZ 
VIDAL FABIÁN MONTES BENAVIDES 
FREDDY VINICIO PAGUAY CUTIUPALA 
LEOVIGILDA SANDRA PEÑAHERRERA HOLGUIN 
STHEWART BAGNER RAMIREZ DIAZ
MARICELA DE JESUS ALAVA PORRO

## Licencia / uso ético

Uso académico. Los autores no se responsabilizan por el uso indebido.
