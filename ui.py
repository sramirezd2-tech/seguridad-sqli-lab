"""
ui.py - Interfaz compartida (HTML + CSS) de las dos aplicaciones del laboratorio.

Solo contiene presentación. La lógica de seguridad (vulnerable vs. segura)
está en app_vulnerable.py y app_segura.py.
"""
from flask import render_template_string

PLANTILLA = """
<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ titulo }}</title>
<style>
 :root{
   --acento: {{ '#c62828' if vulnerable else '#2e7d32' }};
   --acento-claro: {{ '#fdecea' if vulnerable else '#e8f5e9' }};
   --fondo:#f3f5f9; --texto:#1f2937; --borde:#dfe3ea;
 }
 *{box-sizing:border-box}
 body{margin:0;font-family:"Segoe UI",Arial,sans-serif;background:var(--fondo);color:var(--texto)}
 header{background:#111827;color:#fff;padding:16px 24px;display:flex;
        align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px}
 header h1{margin:0;font-size:1.25rem}
 header small{color:#9ca3af}
 .badge{background:var(--acento);color:#fff;padding:6px 14px;border-radius:999px;
        font-weight:700;font-size:.8rem;letter-spacing:.5px}
 main{max-width:980px;margin:24px auto;padding:0 16px}
 .aviso{background:var(--acento-claro);border-left:6px solid var(--acento);
        padding:12px 16px;border-radius:8px;margin-bottom:20px}
 .grid{display:grid;grid-template-columns:1fr 1fr;gap:20px}
 @media(max-width:760px){.grid{grid-template-columns:1fr}}
 .card{background:#fff;border:1px solid var(--borde);border-radius:12px;padding:20px;
       box-shadow:0 2px 6px rgba(0,0,0,.05)}
 .card h2{margin:0 0 14px;font-size:1.05rem}
 label{display:block;font-size:.85rem;margin:10px 0 4px;color:#4b5563}
 input{width:100%;padding:10px;border:1px solid #c5cbd6;border-radius:8px;font-size:.95rem}
 input:focus{outline:2px solid var(--acento);border-color:transparent}
 button{margin-top:14px;width:100%;padding:11px;border:0;border-radius:8px;cursor:pointer;
        background:var(--acento);color:#fff;font-weight:700;font-size:.95rem}
 button:hover{filter:brightness(1.1)}
 .resultado{margin-top:20px}
 .msg{padding:12px 16px;border-radius:8px;font-weight:600;margin-bottom:12px}
 .msg.ok{background:#e8f5e9;color:#1b5e20;border:1px solid #a5d6a7}
 .msg.err{background:#fdecea;color:#b71c1c;border:1px solid #ef9a9a}
 .sql{background:#0f172a;color:#a5f3fc;padding:12px 16px;border-radius:8px;
      font-family:Consolas,monospace;font-size:.85rem;overflow-x:auto;margin-bottom:12px}
 .sql span{color:#fca5a5;font-weight:700;display:block;margin-bottom:4px;
           font-family:"Segoe UI",Arial,sans-serif;font-size:.75rem}
 table{width:100%;border-collapse:collapse;background:#fff;border-radius:8px;overflow:hidden;
       border:1px solid var(--borde)}
 th{background:#111827;color:#fff;text-align:left;padding:10px;font-size:.85rem}
 td{padding:9px 10px;border-top:1px solid var(--borde);font-size:.9rem;word-break:break-word}
 tr:nth-child(even) td{background:#f9fafb}
 footer{text-align:center;color:#6b7280;font-size:.8rem;margin:30px 0}
</style>
</head>
<body>
<header>
  <div><h1>🛒 {{ titulo }}</h1><small>Laboratorio de Seguridad Informática · UNEMI</small></div>
  <span class="badge">{{ 'MODO VULNERABLE' if vulnerable else 'MODO SEGURO' }}</span>
</header>
<main>
  <div class="aviso">
   {% if vulnerable %}
    <b>Aplicación intencionalmente vulnerable.</b> Las consultas SQL se arman
    concatenando la entrada del usuario. Usar solo en localhost.
   {% else %}
    <b>Aplicación mitigada.</b> Las consultas usan sentencias preparadas
    (parámetros <code>?</code>): la entrada se trata como dato, nunca como código SQL.
   {% endif %}
  </div>

  <div class="grid">
    <section class="card">
      <h2>🔐 Iniciar sesión</h2>
      <form method="post" action="/login">
        <label for="u">Usuario</label>
        <input id="u" name="username" autocomplete="off">
        <label for="p">Contraseña</label>
        <input id="p" name="password" type="password" autocomplete="off">
        <button>Ingresar</button>
      </form>
    </section>

    <section class="card">
      <h2>🔎 Buscar productos</h2>
      <form method="get" action="/buscar">
        <label for="q">Nombre del producto</label>
        <input id="q" name="q" value="{{ q or '' }}" autocomplete="off">
        <button>Buscar</button>
      </form>
    </section>
  </div>

  {% if sql or mensaje or filas is not none %}
  <div class="resultado">
    {% if sql %}
      <div class="sql"><span>SQL EJECUTADO POR EL SERVIDOR</span>{{ sql }}</div>
    {% endif %}
    {% if mensaje %}<div class="msg {{ clase }}">{{ mensaje }}</div>{% endif %}
    {% if filas is not none and filas|length > 0 %}
    <table>
      <tr><th>ID</th><th>Nombre</th><th>Descripción</th><th>Precio</th></tr>
      {% for f in filas %}<tr>{% for c in f %}<td>{{ c }}</td>{% endfor %}</tr>{% endfor %}
    </table>
    {% endif %}
  </div>
  {% endif %}
</main>
<footer>Práctica 4 · Seguridad Informática · Uso académico en entorno controlado</footer>
</body></html>
"""


def pagina(vulnerable, **kw):
    kw.setdefault("titulo", "Tienda Demo")
    kw.setdefault("q", "")
    kw.setdefault("sql", None)
    kw.setdefault("mensaje", None)
    kw.setdefault("clase", "ok")
    kw.setdefault("filas", None)
    return render_template_string(PLANTILLA, vulnerable=vulnerable, **kw)
