"""
Página de Puntos Colineales: recta entre A y B trazada con DDA.
La lógica (pendiente, casos, trayectoria) está en core/recta.py.
"""
from tkinter import messagebox
import customtkinter as ctk

from core.recta import analizar_recta, rasterizar_pixeles, redondear_pixel
from ui.plano import anotar_punto, aplicar_vista, crear_plano, dibujar_leyenda, setup_ejes
from ui.tema import es_oscuro, register_plot_updater
from ui.widgets import (
    ALTURA_GRAFICA,
    FONDO_TILE,
    TEXTO_SECUNDARIO,
    TileMetrica,
    botones_calcular_limpiar,
    contenido_tabla,
    crear_pagina,
    encabezado_grafica,
    escribir_valores,
    grupo_entradas,
    leer_numeros,
    tarjeta,
    tarjeta_metricas,
)

# Almacenamiento de datos actuales para repintado reactivo
current_data = {}

ENCABEZADO_TABLA = ["Paso", "Xₖ", "Yₖ", "Píxel"]


def render_plot(ax, figure, canvas, view=None):
    """Redibuja el plano; view = (xlim, ylim) conserva el zoom y la posición actuales."""
    is_dark = es_oscuro()
    line_color = "#3B82F6" if is_dark else "#2563EB"
    pt_color = "#38BDF8" if is_dark else "#0284C7"
    pt_a_color = "#34D399" if is_dark else "#059669"
    pt_b_color = "#A78BFA" if is_dark else "#7C3AED"

    ax.clear()
    limit = current_data.get("limit", 10)
    setup_ejes(ax, figure, limit=limit, is_dark=is_dark)

    if current_data.get("has_data"):
        table_points = current_data["table_points"]
        x1, y1 = current_data["x1"], current_data["y1"]
        x2, y2 = current_data["x2"], current_data["y2"]
        equation = current_data["equation"]
        mismo_punto = (x1 == x2 and y1 == y2)

        # Recta trazada con DDA: se unen los píxeles redondeados, por eso al
        # acercar el plano se ve el escalonado (sierra) propio del método
        if not mismo_punto:
            pixeles = rasterizar_pixeles(table_points)
            ax.plot(
                [p[0] for p in pixeles], [p[1] for p in pixeles],
                color=line_color,
                linewidth=2.0,
                marker="o",
                markersize=4,
                markerfacecolor=pt_color,
                markeredgecolor=pt_color,
                label=f"Recta DDA: {equation}"
            )

        # A y B se marcan en su píxel (redondeado) para que queden sobre la recta DDA
        x1, y1, x2, y2 = (redondear_pixel(v) for v in (x1, y1, x2, y2))

        # Punto A y Punto B (si coinciden se dibuja uno solo)
        texto_a = f"A = B ({x1:g}, {y1:g})" if mismo_punto else f"A ({x1:g}, {y1:g})"
        ax.plot([x1], [y1], marker="o", markersize=9, color=pt_a_color, linestyle="None", label=texto_a)
        anotar_punto(ax, texto_a, x1, y1, pt_a_color, is_dark)
        if not mismo_punto:
            texto_b = f"B ({x2:g}, {y2:g})"
            ax.plot([x2], [y2], marker="s", markersize=9, color=pt_b_color, linestyle="None", label=texto_b)
            anotar_punto(ax, texto_b, x2, y2, pt_b_color, is_dark)

        dibujar_leyenda(ax, is_dark)

    aplicar_vista(ax, view)
    figure.tight_layout()
    canvas.draw()


def create_puntos_colineales_page(container):
    page, body = crear_pagina(
        container,
        "Trazado y Análisis de Rectas",
        "Cálculo algebraico de pendiente, vector director y rasterización discreta.",
    )

    # --- 1. FORMULARIO (INPUTS) ---
    form_card = tarjeta(body)
    form_card.pack(fill="x", padx=20, pady=(0, 8))

    form_top = ctk.CTkFrame(form_card, fg_color="transparent")
    form_top.pack(fill="x", padx=16, pady=8)

    entradas = (
        grupo_entradas(form_top, "Punto A (Origen)", ("X₁:", "Y₁:"))
        + grupo_entradas(form_top, "Punto B (Destino)", ("X₂:", "Y₂:"), padx_derecho=20)
    )
    botones_calcular_limpiar(form_top, "  Calcular Trayectoria", lambda: calculate(), lambda: clear())

    # --- 2. MÉTRICAS ---
    metrics_card = tarjeta_metricas(body)
    tile_m = TileMetrica(metrics_card, 0, "PENDIENTE (m)", "Comportamiento: --", "Ángulo: --")
    tile_eq = TileMetrica(metrics_card, 1, "ECUACIÓN DE LA RECTA", "Ordenada (b): --", "Forma: Explícita")
    tile_dx = TileMetrica(metrics_card, 2, "INCREMENTO X (ΔX)", "Sentido: --", "Magnitud: --")
    tile_dy = TileMetrica(metrics_card, 3, "INCREMENTO Y (ΔY)", "Sentido: --", "Magnitud: --")
    tiles = (tile_m, tile_eq, tile_dx, tile_dy)

    # Franja: caso de trazo detectado y su notación (ocupa las 4 columnas)
    tile_caso = ctk.CTkFrame(metrics_card, corner_radius=10, fg_color=FONDO_TILE)
    tile_caso.grid(row=1, column=0, columnspan=4, sticky="nsew", padx=6, pady=(0, 8))
    ctk.CTkLabel(tile_caso, text="CASO DETECTADO", height=22, font=ctk.CTkFont(size=9, weight="bold"), text_color="gray", anchor="w").grid(row=0, column=0, sticky="w", padx=(12, 10), pady=(6, 0))
    val_caso = ctk.CTkLabel(tile_caso, text="--", height=22, font=ctk.CTkFont(size=13, weight="bold"), anchor="w")
    val_caso.grid(row=0, column=1, sticky="w", pady=(6, 0))
    val_caso_sub = ctk.CTkLabel(tile_caso, text="", height=22, font=ctk.CTkFont(size=10), text_color=TEXTO_SECUNDARIO, anchor="w")
    val_caso_sub.grid(row=0, column=2, sticky="w", padx=(12, 12), pady=(6, 0))
    ctk.CTkLabel(tile_caso, text="NOTACIÓN", height=22, font=ctk.CTkFont(size=9, weight="bold"), text_color="gray", anchor="w").grid(row=1, column=0, sticky="w", padx=(12, 10), pady=(0, 6))
    val_notacion = ctk.CTkLabel(tile_caso, text="--", height=22, font=ctk.CTkFont(size=12), anchor="w")
    val_notacion.grid(row=1, column=1, columnspan=2, sticky="w", pady=(0, 6))

    # --- 3. TABLA Y PLANO ---
    split_box = ctk.CTkFrame(body, height=ALTURA_GRAFICA, corner_radius=0, fg_color="transparent")
    split_box.pack(fill="x", padx=20, pady=(0, 12))
    split_box.pack_propagate(False)

    table_card = tarjeta(split_box, width=330)
    table_card.pack(side="left", fill="y", padx=(0, 10))
    table_card.pack_propagate(False)
    tbl_count, tabla = contenido_tabla(table_card, "  Puntos Discretos", "0 pasos calculados")
    tabla.mostrar([ENCABEZADO_TABLA])

    graph_card = tarjeta(split_box)
    graph_card.pack(side="left", fill="both", expand=True)
    encabezado_grafica(graph_card, "  Visualizador Geométrico", "grid-dots", lambda: restablecer_vista())
    figure, ax, canvas = crear_plano(graph_card, body)

    # --- LÓGICA DE CONTROL ---
    def calculate():
        try:
            x1, y1, x2, y2 = leer_numeros(entradas)
        except ValueError:
            messagebox.showerror("Dato Inválido", "Por favor ingresa coordenadas numéricas válidas.")
            return

        datos = analizar_recta(x1, y1, x2, y2)
        current_data.clear()
        current_data.update(datos, has_data=True)

        pendiente, ordenada, angulo = datos["pendiente"], datos["ordenada"], datos["angulo"]
        delta_x, delta_y = datos["delta_x"], datos["delta_y"]

        tile_m.mostrar(
            f"{pendiente:g}" if pendiente is not None else "Indefinida",
            f"Sentido: {datos['comportamiento']}",
            f"Ángulo: {angulo:.1f}°" if angulo is not None else "Ángulo: --",
        )

        if ordenada is not None:
            sub_eq = (f"Ordenada (b): {ordenada:g}", "Forma: y = mx + b")
        elif delta_y != 0:
            sub_eq = ("Ordenada (b): no existe", "Forma: x = constante")
        else:
            sub_eq = ("Ordenada (b): no existe", "Forma: punto aislado")
        tile_eq.mostrar(datos["equation"], *sub_eq)

        tile_dx.mostrar(
            f"{delta_x:+g}" if delta_x != 0 else "0",
            f"Sentido: {datos['dir_x']}",
            f"Magnitud: |ΔX| = {abs(delta_x):g}",
        )
        tile_dy.mostrar(
            f"{delta_y:+g}" if delta_y != 0 else "0",
            f"Sentido: {datos['dir_y']}",
            f"Magnitud: |ΔY| = {abs(delta_y):g}",
        )

        val_caso.configure(text=datos["caso"])
        val_caso_sub.configure(text=datos["caso_detalle"])
        val_notacion.configure(text=datos["notacion"])

        # Tabla: valores con decimales y el píxel redondeado que les corresponde
        filas = [list(ENCABEZADO_TABLA)]
        for paso, px, py in datos["table_points"]:
            filas.append([str(paso), f"{px:.2f}", f"{py:.2f}", f"({redondear_pixel(px)}, {redondear_pixel(py)})"])
        tabla.mostrar(filas)
        tbl_count.configure(text=f"{len(datos['table_points'])} puntos calculados")

        render_plot(ax, figure, canvas)

    def clear():
        for entry in entradas:
            entry.delete(0, "end")
        for tile in tiles:
            tile.limpiar()

        val_caso.configure(text="--")
        val_caso_sub.configure(text="")
        val_notacion.configure(text="--")

        tabla.mostrar([ENCABEZADO_TABLA])
        tbl_count.configure(text="0 pasos calculados")
        current_data.clear()

        render_plot(ax, figure, canvas)
        entradas[0].focus_set()

    def update_plot():
        # Cambio de tema: se conserva el zoom y la posición que dejó el usuario
        render_plot(ax, figure, canvas, view=(ax.get_xlim(), ax.get_ylim()))

    def restablecer_vista():
        limit = current_data.get("limit", 10)
        ax.set_xlim(-limit, limit)
        ax.set_ylim(-limit, limit)
        canvas.draw_idle()

    register_plot_updater(update_plot)

    # Valores iniciales para facilitar la visualización inmediata
    escribir_valores(entradas, (1, 2, 5, 8))

    return page
