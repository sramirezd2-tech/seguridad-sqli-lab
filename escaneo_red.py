"""
escaneo_red.py - Escáner básico de puertos TCP (connect scan) con detección
simple de servicio y banner.

Uso:
    python escaneo_red.py                       # 127.0.0.1, puertos comunes + 5000/5001
    python escaneo_red.py -t 127.0.0.1 -p 1-1024
    python escaneo_red.py -t 192.168.1.10 -p 22,80,443

ÉTICA: solo escanea loopback o redes PRIVADAS (RFC1918). Escanear equipos
ajenos sin autorización puede ser delito. Úsalo solo en tu laboratorio.
"""
import argparse
import ipaddress
import json
import socket
import sys
from concurrent.futures import ThreadPoolExecutor

PUERTOS_COMUNES = [21, 22, 23, 25, 53, 80, 110, 139, 443, 445, 1433, 3306, 3389,
                   5000, 5001, 5432, 8000, 8080]


def validar_objetivo(host):
    ip = ipaddress.ip_address(socket.gethostbyname(host))
    if not (ip.is_loopback or ip.is_private):
        sys.exit(f"[BLOQUEADO] {ip} no es una IP privada/loopback. Solo se permite red de laboratorio.")
    return str(ip)


def parsear_puertos(texto):
    puertos = set()
    for parte in texto.split(","):
        if "-" in parte:
            a, b = parte.split("-")
            puertos.update(range(int(a), int(b) + 1))
        else:
            puertos.add(int(parte))
    return sorted(p for p in puertos if 1 <= p <= 65535)


def escanear_puerto(ip, puerto, timeout=0.6):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        if s.connect_ex((ip, puerto)) != 0:
            return None
        try:
            servicio = socket.getservbyport(puerto, "tcp")
        except OSError:
            servicio = "desconocido"
        banner = ""
        try:
            s.sendall(b"HEAD / HTTP/1.0\r\n\r\n")
            banner = s.recv(120).decode(errors="ignore").splitlines()[0]
        except Exception:
            pass
        return {"puerto": puerto, "estado": "abierto", "servicio": servicio, "banner": banner}
    finally:
        s.close()


def main():
    ap = argparse.ArgumentParser(description="Escáner de puertos básico (solo red privada)")
    ap.add_argument("-t", "--target", default="127.0.0.1")
    ap.add_argument("-p", "--ports", default=None, help="ej: 1-1024 o 22,80,443")
    ap.add_argument("--json", action="store_true", help="guardar escaneo.json")
    args = ap.parse_args()

    ip = validar_objetivo(args.target)
    puertos = parsear_puertos(args.ports) if args.ports else PUERTOS_COMUNES
    print(f"\n=== Escaneo de {ip} ({len(puertos)} puertos) ===\n")

    with ThreadPoolExecutor(max_workers=100) as ex:
        abiertos = [r for r in ex.map(lambda p: escanear_puerto(ip, p), puertos) if r]

    if not abiertos:
        print("No se encontraron puertos abiertos.")
    else:
        print(f"{'PUERTO':<8}{'ESTADO':<10}{'SERVICIO':<14}BANNER")
        print("-" * 70)
        for r in abiertos:
            print(f"{r['puerto']:<8}{r['estado']:<10}{r['servicio']:<14}{r['banner']}")

    print("\nRecomendaciones: cierre servicios innecesarios, use firewall (ufw/iptables)"
          " y exponga solo lo indispensable.")
    if args.json:
        with open("escaneo.json", "w", encoding="utf-8") as f:
            json.dump(abiertos, f, indent=2, ensure_ascii=False)
        print("Guardado en escaneo.json")


if __name__ == "__main__":
    main()
