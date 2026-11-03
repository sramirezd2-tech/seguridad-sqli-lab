"""
init_db.py - Crea la base de datos SQLite de laboratorio (usuarios.db).

Contiene datos FICTICIOS. Las contraseñas están en texto plano a propósito
para poder demostrar el impacto de la extracción no autorizada (la mala
práctica se corrige en hardening_bd.py).
"""
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "usuarios.db")


def crear_bd(ruta=DB_PATH):
    if os.path.exists(ruta):
        os.remove(ruta)
    con = sqlite3.connect(ruta)
    cur = con.cursor()
    cur.executescript(
        """
        CREATE TABLE usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            rol TEXT NOT NULL
        );
        CREATE TABLE productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            precio REAL NOT NULL
        );
        """
    )
    cur.executemany(
        "INSERT INTO usuarios (username, password, rol) VALUES (?, ?, ?)",
        [
            ("admin", "admin123", "administrador"),
            ("maria", "maria2026", "usuario"),
            ("juan", "juan#pass", "usuario"),
            ("auditor", "audit0r!", "auditor"),
        ],
    )
    cur.executemany(
        "INSERT INTO productos (nombre, descripcion, precio) VALUES (?, ?, ?)",
        [
            ("Laptop Pro 14", "Laptop para desarrollo", 950.00),
            ("Mouse Inalambrico", "Mouse ergonomico", 18.50),
            ("Teclado Mecanico", "Teclado switch azul", 45.00),
            ("Monitor 24 pulgadas", "Monitor Full HD", 160.00),
            ("Router WiFi 6", "Router doble banda", 85.00),
        ],
    )
    con.commit()
    con.close()
    print(f"[OK] Base de datos creada en: {ruta}")


if __name__ == "__main__":
    crear_bd()
