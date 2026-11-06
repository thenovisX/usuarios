"""Lógica de comprobación de existencia de un usuario en cada plataforma."""

from __future__ import annotations

import concurrent.futures
from dataclasses import dataclass

import requests

from .sites import iter_sites

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)

# Estados posibles del resultado de una comprobación.
FOUND = "found"
NOT_FOUND = "not_found"
UNKNOWN = "unknown"
ERROR = "error"


@dataclass
class Result:
    site: str
    category: str
    url: str
    status: str  # FOUND | NOT_FOUND | UNKNOWN | ERROR
    http_status: int | None = None
    detail: str = ""

    @property
    def exists(self) -> bool:
        return self.status == FOUND


def _check_site(site: dict, username: str, session: requests.Session,
                timeout: float) -> Result:
    url = site["url"].format(username)
    check = site["check"]
    try:
        # redirect=False solo para la estrategia de redirección; el resto sigue
        # redirecciones normales como lo haría un navegador.
        allow_redirects = check != "redirect"
        resp = session.get(url, timeout=timeout, allow_redirects=allow_redirects)
    except requests.RequestException as exc:
        return Result(site["name"], site["category"], url, ERROR,
                      detail=type(exc).__name__)

    code = resp.status_code

    if check == "status":
        if code == 404 or code == 410:
            return Result(site["name"], site["category"], url, NOT_FOUND, code)
        if 200 <= code < 300:
            return Result(site["name"], site["category"], url, FOUND, code)
        # 403/429/5xx: la plataforma bloquea o no responde con certeza.
        return Result(site["name"], site["category"], url, UNKNOWN, code,
                      detail="respuesta ambigua")

    if check == "message":
        if 200 <= code < 300:
            body = resp.text
            for needle in site.get("absence", []):
                if needle in body:
                    return Result(site["name"], site["category"], url,
                                  NOT_FOUND, code)
            return Result(site["name"], site["category"], url, FOUND, code)
        if code == 404 or code == 410:
            return Result(site["name"], site["category"], url, NOT_FOUND, code)
        return Result(site["name"], site["category"], url, UNKNOWN, code,
                      detail="respuesta ambigua")

    if check == "redirect":
        # Existe si NO hubo redirección (status directo 2xx).
        if 200 <= code < 300:
            return Result(site["name"], site["category"], url, FOUND, code)
        if code in (301, 302, 303, 307, 308):
            return Result(site["name"], site["category"], url, NOT_FOUND, code)
        if code == 404:
            return Result(site["name"], site["category"], url, NOT_FOUND, code)
        return Result(site["name"], site["category"], url, UNKNOWN, code)

    return Result(site["name"], site["category"], url, UNKNOWN, code,
                  detail="estrategia desconocida")


def search_username(username: str, *, categories=None, timeout: float = 10.0,
                    workers: int = 20, progress=None) -> list[Result]:
    """Comprueba el usuario en todas las plataformas (o las de `categories`).

    `progress` es un callable opcional que recibe cada Result en cuanto termina,
    útil para mostrar avance en la CLI.
    """
    sites = list(iter_sites(categories))
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT,
                            "Accept-Language": "en-US,en;q=0.9"})

    results: list[Result] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(_check_site, site, username, session, timeout): site
            for site in sites
        }
        for fut in concurrent.futures.as_completed(futures):
            res = fut.result()
            results.append(res)
            if progress:
                progress(res)

    results.sort(key=lambda r: (r.category, r.site.lower()))
    return results
