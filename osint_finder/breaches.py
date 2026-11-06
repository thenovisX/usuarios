"""Comprobación de exposición en brechas, estilo Have I Been Pwned.

IMPORTANTE — límites de diseño:
  * Esta comprobación SOLO indica SI un correo o usuario apareció en una brecha
    de datos pública conocida, y el nombre/fecha de esa brecha.
  * NUNCA recupera ni muestra contraseñas, hashes ni datos personales de la
    cuenta. Hacerlo facilitaría el robo de cuentas y queda fuera del alcance de
    esta herramienta.

Usa la API pública de Have I Been Pwned (v3), que requiere una clave de API.
La clave se obtiene en https://haveibeenpwned.com/API/Key y se pasa por el
argumento `--hibp-key` o la variable de entorno HIBP_API_KEY. Por diseño, la
propia API de HIBP tampoco expone contraseñas: solo metadatos de la brecha.
"""

from __future__ import annotations

from dataclasses import dataclass

import requests

HIBP_URL = "https://haveibeenpwned.com/api/v3/breachedaccount/{}"
USER_AGENT = "osint_finder (OSINT legítimo; https://haveibeenpwned.com/API/v3)"


@dataclass
class Breach:
    name: str
    domain: str
    breach_date: str
    data_classes: list  # tipos de datos expuestos (p. ej. "Email addresses")


@dataclass
class BreachReport:
    account: str
    checked: bool          # ¿se pudo consultar?
    exposed: bool          # ¿apareció en alguna brecha?
    breaches: list         # list[Breach]
    error: str = ""


def check_breaches(account: str, api_key: str, *, timeout: float = 15.0) -> BreachReport:
    """Consulta HIBP y devuelve SOLO metadatos de brechas (nunca contraseñas)."""
    if not api_key:
        return BreachReport(account, checked=False, exposed=False, breaches=[],
                            error="falta clave de API de HIBP (--hibp-key o HIBP_API_KEY)")

    headers = {"hibp-api-key": api_key, "User-Agent": USER_AGENT}
    # truncateResponse=false para recibir metadatos (nombre, fecha, tipos);
    # HIBP nunca devuelve contraseñas en este endpoint.
    params = {"truncateResponse": "false"}
    try:
        resp = requests.get(HIBP_URL.format(account), headers=headers,
                            params=params, timeout=timeout)
    except requests.RequestException as exc:
        return BreachReport(account, checked=False, exposed=False, breaches=[],
                            error=f"error de red: {type(exc).__name__}")

    if resp.status_code == 404:
        # HIBP devuelve 404 cuando la cuenta no está en ninguna brecha.
        return BreachReport(account, checked=True, exposed=False, breaches=[])

    if resp.status_code == 401:
        return BreachReport(account, checked=False, exposed=False, breaches=[],
                            error="clave de API inválida o no autorizada")

    if resp.status_code == 429:
        return BreachReport(account, checked=False, exposed=False, breaches=[],
                            error="límite de peticiones alcanzado; reintenta más tarde")

    if resp.status_code != 200:
        return BreachReport(account, checked=False, exposed=False, breaches=[],
                            error=f"respuesta inesperada: HTTP {resp.status_code}")

    breaches = []
    for item in resp.json():
        breaches.append(Breach(
            name=item.get("Name", ""),
            domain=item.get("Domain", ""),
            breach_date=item.get("BreachDate", ""),
            # Solo las CATEGORÍAS de datos expuestos, no los datos en sí.
            data_classes=item.get("DataClasses", []),
        ))
    return BreachReport(account, checked=True, exposed=bool(breaches),
                        breaches=breaches)
