# Manual de uso y pruebas

## 0. Resumen del orden de ejecución (Windows / PowerShell)

Se usan **3 terminales** abiertas en la carpeta del proyecto. Respeta este orden:

| Paso | Terminal | Comando | Qué hace |
|---|---|---|---|
| 1 | única vez | `pip install -r requirements.txt` | Instala Flask y requests |
| 2 | única vez | `python init_db.py` | Crea `usuarios.db` |
| 3 | Terminal 1 | `python app_vulnerable.py` | Levanta la app vulnerable (5000). **Dejar abierta** |
| 4 | Terminal 2 | `python app_segura.py` | Levanta la app segura (5001). **Dejar abierta** |
| 5 | Terminal 3 | `python ataque_sql_i.py --url http://127.0.0.1:5000` | Ataca la vulnerable (6/6) |
| 6 | Terminal 3 | `python ataque_sql_i.py --url http://127.0.0.1:5001` | Valida el parche (0/6) |
| 7 | Terminal 3 | `python escaneo_red.py` | Muestra puertos 5000 y 5001 abiertos |
| 8 | Terminal 3 | `python hardening_bd.py` y luego `python hardening_bd.py --aplicar` | Auditoría y endurecimiento |

Para detener un servidor: `Ctrl + C` en su terminal. Si `python` no funciona, usa `py`.
Si PowerShell bloquea la activación del entorno virtual, ejecuta una vez:
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

## 1. Requisitos
- Python 3.9 o superior
- Visual Studio Code, Git
- Navegador web

## 2. Instalación
```bash
git clone https://github.com/sramirezd2-tech/seguridad-sqli-lab.git
cd seguridad-sqli-lab
python -m venv venv
# Windows:  venv\Scripts\activate      Linux/Mac:  source venv/bin/activate
pip install -r requirements.txt        # instala Flask y requests
```

## 3. Crear la base de datos
```bash
python init_db.py
```
Salida esperada: `[OK] Base de datos creada en: ...usuarios.db`
Usuarios ficticios: `admin/admin123`, `maria/maria2026`, `juan/juan#pass`, `auditor/audit0r!`

## 4. Ejecutar la app VULNERABLE
```bash
python app_vulnerable.py
```
Abrir http://127.0.0.1:5000 

## 5. Ataques ANTES de la mitigación

### 5.1 Manual (navegador)
| Prueba | Dónde | Entrada |
|---|---|---|
| Bypass login | Usuario | `admin'--` (contraseña cualquiera) |
| Bypass login | Usuario / Contraseña | `admin' OR '1'='1` / `x' OR '1'='1` |
| Error SQL | Usuario | `'` |
| Extracción | Buscador | `zzz' UNION SELECT id, username, password, rol FROM usuarios--` |
| Esquema | Buscador | `zzz' UNION SELECT 1, name, sql, 0 FROM sqlite_master WHERE type='table'--` |

### 5.2 Automatizada
En otra terminal:
```bash
python ataque_sql_i.py --url http://127.0.0.1:5000
```
Resultado esperado: `Ataques exitosos: 6/6 => APLICACIÓN VULNERABLE` y archivo `resultados_5000.json`.

## 6. Validar el PARCHE
Detener la app vulnerable (o dejarla) y ejecutar:
```bash
python app_segura.py
python ataque_sql_i.py --url http://127.0.0.1:5001
```
Resultado esperado: `Ataques exitosos: 0/6 => Ataques neutralizados`.
Repetir manualmente los payloads del punto 5.1 en http://127.0.0.1:5001: no hay bypass ni extracción.

## 7. Módulo de escaneo de red
```bash
python escaneo_red.py                      # puertos comunes de 127.0.0.1
python escaneo_red.py -t 127.0.0.1 -p 1-1024 --json
```
Debe mostrar abiertos los puertos 5000 y 5001 (apps Flask). 

## 8. Hardening de la base de datos
```bash
python hardening_bd.py              # solo auditoría
python hardening_bd.py --aplicar    # genera usuarios_hardened.db
```
Antes: contraseñas en texto plano y permisos abiertos. Después: hash con salt (scrypt), permisos 600 y respaldo.

## 9. Tabla comparativa de resultados esperados

| ID | Prueba | App vulnerable (5000) | App segura (5001) |
|---|---|---|---|
| T1 | Login legítimo | Acceso (200) | Acceso (200) |
| T2 | Credenciales falsas | Rechazado (401) | Rechazado (401) |
| T3 | `OR '1'='1'` | **Bypass (200)** | Rechazado (401) |
| T4 | `admin'--` | **Bypass (200)** | Rechazado (401) |
| T5 | Comilla simple | **Error SQL expuesto (500)** | Rechazado (401), sin detalles |
| T6 | Búsqueda legítima | Resultados | Resultados |
| T7 | UNION usuarios | **Contraseñas expuestas** | 0 resultados |
| T8 | sqlite_master | **Esquema expuesto** | 0 resultados |
| T9 | `' OR 1=1--` | **Todos los registros** | 0 resultados |

## 10. Problemas frecuentes
- *Address already in use:* otro proceso usa el puerto; ciérralo o cambia el puerto en `app.run`.
- *ModuleNotFoundError:* activa el entorno virtual y ejecuta `pip install -r requirements.txt`.
- *Unable to open database:* ejecuta primero `python init_db.py`.
