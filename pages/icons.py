import math
import customtkinter as ctk
from PIL import Image, ImageDraw

_pil_cache = {}


def _draw_lucide_shape(name, draw, s, rgba):
    scale = s / 24.0
    lw = max(1, round(2.0 * scale))

    def pt(x, y):
        return (x * scale, y * scale)

    def line(pts):
        scaled_pts = [pt(x, y) for (x, y) in pts]
        for i in range(len(scaled_pts) - 1):
            draw.line([scaled_pts[i], scaled_pts[i + 1]], fill=rgba, width=lw, joint="curve")

    def circle(cx, cy, r, fill=None, outline=rgba, width=lw):
        box = [pt(cx - r, cy - r), pt(cx + r, cy + r)]
        draw.ellipse(box, fill=fill, outline=outline, width=width)

    if name == "trending-up" or name == "chart":
        line([(23, 6), (13.5, 15.5), (8.5, 10.5), (1, 18)])
        line([(17, 6), (23, 6), (23, 12)])

    elif name == "logo":
        circle(12, 12, 10, fill=None, outline=rgba, width=max(1, round(1.4 * scale)))
        line([(5, 12), (19, 12)])
        line([(12, 5), (12, 19)])
        line([(6, 17), (18, 7)])
        circle(9, 14.5, 1.4, fill=rgba, outline=rgba)
        circle(15, 9.5, 1.4, fill=rgba, outline=rgba)

    elif name == "rocket":
        line([(12, 2), (16, 7), (16, 14), (13, 17), (11, 17), (8, 14), (8, 7), (12, 2)])
        circle(12, 9, 2, fill=None, outline=rgba, width=lw)
        line([(8, 11), (4, 15), (7, 16), (8, 14)])
        line([(16, 11), (20, 15), (17, 16), (16, 14)])
        line([(10, 17), (12, 21), (14, 17)])

    elif name == "sparkles":
        line([(12, 3), (12, 21)])
        line([(3, 12), (21, 12)])
        line([(6, 6), (18, 18)])
        line([(18, 6), (6, 18)])
        circle(12, 12, 2.5, fill=rgba, outline=rgba)

    elif name == "play":
        pts = [pt(7, 5), pt(19, 12), pt(7, 19)]
        draw.polygon(pts, fill=rgba, outline=rgba)

    elif name == "rotate-ccw":
        box = [pt(4, 4), pt(20, 20)]
        draw.arc(box, start=40, end=310, fill=rgba, width=lw)
        line([(3, 9), (4, 4), (9, 5)])

    elif name == "table":
        line([(3, 4), (21, 4), (21, 20), (3, 20), (3, 4)])
        line([(3, 10), (21, 10)])
        line([(10, 4), (10, 20)])

    elif name == "grid-math":
        circle(12, 12, 10, fill=None, outline=rgba, width=lw)
        line([(4, 12), (20, 12)])
        line([(12, 4), (12, 20)])
        line([(6, 16), (18, 8)])

    elif name == "sun":
        circle(12, 12, 4.5, fill=None, outline=rgba, width=lw)
        line([(12, 2), (12, 4.5)])
        line([(12, 19.5), (12, 22)])
        line([(2, 12), (4.5, 12)])
        line([(19.5, 12), (22, 12)])
        line([(4.93, 4.93), (6.7, 6.7)])
        line([(17.3, 17.3), (19.07, 19.07)])
        line([(4.93, 19.07), (6.7, 17.3)])
        line([(17.3, 6.7), (19.07, 4.93)])

    elif name == "moon":
        cx, cy, r = 12, 12, 8.5
        pts = []
        for deg in range(-80, 81, 10):
            rad = math.radians(deg)
            pts.append((cx + r * math.cos(rad) - 2.5, cy + r * math.sin(rad)))
        cx2, cy2, r2 = 9, 12, 6.2
        for deg in range(75, -76, -10):
            rad = math.radians(deg)
            pts.append((cx2 + r2 * math.cos(rad) - 2.5, cy2 + r2 * math.sin(rad)))
        scaled = [pt(x, y) for (x, y) in pts]
        draw.polygon(scaled, fill=rgba, outline=rgba)

    else:
        circle(12, 12, 5, fill=rgba, outline=rgba)


def _render_pil(name, size, rgba):
    render_size = size * 4
    img = Image.new("RGBA", (render_size, render_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    _draw_lucide_shape(name, draw, render_size, rgba)
    return img.resize((size, size), Image.Resampling.LANCZOS)


def get_icon(name, size=18, light_color="#1E293B", dark_color="#F8FAFC"):
    """
    Retorna un CTkImage fresco creado sobre el intérprete Tkinter activo,
    reutilizando las imágenes base de Pillow cacheadas en memoria.
    """
    key = (name, size, light_color, dark_color)
    if key not in _pil_cache:
        def to_rgba(hex_str):
            hex_str = hex_str.lstrip("#")
            return (int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16), 255)

        img_light = _render_pil(name, size, to_rgba(light_color))
        img_dark = _render_pil(name, size, to_rgba(dark_color))
        _pil_cache[key] = (img_light, img_dark)

    img_light, img_dark = _pil_cache[key]
    return ctk.CTkImage(light_image=img_light, dark_image=img_dark, size=(size, size))
