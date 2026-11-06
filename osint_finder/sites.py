"""Catálogo de plataformas públicas a comprobar.

Cada sitio define cómo se construye la URL pública del perfil y cómo decidir si
la cuenta existe. Solo se consultan URLs públicas, igual que haría un navegador.

Tipos de detección (`check`):
  - "status":   existe si la respuesta es 2xx; ausente si es 404.
  - "message":  ausente si el cuerpo contiene alguna de las cadenas de
                `absence`; en caso contrario, existe (con respuesta 2xx).
  - "redirect": ausente si la petición redirige fuera de la URL del perfil
                (p. ej. a la portada o a /login).

Campos:
  name     Nombre legible de la plataforma.
  url      Plantilla de la URL del perfil; usa "{}" para el usuario.
  check    Estrategia de detección (ver arriba).
  absence  Lista de cadenas que indican "no existe" (solo para "message").
  category Categoría para agrupar la salida.
"""

SITES = [
    # --- Redes sociales ---
    {"name": "Instagram", "url": "https://www.instagram.com/{}/", "check": "status", "category": "social"},
    {"name": "Twitter/X", "url": "https://x.com/{}", "check": "status", "category": "social"},
    {"name": "Facebook", "url": "https://www.facebook.com/{}", "check": "status", "category": "social"},
    {"name": "TikTok", "url": "https://www.tiktok.com/@{}", "check": "status", "category": "social"},
    {"name": "Pinterest", "url": "https://www.pinterest.com/{}/", "check": "status", "category": "social"},
    {"name": "Snapchat", "url": "https://www.snapchat.com/add/{}", "check": "status", "category": "social"},
    {"name": "VK", "url": "https://vk.com/{}", "check": "message", "absence": ["This page is", "404 Not Found"], "category": "social"},
    {"name": "Tumblr", "url": "https://{}.tumblr.com", "check": "status", "category": "social"},

    # --- Desarrollo / tech ---
    {"name": "GitHub", "url": "https://github.com/{}", "check": "status", "category": "tech"},
    {"name": "GitLab", "url": "https://gitlab.com/{}", "check": "status", "category": "tech"},
    {"name": "Bitbucket", "url": "https://bitbucket.org/{}/", "check": "status", "category": "tech"},
    {"name": "Docker Hub", "url": "https://hub.docker.com/u/{}", "check": "status", "category": "tech"},
    {"name": "PyPI", "url": "https://pypi.org/user/{}/", "check": "status", "category": "tech"},
    {"name": "npm", "url": "https://www.npmjs.com/~{}", "check": "status", "category": "tech"},
    {"name": "Replit", "url": "https://replit.com/@{}", "check": "status", "category": "tech"},
    {"name": "HackerNews", "url": "https://news.ycombinator.com/user?id={}", "check": "message", "absence": ["No such user."], "category": "tech"},
    {"name": "Stack Overflow", "url": "https://stackoverflow.com/users/{}", "check": "status", "category": "tech"},
    {"name": "Keybase", "url": "https://keybase.io/{}", "check": "status", "category": "tech"},

    # --- Foros / comunidades ---
    {"name": "Reddit", "url": "https://www.reddit.com/user/{}", "check": "status", "category": "community"},
    {"name": "Medium", "url": "https://medium.com/@{}", "check": "status", "category": "community"},
    {"name": "Dev.to", "url": "https://dev.to/{}", "check": "status", "category": "community"},
    {"name": "Patreon", "url": "https://www.patreon.com/{}", "check": "status", "category": "community"},
    {"name": "ProductHunt", "url": "https://www.producthunt.com/@{}", "check": "status", "category": "community"},
    {"name": "Telegram", "url": "https://t.me/{}", "check": "message", "absence": ["If you have Telegram, you can contact"], "category": "community"},

    # --- Multimedia / creatividad ---
    {"name": "YouTube", "url": "https://www.youtube.com/@{}", "check": "status", "category": "media"},
    {"name": "Twitch", "url": "https://www.twitch.tv/{}", "check": "status", "category": "media"},
    {"name": "SoundCloud", "url": "https://soundcloud.com/{}", "check": "status", "category": "media"},
    {"name": "Spotify", "url": "https://open.spotify.com/user/{}", "check": "status", "category": "media"},
    {"name": "Vimeo", "url": "https://vimeo.com/{}", "check": "status", "category": "media"},
    {"name": "Flickr", "url": "https://www.flickr.com/people/{}", "check": "status", "category": "media"},
    {"name": "DeviantArt", "url": "https://{}.deviantart.com", "check": "status", "category": "media"},
    {"name": "Behance", "url": "https://www.behance.net/{}", "check": "status", "category": "media"},
    {"name": "Dribbble", "url": "https://dribbble.com/{}", "check": "status", "category": "media"},
    {"name": "500px", "url": "https://500px.com/p/{}", "check": "status", "category": "media"},
    {"name": "Imgur", "url": "https://imgur.com/user/{}", "check": "status", "category": "media"},
    {"name": "Last.fm", "url": "https://www.last.fm/user/{}", "check": "status", "category": "media"},

    # --- Gaming ---
    {"name": "Steam", "url": "https://steamcommunity.com/id/{}", "check": "message", "absence": ["The specified profile could not be found."], "category": "gaming"},
    {"name": "Chess.com", "url": "https://www.chess.com/member/{}", "check": "status", "category": "gaming"},
    {"name": "Lichess", "url": "https://lichess.org/@/{}", "check": "status", "category": "gaming"},

    # --- Otros ---
    {"name": "About.me", "url": "https://about.me/{}", "check": "status", "category": "other"},
    {"name": "Gravatar", "url": "https://gravatar.com/{}", "check": "status", "category": "other"},
    {"name": "Linktree", "url": "https://linktr.ee/{}", "check": "status", "category": "other"},
    {"name": "Wordpress", "url": "https://{}.wordpress.com", "check": "status", "category": "other"},
    {"name": "Blogger", "url": "https://{}.blogspot.com", "check": "status", "category": "other"},
]


def iter_sites(categories=None):
    """Devuelve los sitios, opcionalmente filtrados por categoría."""
    if not categories:
        yield from SITES
        return
    wanted = {c.lower() for c in categories}
    for site in SITES:
        if site["category"].lower() in wanted:
            yield site


def all_categories():
    return sorted({s["category"] for s in SITES})
