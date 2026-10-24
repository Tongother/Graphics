"""
Página de Trazado y Análisis de Triángulos.
La lógica (métricas, clasificación, DDA de los lados y relleno) está en core/triangulo.py.
"""
from tkinter import messagebox
import customtkinter as ctk

from matplotlib.collections import LineCollection

from core.recta import redondear_pixel
from core.triangulo import LADOS, analizar_triangulo, vertices_coinciden
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

# Estado reactivo global del módulo de triángulos
current_triangle_data = {}

# Alto de la fila con las tablas de AB, BC y CA (debajo del plano)
ALTURA_TABLAS = 420

ENCABEZADO_TABLA = ["Paso", "Xₖ", "Yₖ", "Píxel"]


def render_triangle_plot(ax, figure, canvas, view=None):
    """
    Dibuja el triángulo con DDA: el relleno (líneas desde A, B y C), los lados AB, BC
    y CA uniendo sus píxeles y los vértices. view = (xlim, ylim) conserva el
    zoom y la posición actuales.
    """
    is_dark = es_oscuro()
    fill_color = "#F59E0B" if is_dark else "#D97706"  # Ámbar, como el vértice C de donde salen
    poly_edge = "#3B82F6" if is_dark else "#2563EB"
    step_pt_color = "#38BDF8" if is_dark else "#0284C7"

    col_a = "#10B981" if is_dark else "#059669"  # Esmeralda
    col_b = "#8B5CF6" if is_dark else "#7C3AED"  # Violeta
    col_c = "#F59E0B" if is_dark else "#D97706"  # Ámbar

    ax.clear()
    limit = current_triangle_data.get("limit", 10)
    setup_ejes(ax, figure, limit=limit, is_dark=is_dark)

    if current_triangle_data.get("has_data"):
        x1, y1 = current_triangle_data["x1"], current_triangle_data["y1"]
        x2, y2 = current_triangle_data["x2"], current_triangle_data["y2"]
        x3, y3 = current_triangle_data["x3"], current_triangle_data["y3"]
        area = current_triangle_data.get("area", 0)
        relleno = current_triangle_data.get("relleno", [])

        # Relleno: líneas DDA de cada vértice a cada píxel de su lado opuesto
        if relleno:
            ax.add_collection(LineCollection(
                relleno,
                colors=fill_color,
                linewidths=0.9,
                alpha=0.45,
                label=f"Relleno DDA desde A, B y C ({len(relleno)} líneas, Área: {area:.2f} u²)"
            ))

        # Lados AB, BC y CA: se unen los píxeles del DDA (escalonado al acercar)
        for i, lado in enumerate(LADOS):
            pixeles = current_triangle_data["pixeles"][lado]
            ax.plot(
                [p[0] for p in pixeles], [p[1] for p in pixeles],
                color=poly_edge,
                linewidth=2.0,
                marker="o",
                markersize=3.5,
                markerfacecolor=step_pt_color,
                markeredgecolor=step_pt_color,
                label="Lados AB, BC, CA (DDA)" if i == 0 else None
            )

        # Los vértices se marcan en su píxel (redondeado) para que queden sobre los lados
        vertices = [
            ("A", redondear_pixel(x1), redondear_pixel(y1), col_a, "o"),
            ("B", redondear_pixel(x2), redondear_pixel(y2), col_b, "s"),
            ("C", redondear_pixel(x3), redondear_pixel(y3), col_c, "^"),
        ]
        for nombre, x, y, col, marker in vertices:
            ax.plot([x], [y], marker=marker, markersize=9, color=col, linestyle="None", label=f"{nombre} ({x:g}, {y:g})")
        for nombre, x, y, col, _ in vertices:
            anotar_punto(ax, f"{nombre} ({x:g}, {y:g})", x, y, col, is_dark)

        dibujar_leyenda(ax, is_dark)

    aplicar_vista(ax, view)
    figure.tight_layout()
    canvas.draw()


def create_triangulo_page(container):
    page, body = crear_pagina(
        container,
        "Trazado y Análisis de Triángulos",
        "Ingreso de 3 vértices, cálculo de área (Gauss), perímetro, clasificación y rasterización.",
    )

    # --- 1. FORMULARIO (INPUTS DE LOS 3 VÉRTICES) ---
    form_card = tarjeta(body)
    form_card.pack(fill="x", padx=20, pady=(0, 8))

    form_top = ctk.CTkFrame(form_card, fg_color="transparent")
    form_top.pack(fill="x", padx=16, pady=8)

    entradas = (
        grupo_entradas(form_top, "Vértice A", ("X₁:", "Y₁:"), width=58, separacion=8, padx_derecho=14)
        + grupo_entradas(form_top, "Vértice B", ("X₂:", "Y₂:"), width=58, separacion=8, padx_derecho=14)
        + grupo_entradas(form_top, "Vértice C", ("X₃:", "Y₃:"), width=58, separacion=8, padx_derecho=18)
    )
    botones_calcular_limpiar(form_top, "  Calcular Triángulo", lambda: calculate(), lambda: clear())

    # --- 2. MÉTRICAS ---
    metrics_card = tarjeta_metricas(body)
    tile_area = TileMetrica(metrics_card, 0, "ÁREA Y PERÍMETRO", "Perímetro: --", "Semiperímetro: --")
    tile_class = TileMetrica(metrics_card, 1, "CLASIFICACIÓN", "Por ángulos: --", "Estado: --")
    tile_sides = TileMetrica(metrics_card, 2, "LONGITUDES DE LADOS", "d(A, B): --", "d(B, C): -- | d(C, A): --")
    tile_slopes = TileMetrica(metrics_card, 3, "PENDIENTES DE SEGMENTOS", "m_AB: -- | m_BC: --", "m_CA: --")
    tiles = (tile_area, tile_class, tile_sides, tile_slopes)

    # Franja: caso DDA de cada lado con su notación (ocupa las 4 columnas)
    tile_casos = ctk.CTkFrame(metrics_card, corner_radius=10, fg_color=FONDO_TILE)
    tile_casos.grid(row=1, column=0, columnspan=4, sticky="nsew", padx=6, pady=(0, 8))
    casos_labels = {}
    for fila, lado in enumerate(LADOS):
        pad_y = (6 if fila == 0 else 0, 6 if fila == 2 else 0)
        ctk.CTkLabel(tile_casos, text=f"LÍNEA {lado}", height=22, font=ctk.CTkFont(size=9, weight="bold"), text_color="gray", anchor="w").grid(row=fila, column=0, sticky="w", padx=(12, 10), pady=pad_y)
        val_caso = ctk.CTkLabel(tile_casos, text="--", height=22, font=ctk.CTkFont(size=12, weight="bold"), anchor="w")
        val_caso.grid(row=fila, column=1, sticky="w", pady=pad_y)
        val_detalle = ctk.CTkLabel(tile_casos, text="", height=22, font=ctk.CTkFont(size=10), text_color=TEXTO_SECUNDARIO, anchor="w")
        val_detalle.grid(row=fila, column=2, sticky="w", padx=(12, 12), pady=pad_y)
        val_notacion = ctk.CTkLabel(tile_casos, text="", height=22, font=ctk.CTkFont(size=11), anchor="w")
        val_notacion.grid(row=fila, column=3, sticky="w", padx=(0, 12), pady=pad_y)
        casos_labels[lado] = (val_caso, val_detalle, val_notacion)

    # --- 3. PLANO CARTESIANO (ancho completo) ---
    split_box = ctk.CTkFrame(body, height=ALTURA_GRAFICA, corner_radius=0, fg_color="transparent")
    split_box.pack(fill="x", padx=20, pady=(0, 12))
    split_box.pack_propagate(False)

    graph_card = tarjeta(split_box)
    graph_card.pack(side="left", fill="both", expand=True)
    encabezado_grafica(graph_card, "  Geometría 2D del Triángulo", "triangle", lambda: restablecer_vista())
    figure, ax, canvas = crear_plano(graph_card, body)

    # --- 4. TABLAS DE LAS LÍNEAS AB, BC Y CA (una por línea, como en el documento) ---
    tables_box = ctk.CTkFrame(body, height=ALTURA_TABLAS, corner_radius=0, fg_color="transparent")
    tables_box.pack(fill="x", padx=20, pady=(0, 12))
    tables_box.pack_propagate(False)
    tables_box.columnconfigure((0, 1, 2), weight=1, uniform="tabla")
    tables_box.rowconfigure(0, weight=1)

    tablas = {}
    for col, lado in enumerate(LADOS):
        table_card = tarjeta(tables_box)
        table_card.grid(row=0, column=col, sticky="nsew", padx=(0 if col == 0 else 5, 0 if col == 2 else 5))
        lbl_info, tabla = contenido_tabla(table_card, f"  Línea {lado}", "0 puntos calculados", width=60)
        tabla.mostrar([ENCABEZADO_TABLA])
        tablas[lado] = (lbl_info, tabla)

    # --- LÓGICA DE CONTROL ---
    def calculate():
        try:
            x1, y1, x2, y2, x3, y3 = leer_numeros(entradas)
        except ValueError:
            messagebox.showerror("Dato Inválido", "Por favor ingresa coordenadas numéricas válidas para los tres vértices.")
            return

        if vertices_coinciden(x1, y1, x2, y2, x3, y3):
            messagebox.showwarning(
                "Vértices Coincidentes",
                "Al menos dos de los vértices tienen exactamente las mismas coordenadas.\n"
                "Para formar un triángulo los tres vértices deben ser distintos."
            )
            return

        datos = analizar_triangulo(x1, y1, x2, y2, x3, y3)
        current_triangle_data.clear()
        current_triangle_data.update(datos, has_data=True)

        if datos["es_colineal"]:
            messagebox.showwarning(
                "Puntos Colineales",
                "Los tres puntos ingresados están sobre la misma línea recta (Área = 0).\n"
                "No forman un triángulo con superficie, sino un segmento colineal."
            )

        d_ab, d_bc, d_ca = datos["d_ab"], datos["d_bc"], datos["d_ca"]
        tile_area.mostrar(
            f"{datos['area']:.2f} u²",
            f"Perímetro: {datos['perimetro']:.2f} u",
            f"Semiperímetro: {datos['semiperimetro']:.2f} u",
        )
        tile_class.mostrar(datos["tipo_lados"], f"Por ángulos: {datos['tipo_angulos']}", f"Estado: {datos['estado_texto']}")
        tile_sides.mostrar(
            f"L_máx: {max(d_ab, d_bc, d_ca):.2f} u",
            f"d(A, B) = {d_ab:.2f} u",
            f"d(B, C): {d_bc:.2f} | d(C, A): {d_ca:.2f}",
        )
        tile_slopes.mostrar(f"m_AB = {datos['str_m_ab']}", f"m_BC: {datos['str_m_bc']}", f"m_CA: {datos['str_m_ca']}")

        for lado, (val_caso, val_detalle, val_notacion) in casos_labels.items():
            caso, detalle, notacion = datos["casos"][lado]
            val_caso.configure(text=caso)
            val_detalle.configure(text=detalle)
            val_notacion.configure(text=notacion)

        # Tabla de cada línea: valores con decimales y el píxel redondeado
        for lado, (xa, ya, xb, yb) in datos["lados"].items():
            pasos = datos["pasos"][lado]
            filas = [list(ENCABEZADO_TABLA)]
            for paso, px, py in pasos:
                filas.append([str(paso), f"{px:.2f}", f"{py:.2f}", f"({redondear_pixel(px)}, {redondear_pixel(py)})"])
            lbl_info, tabla = tablas[lado]
            tabla.mostrar(filas)
            ini, fin = lado
            lbl_info.configure(text=f"{ini}({xa:g}, {ya:g}) → {fin}({xb:g}, {yb:g}) · {len(pasos)} puntos calculados")

        render_triangle_plot(ax, figure, canvas)

    def clear():
        for entry in entradas:
            entry.delete(0, "end")
        for tile in tiles:
            tile.limpiar()

        for val_caso, val_detalle, val_notacion in casos_labels.values():
            val_caso.configure(text="--")
            val_detalle.configure(text="")
            val_notacion.configure(text="")

        for lbl_info, tabla in tablas.values():
            tabla.mostrar([ENCABEZADO_TABLA])
            lbl_info.configure(text="0 puntos calculados")
        current_triangle_data.clear()

        render_triangle_plot(ax, figure, canvas)
        entradas[0].focus_set()

    def update_plot():
        # Cambio de tema: se conserva el zoom y la posición que dejó el usuario
        render_triangle_plot(ax, figure, canvas, view=(ax.get_xlim(), ax.get_ylim()))

    def restablecer_vista():
        limit = current_triangle_data.get("limit", 10)
        ax.set_xlim(-limit, limit)
        ax.set_ylim(-limit, limit)
        canvas.draw_idle()

    register_plot_updater(update_plot)

    # Valores por defecto para visualización inmediata
    escribir_valores(entradas, (1, 1, 7, 2, 3, 7))

    return page
