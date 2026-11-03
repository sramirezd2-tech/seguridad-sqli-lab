"""
hardening_bd.py - Auditoría y endurecimiento (hardening) de la base SQLite.

Uso:
    python hardening_bd.py            # solo auditoría (no modifica nada)
    python hardening_bd.py --aplicar  # crea usuarios_hardened.db con mejoras

Controles que revisa/aplica:
  1. Permisos del archivo .db (solo propietario: 600)       [físico]
  2. Contraseñas en texto plano -> hash con salt (scrypt)    [datos]
  3. PRAGMA integrity_check y foreign_keys                   [integridad]
  4. Respaldo del archivo antes de modificar                 [disponibilidad]
  5. Recordatorio de principio de mínimo privilegio          [política]
"""
import argparse
import os
import shutil
import sqlite3
import stat
from datetime import datetime

from werkzeug.security import generate_password_hash

BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE, "usuarios.db")
DB_HARD = os.path.join(BASE, "usuarios_hardened.db")


def hay_hashes(valor):
    return valor.startswith(("scrypt:", "pbkdf2:"))


def auditar(ruta):
    print(f"\n=== AUDITORÍA de {os.path.basename(ruta)} ===")
    hallazgos = 0

    if os.name == "nt":
        # En Windows no existe chmod 600: el control equivalente son las ACL de NTFS
        print("[i] Windows: revisar permisos con 'icacls usuarios.db' y limitar el acceso "
              "al usuario propietario (los permisos tipo Unix no aplican).")
    else:
        modo = stat.S_IMODE(os.stat(ruta).st_mode)
        if modo & 0o077:
            print(f"[!] Permisos {oct(modo)}: otros usuarios pueden leer el archivo (usar 600)")
            hallazgos += 1
        else:
            print(f"[OK] Permisos {oct(modo)}")

    con = sqlite3.connect(ruta)
    plano = [u for (u, p) in con.execute("SELECT username, password FROM usuarios") if not hay_hashes(p)]
    if plano:
        print(f"[!] {len(plano)} contraseña(s) en TEXTO PLANO: {', '.join(plano)}")
        hallazgos += 1
    else:
        print("[OK] Todas las contraseñas están hasheadas")

    print(f"[i] integrity_check: {con.execute('PRAGMA integrity_check').fetchone()[0]}")
    print(f"[i] foreign_keys: {con.execute('PRAGMA foreign_keys').fetchone()[0]} (recomendado 1)")
    con.close()

    print("[i] Política: usar una cuenta de aplicación con mínimo privilegio (solo SELECT/INSERT "
          "necesarios) y nunca la cuenta administradora. En motores como MySQL/PostgreSQL: "
          "GRANT limitado + cifrado TLS + auditoría de logs.")
    print(f"\nHallazgos críticos: {hallazgos}")
    return hallazgos


def aplicar():
    if not os.path.exists(DB):
        raise SystemExit("Primero ejecute: python init_db.py")
    respaldo = os.path.join(BASE, f"respaldo_{datetime.now():%Y%m%d_%H%M%S}.db")
    shutil.copy2(DB, respaldo)
    print(f"[OK] Respaldo creado: {respaldo}")

    shutil.copy2(DB, DB_HARD)
    con = sqlite3.connect(DB_HARD)
    for uid, pwd in con.execute("SELECT id, password FROM usuarios").fetchall():
        if not hay_hashes(pwd):
            con.execute("UPDATE usuarios SET password = ? WHERE id = ?", (generate_password_hash(pwd), uid))
    con.commit()
    con.close()
    if os.name != "nt":
        os.chmod(DB_HARD, 0o600)
    print(f"[OK] Contraseñas hasheadas en {os.path.basename(DB_HARD)}"
          + ("" if os.name == "nt" else " y permisos 600"))
    print("[i] Para usarlas en la app, verificar con check_password_hash() tras buscar por username.")
    auditar(DB_HARD)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--aplicar", action="store_true")
    a = ap.parse_args()
    if not os.path.exists(DB):
        raise SystemExit("Primero ejecute: python init_db.py")
    auditar(DB)
    if a.aplicar:
        aplicar()