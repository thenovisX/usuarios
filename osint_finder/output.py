"""Formateo de resultados para la terminal y para exportación JSON."""

from __future__ import annotations

import json

from .checker import FOUND, NOT_FOUND, UNKNOWN, ERROR, Result

# Colores ANSI (se desactivan si la salida no es un terminal).
_COLORS = {
    FOUND: "\033[92m",       # verde
    NOT_FOUND: "\033[90m",   # gris
    UNKNOWN: "\033[93m",     # amarillo
    ERROR: "\033[91m",       # rojo
    "reset": "\033[0m",
    "bold": "\033[1m",
}

_SYMBOL = {FOUND: "[+]", NOT_FOUND: "[-]", UNKNOWN: "[?]", ERROR: "[!]"}
_LABEL = {FOUND: "ENCONTRADO", NOT_FOUND: "no existe",
          UNKNOWN: "incierto", ERROR: "error"}


def _c(text: str, key: str, color: bool) -> str:
    if not color:
        return text
    return f"{_COLORS.get(key, '')}{text}{_COLORS['reset']}"


def print_result_line(res: Result, color: bool = True, only_found: bool = False):
    if only_found and res.status != FOUND:
        return
    symbol = _c(_SYMBOL[res.status], res.status, color)
    name = _c(f"{res.site:<16}", "bold", color) if res.status == FOUND else f"{res.site:<16}"
    label = _LABEL[res.status]
    extra = f" ({res.detail})" if res.detail and res.status in (UNKNOWN, ERROR) else ""
    if res.status == FOUND:
        print(f"  {symbol} {name} {res.url}")
    else:
        print(f"  {symbol} {name} {label}{extra}")


def print_summary(username: str, results: list[Result], color: bool = True):
    found = [r for r in results if r.status == FOUND]
    unknown = [r for r in results if r.status == UNKNOWN]
    errors = [r for r in results if r.status == ERROR]
    title = _c(f"Resumen para '{username}'", "bold", color)
    print(f"\n{title}")
    print(f"  Encontrados: {len(found)} | Inciertos: {len(unknown)} | "
          f"Errores: {len(errors)} | Total comprobados: {len(results)}")
    if found:
        print(f"  Perfiles encontrados: {', '.join(r.site for r in found)}")


def print_breach_report(report, color: bool = True):
    title = _c(f"\nExposición en brechas para '{report.account}'", "bold", color)
    print(title)
    if not report.checked:
        print(_c(f"  [!] No comprobado: {report.error}", ERROR, color))
        return
    if not report.exposed:
        print(_c("  [+] No aparece en ninguna brecha pública conocida.", FOUND, color))
        return
    print(_c(f"  [!] Aparece en {len(report.breaches)} brecha(s):", UNKNOWN, color))
    for b in report.breaches:
        fecha = f" ({b.breach_date})" if b.breach_date else ""
        print(f"    - {b.name}{fecha}  [datos expuestos: {', '.join(b.data_classes) or 'n/d'}]")
    print(_c("  Nota: esta herramienta NO muestra contraseñas; solo si hubo exposición.",
             NOT_FOUND, color))


def build_json(username: str, results: list[Result], breach_report=None) -> str:
    data = {
        "username": username,
        "results": [
            {
                "site": r.site,
                "category": r.category,
                "url": r.url,
                "status": r.status,
                "http_status": r.http_status,
                "detail": r.detail,
            }
            for r in results
        ],
        "found": [r.site for r in results if r.status == FOUND],
    }
    if breach_report is not None:
        data["breaches"] = {
            "account": breach_report.account,
            "checked": breach_report.checked,
            "exposed": breach_report.exposed,
            "error": breach_report.error,
            # Solo metadatos de brecha; nunca contraseñas.
            "items": [
                {
                    "name": b.name,
                    "domain": b.domain,
                    "breach_date": b.breach_date,
                    "data_classes": b.data_classes,
                }
                for b in breach_report.breaches
            ],
        }
    return json.dumps(data, indent=2, ensure_ascii=False)
