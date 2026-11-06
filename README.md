# osint_finder

Herramienta OSINT de línea de comandos que, a partir de un **nombre de usuario**, descubre en qué **plataformas públicas** existe ese perfil (al estilo de [Sherlock](https://github.com/sherlock-project/sherlock) y [Maigret](https://github.com/soxoj/maigret)), consultando únicamente las URLs públicas de cada sitio, igual que haría un navegador.

Incluye además una comprobación **opcional** de exposición en brechas de datos al estilo de [Have I Been Pwned](https://haveibeenpwned.com): indica **si** un correo o usuario apareció en una filtración conocida y el **nombre y la fecha** de esa brecha.

## ⚠️ Alcance y uso responsable

- Esta herramienta es para **OSINT legítimo sobre información pública** y **uso autorizado** (investigación, verificación de tu propia huella digital, seguridad defensiva, concienciación).
- **NO recupera ni muestra contraseñas filtradas**, ni hashes, ni datos personales de cuentas ajenas. La comprobación de brechas solo responde *sí/no* y el nombre de la brecha. Recuperar o mostrar contraseñas de terceros facilita el robo de cuentas y el acoso, y **queda deliberadamente fuera** de este proyecto.
- Solo se consultan recursos **públicos**. No elude autenticación, CAPTCHAs ni límites de acceso, y no accede a información privada.
- Respeta la ley aplicable y los términos de servicio de cada plataforma. Úsala solo sobre cuentas tuyas o con autorización explícita. El autor y los colaboradores no se responsabilizan del uso indebido.

## Instalación

Requiere Python 3.9+.

```bash
git clone https://github.com/thenovisX/usuarios.git
cd usuarios
python -m venv .venv && source .venv/bin/activate   # opcional
pip install -r requirements.txt
```

O como paquete (deja disponible el comando `osint-finder`):

```bash
pip install -e .
```

## Uso

```bash
# Buscar un usuario en todas las plataformas
python -m osint_finder juanperez

# Varios usuarios a la vez
python -m osint_finder juanperez otra_cuenta

# Solo mostrar donde se encontró
python -m osint_finder juanperez --only-found

# Limitar por categoría (social, tech, community, media, gaming, other)
python -m osint_finder juanperez -c social tech

# Exportar a JSON
python -m osint_finder juanperez --json resultado.json

# Comprobar exposición en brechas (requiere clave de API de HIBP)
export HIBP_API_KEY="tu_clave"
python -m osint_finder juanperez --breach juan@example.com

# Solo comprobación de brechas, sin enumeración de plataformas
python -m osint_finder --breach juan@example.com
```

Si instalaste con `pip install -e .`, puedes usar `osint-finder` en lugar de `python -m osint_finder`.

### Opciones principales

| Opción | Descripción |
| --- | --- |
| `-c, --categories` | Limita la búsqueda a categorías concretas. |
| `--only-found` | Muestra solo las plataformas donde existe el usuario. |
| `--timeout` | Tiempo de espera por petición (segundos, def. 10). |
| `--workers` | Número de peticiones concurrentes (def. 20). |
| `--breach CORREO_O_USUARIO` | Comprueba exposición en brechas (sin contraseñas). |
| `--hibp-key` | Clave de API de HIBP (o variable `HIBP_API_KEY`). |
| `--json [ARCHIVO]` | Exporta en JSON (a archivo o a stdout). |
| `--no-color`, `--no-banner` | Salida sin colores / sin banner. |

## Cómo funciona

Para cada plataforma del catálogo (`osint_finder/sites.py`) se construye la URL pública del perfil y se decide si la cuenta existe mediante una de estas estrategias:

- **status**: existe si la respuesta HTTP es 2xx; no existe si es 404/410.
- **message**: existe salvo que el cuerpo de la respuesta contenga una cadena característica de "perfil no encontrado".
- **redirect**: no existe si la petición redirige fuera de la URL del perfil (p. ej. a la portada o al login).

Las plataformas que bloquean peticiones automáticas o responden de forma ambigua (403/429/5xx) se marcan como **inciertas** en vez de dar un falso positivo o negativo.

### Comprobación de brechas (HIBP)

Usa el endpoint `breachedaccount` de la API v3 de Have I Been Pwned, que **por diseño nunca devuelve contraseñas**: solo el nombre de la brecha, la fecha y las *categorías* de datos expuestos (p. ej. "Email addresses"). Necesitas una [clave de API de HIBP](https://haveibeenpwned.com/API/Key).

## Estructura del proyecto

```
osint_finder/
├── __init__.py
├── __main__.py      # punto de entrada (python -m osint_finder)
├── cli.py           # interfaz de línea de comandos
├── sites.py         # catálogo de plataformas y su detección
├── checker.py       # lógica de enumeración concurrente
├── breaches.py      # comprobación HIBP (solo sí/no + metadatos)
└── output.py        # formateo en terminal y JSON
```

## Limitaciones

- La detección depende del comportamiento actual de cada sitio; un cambio de HTML o de política anti-bots puede provocar resultados inciertos. Amplía o ajusta `sites.py` según sea necesario.
- Un resultado "encontrado" confirma que la URL del perfil existe, no que pertenezca a una persona concreta; varias personas pueden compartir un alias.

## Licencia

MIT. Ver [LICENSE](LICENSE).
