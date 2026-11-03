"""
app_vulnerable.py - Aplicación Flask INTENCIONALMENTE VULNERABLE a SQL Injection.

*** SOLO PARA FINES EDUCATIVOS. NO DESPLEGAR EN INTERNET NI USAR EN PRODUCCIÓN. ***

Vulnerabilidad (CWE-89): las consultas se arman concatenando texto ingresado
por el usuario, por lo que la entrada puede alterar la lógica del SQL.

Puerto: 5000 (solo escucha en 127.0.0.1)
"""
import os
import sqlite3

from flask import Flask, request

from ui import pagina as _pagina

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "usuarios.db")



def consultar(sql):
    con = sqlite3.connect(DB_PATH)
    try:
        return con.execute(sql).fetchall()
    finally:
        con.close()


def pagina(**kw):
    kw.setdefault("titulo", "Tienda Demo (VULNERABLE)")
    return _pagina(True, **kw)


@app.route("/")
def index():
    return pagina()


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "")
    password = request.form.get("password", "")

    # VULNERABLE: concatenación directa de la entrada del usuario
    sql = (
        "SELECT id, username, rol FROM usuarios "
        "WHERE username = '" + username + "' AND password = '" + password + "'"
    )
    try:
        filas = consultar(sql)
    except sqlite3.Error as e:
        # VULNERABLE: expone el error interno de la base de datos
        return pagina(sql=sql, mensaje=f"Error SQL: {e}", clase="err"), 500

    if filas:
        _, usuario, rol = filas[0]
        return pagina(sql=sql, mensaje=f"Bienvenido {usuario} (rol: {rol}) - LOGIN EXITOSO")
    return pagina(sql=sql, mensaje="Credenciales incorrectas", clase="err"), 401


@app.route("/buscar")
def buscar():
    q = request.args.get("q", "")

    # VULNERABLE: concatenación directa de la entrada del usuario
    sql = (
        "SELECT id, nombre, descripcion, precio FROM productos "
        "WHERE nombre LIKE '%" + q + "%'"
    )
    try:
        filas = consultar(sql)
    except sqlite3.Error as e:
        return pagina(q=q, sql=sql, mensaje=f"Error SQL: {e}", clase="err"), 500
    return pagina(q=q, sql=sql, filas=filas, mensaje=f"{len(filas)} resultado(s)")


if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        from init_db import crear_bd
        crear_bd()
    # host 127.0.0.1: nunca exponer esta app a la red
    app.run(host="127.0.0.1", port=5000, debug=False)
