---
name: nuevo-modulo
description: Agrega un módulo/algoritmo nuevo a la app de Graficación (p. ej. elipse, transformaciones 2D, recorte, Bresenham de líneas) con su lógica en core/, su página en pages/, su entrada en el menú y sus pruebas. Usar cuando se pida "agregar", "crear" o "implementar" una página o algoritmo nuevo.
---

# Agregar un módulo nuevo

Sigue estos pasos en orden. Usa `pages/triangulo.py` como plantilla de página (es la más
simple con tarjetas + plano + tablas); no hace falta leer las otras páginas.

## 1. Lógica en `core/<modulo>.py`

- Solo `math`/`fractions` y otros `core/*`; **sin** `customtkinter`, `tkinter` ni `matplotlib`.
- Reutiliza `core/recta.py`: `generar_puntos_trayectoria`, `rasterizar_pixeles`,
  `redondear_pixel`, `clasificar_recta`, `calcular_limite`.
- Expón `analizar_<modulo>(...) -> dict` con todo lo que mostrará la página (métricas,
  pasos para tablas, píxeles, `"limit"` para el plano). Las validaciones con mensaje al
  usuario se quedan en la página; ofrece aquí funciones booleanas (p. ej. `vertices_coinciden`).

## 2. Pruebas rápidas en `tests/test_core_<modulo>.py`

- Casos del documento del profesor (los PDF están en `docs/`, léelos solo si hace falta un dato).
- Corre: `.venv/Scripts/python.exe -m unittest discover -s tests -p "test_core_*.py"`.

## 3. Página en `pages/<modulo>.py`

Esqueleto (todo viene de `ui/`):

```python
from tkinter import messagebox
import customtkinter as ctk

from core.<modulo> import analizar_<modulo>
from ui.plano import anotar_punto, aplicar_vista, crear_plano, dibujar_leyenda, setup_ejes
from ui.tema import es_oscuro, register_plot_updater
from ui.widgets import (ALTURA_GRAFICA, TileMetrica, botones_calcular_limpiar, contenido_tabla,
                        crear_pagina, encabezado_grafica, escribir_valores, grupo_entradas,
                        leer_numeros, tarjeta, tarjeta_metricas)

current_<modulo>_data = {}

def render_<modulo>_plot(ax, figure, canvas, view=None):
    is_dark = es_oscuro()
    ax.clear()
    setup_ejes(ax, figure, limit=current_<modulo>_data.get("limit", 10), is_dark=is_dark)
    if current_<modulo>_data.get("has_data"):
        ...  # ax.plot / LineCollection / anotar_punto(...)
        dibujar_leyenda(ax, is_dark)
    aplicar_vista(ax, view)
    figure.tight_layout()
    canvas.draw()

def create_<modulo>_page(container):
    page, body = crear_pagina(container, "Título", "Subtítulo")
    form_card = tarjeta(body); form_card.pack(fill="x", padx=20, pady=(0, 8))
    form_top = ctk.CTkFrame(form_card, fg_color="transparent"); form_top.pack(fill="x", padx=16, pady=8)
    entradas = grupo_entradas(form_top, "Punto A", ("X₁:", "Y₁:"))
    botones_calcular_limpiar(form_top, "  Calcular", lambda: calculate(), lambda: clear())
    metrics_card = tarjeta_metricas(body)
    tile = TileMetrica(metrics_card, 0, "TÍTULO", "Detalle 1: --", "Detalle 2: --")
    graph_card = tarjeta(body, height=ALTURA_GRAFICA); graph_card.pack(fill="x", padx=20, pady=(0, 12))
    graph_card.pack_propagate(False)
    encabezado_grafica(graph_card, "  Visualizador", "grid-dots", lambda: restablecer_vista())
    figure, ax, canvas = crear_plano(graph_card, body)

    def calculate():
        try:
            valores = leer_numeros(entradas)
        except ValueError:
            messagebox.showerror("Dato Inválido", "...")
            return
        datos = analizar_<modulo>(*valores)
        current_<modulo>_data.clear()
        current_<modulo>_data.update(datos, has_data=True)
        tile.mostrar(...)
        render_<modulo>_plot(ax, figure, canvas)

    def clear(): ...            # vaciar entradas, tile.limpiar(), estado.clear(), redibujar
    def restablecer_vista(): ...  # ax.set_xlim/ylim(±limit) + canvas.draw_idle()

    register_plot_updater(lambda: render_<modulo>_plot(ax, figure, canvas, view=(ax.get_xlim(), ax.get_ylim())))
    escribir_valores(entradas, (...))  # valores por defecto
    return page
```

## 4. Registro en el menú

Agrega una tupla a `PAGINAS` en `pages/index.py`:
`("<clave>", "Texto del menú", "<icono>", create_<modulo>_page)`.
El icono es `public/<icono>.svg`; si no existe, descarga el SVG de Tabler Icons (trazo, 24×24)
a `public/`. `main.py` no se toca.

## 5. Pruebas de dibujo e interfaz

- `tests/test_graficas.py`: `render_<modulo>_plot` con `FigureCanvasAgg` y estado de ejemplo.
- `tests/test_interfaz.py`: crear la página, `boton(page, "Calcular").invoke()` y revisar el estado.
- Corre la suite completa: `.venv/Scripts/python.exe -m unittest discover -s tests`.

## 6. Documentación

- `README.md`: una viñeta en "Características Principales" y el archivo en "Estructura".
- `AGENTS.md`: solo si cambian reglas o comandos (la tabla "Dónde está cada cosa" ya es genérica).
