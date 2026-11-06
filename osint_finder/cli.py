"""Interfaz de línea de comandos de osint_finder."""

from __future__ import annotations

import argparse
import os
import sys

from . import __version__
from .breaches import check_breaches
from .checker import FOUND, search_username
from .output import (build_json, print_breach_report, print_result_line,
                     print_summary)
from .sites import all_categories

BANNER = r"""
  ___  ____ ___ _   _ _____    _____ ___ _   _ ____  _____ ____
 / _ \/ ___|_ _| \ | |_   _|  |  ___|_ _| \ | |  _ \| ____|  _ \
| | | \___ \| ||  \| | | |    | |_   | ||  \| | | | |  _| | |_) |
| |_| |___) | || |\  | | |    |  _|  | || |\  | |_| | |___|  _ <
 \___/|____/___|_| \_| |_|    |_|   |___|_| \_|____/|_____|_| \_\

 Enumeración OSINT de usuario en plataformas públicas
 Uso legítimo sobre información pública · NO revela contraseñas
"""


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="osint_finder",
        description="Busca en qué plataformas públicas existe un nombre de usuario "
                    "y, opcionalmente, si un correo/usuario apareció en brechas "
                    "conocidas (sin mostrar contraseñas).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("usernames", nargs="*", help="Uno o más nombres de usuario a buscar.")
    p.add_argument("--version", action="version", version=f"osint_finder {__version__}")

    g = p.add_argument_group("búsqueda")
    g.add_argument("-c", "--categories", nargs="+", metavar="CAT",
                   help=f"Limitar a categorías: {', '.join(all_categories())}.")
    g.add_argument("--timeout", type=float, default=10.0,
                   help="Tiempo de espera por petición en segundos (def. 10).")
    g.add_argument("--workers", type=int, default=20,
                   help="Peticiones concurrentes (def. 20).")
    g.add_argument("--only-found", action="store_true",
                   help="Mostrar solo las plataformas donde se encontró el usuario.")

    b = p.add_argument_group("brechas (opcional, sin contraseñas)")
    b.add_argument("--breach", metavar="CORREO_O_USUARIO",
                   help="Comprobar exposición en brechas estilo HIBP (solo sí/no + "
                        "nombre de la brecha; nunca contraseñas).")
    b.add_argument("--hibp-key", default=os.environ.get("HIBP_API_KEY"),
                   help="Clave de API de HIBP (o variable HIBP_API_KEY).")

    o = p.add_argument_group("salida")
    o.add_argument("--json", dest="json_out", metavar="ARCHIVO", nargs="?",
                   const="-", help="Exportar en JSON (a ARCHIVO o a stdout si se omite).")
    o.add_argument("--no-color", action="store_true", help="Desactivar colores.")
    o.add_argument("--no-banner", action="store_true", help="No mostrar el banner.")
    return p


def run(argv=None) -> int:
    args = build_parser().parse_args(argv)
    color = not args.no_color and sys.stdout.isatty()

    if not args.usernames and not args.breach:
        build_parser().print_help()
        return 2

    if not args.no_banner and not (args.json_out == "-"):
        print(BANNER)

    json_payloads = []

    for username in args.usernames:
        if not args.json_out:
            print(f"\n>> Buscando '{username}' en plataformas públicas...\n")

        seen = {"n": 0}
        total = None

        def progress(res):
            if args.json_out:
                return
            print_result_line(res, color=color, only_found=args.only_found)

        results = search_username(
            username,
            categories=args.categories,
            timeout=args.timeout,
            workers=args.workers,
            progress=None if args.json_out else progress,
        )

        breach_report = None
        if args.breach:
            breach_report = check_breaches(args.breach, args.hibp_key,
                                          timeout=args.timeout)

        if args.json_out:
            json_payloads.append(build_json(username, results, breach_report))
        else:
            print_summary(username, results, color=color)
            if breach_report is not None:
                print_breach_report(breach_report, color=color)

    # Caso: solo comprobación de brechas, sin usernames.
    if args.breach and not args.usernames:
        report = check_breaches(args.breach, args.hibp_key, timeout=args.timeout)
        if args.json_out:
            json_payloads.append(build_json(args.breach, [], report))
        else:
            print_breach_report(report, color=color)

    if args.json_out:
        output = "\n".join(json_payloads)
        if args.json_out == "-":
            print(output)
        else:
            with open(args.json_out, "w", encoding="utf-8") as fh:
                fh.write(output + "\n")
            print(f"Resultados guardados en {args.json_out}")

    return 0


def main():
    try:
        sys.exit(run())
    except KeyboardInterrupt:
        print("\nInterrumpido.", file=sys.stderr)
        sys.exit(130)


if __name__ == "__main__":
    main()
