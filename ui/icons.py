import io
from pathlib import Path

import customtkinter as ctk
import resvg_py
from PIL import Image

ICONS_DIR = Path(__file__).resolve().parent.parent / "public"

# Se renderiza más grande que el tamaño final para que CTkImage reduzca
# la imagen (y no la amplíe) en pantallas con escalado mayor a 100%.
SUPERSAMPLE = 4

_pil_cache = {}


def _render_svg(name, size, color):
    """Rasteriza public/<name>.svg aplicando el color al trazo del icono."""
    render_size = size * SUPERSAMPLE
    png = resvg_py.svg_to_bytes(
        svg_path=str(ICONS_DIR / f"{name}.svg"),
        width=render_size,
        height=render_size,
        style_sheet=f"svg {{ stroke: {color} }}",
    )
    return Image.open(io.BytesIO(png)).convert("RGBA")


def get_icon(name, size=18, light_color="#1E293B", dark_color="#F8FAFC"):
    """
    Retorna un CTkImage fresco creado sobre el intérprete Tkinter activo,
    reutilizando las imágenes base de Pillow cacheadas en memoria.
    """
    key = (name, size, light_color, dark_color)
    if key not in _pil_cache:
        img_light = _render_svg(name, size, light_color)
        img_dark = _render_svg(name, size, dark_color)
        _pil_cache[key] = (img_light, img_dark)

    img_light, img_dark = _pil_cache[key]
    return ctk.CTkImage(light_image=img_light, dark_image=img_dark, size=(size, size))
