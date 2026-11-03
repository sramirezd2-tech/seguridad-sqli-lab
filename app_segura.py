"""
app_segura.py - Versión MITIGADA de app_vulnerable.py.

Contramedidas aplicadas:
  1. Consultas parametrizadas (sentencias preparadas con '?').
  2. Mensajes de error genéricos (no se filtran detalles de la BD).
  3. Validación básica de longitud de entrada (defensa en profundidad).
  4. Cabeceras de seguridad HTTP básicas.
  5. El SQL ya NO se muestra al cliente.

Puerto: 5001 (para poder comparar contra la vulnerable en el 5000).
"""
import os
import sqlite3

from flask import Flask, request

from ui import pagina as _pagina

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "usuarios.db")
MAX_LEN = 100  # límite alto a propósito: la defensa real es la parametrización



def consultar(sql, params=()):
    con = sqlite3.connect(DB_PATH)
    try:
        return con.execute(sql, params).fetchall()
    finally:
        con.close()


def pagina(**kw):
    kw.setdefault("titulo", "Tienda Demo (SEGURA)")
    return _pagina(False, **kw)


@app.after_request
def cabeceras(resp):
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["Content-Security-Policy"] = "default-src 'self'; style-src 'unsafe-inline'"
    return resp


@app.route("/")
def index():
    return pagina()


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "")
    password = request.form.get("password", "")

    if len(username) > MAX_LEN or len(password) > MAX_LEN:
        return pagina(mensaje="Entrada inválida", clase="err"), 400

    try:
        # SEGURO: los valores viajan separados de la sentencia SQL
        filas = consultar(
            "SELECT id, username, rol FROM usuarios WHERE username = ? AND password = ?",
            (username, password),
        )
    except sqlite3.Error:
        return pagina(mensaje="Error interno del servidor", clase="err"), 500

    if filas:
        _, usuario, rol = filas[0]
        return pagina(mensaje=f"Bienvenido {usuario} (rol: {rol}) - LOGIN EXITOSO")
    return pagina(mensaje="Credenciales incorrectas", clase="err"), 401


@app.route("/buscar")
def buscar():
    q = request.args.get("q", "")
    if len(q) > MAX_LEN:
        return pagina(mensaje="Entrada inválida", clase="err"), 400
    try:
        filas = consultar(
            "SELECT id, nombre, descripcion, precio FROM productos WHERE nombre LIKE ?",
            (f"%{q}%",),
        )
    except sqlite3.Error:
        return pagina(q=q, mensaje="Error interno del servidor", clase="err"), 500
    return pagina(q=q, filas=filas, mensaje=f"{len(filas)} resultado(s)")


if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        from init_db import crear_bd
        crear_bd()
    app.run(host="127.0.0.1", port=5001, debug=False)
