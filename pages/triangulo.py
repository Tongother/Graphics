"""
Módulo de Trazado y Análisis de Triángulos.
Cálculo de métricas geométricas (área, perímetro, longitudes, pendientes),
clasificación por lados y ángulos, trazo de los lados AB, BC y CA con DDA,
relleno con líneas DDA desde cada vértice fijo hacia el lado opuesto y renderizado
con Matplotlib.
"""
import math
from tkinter import messagebox
import customtkinter as ctk
from CTkTable import CTkTable

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.collections import LineCollection
from matplotlib.figure import Figure

from pages.icons import get_icon
from pages.puntos_colineales import (
    ALTURA_GRAFICA,
    PaginaDesplazable,
    clasificar_recta,
    generar_puntos_trayectoria,
    habilitar_navegacion,
    rasterizar_pixeles,
    redondear_pixel,
    register_plot_updater,
    setup_ejes,
)

# Estado reactivo global del módulo de triángulos
current_triangle_data = {}

# Alto de la fila con las tablas de AB, BC y CA (debajo del plano)
ALTURA_TABLAS = 420


def distancia_euclidiana(x1, y1, x2, y2):
    """Calcula la distancia euclidiana entre dos puntos 2D."""
    return math.hypot(x2 - x1, y2 - y1)


def calcular_area_triangulo(x1, y1, x2, y2, x3, y3):
    """
    Calcula el área del triángulo usando la fórmula del determinante de Gauss (Shoelace).
    Retorna el área no negativa.
    """
    area = 0.5 * abs(x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))
    return area


def calcular_perimetro_triangulo(d_ab, d_bc, d_ca):
    """Suma las tres longitudes de lado."""
    return d_ab + d_bc + d_ca


def clasificar_por_lados(d_ab, d_bc, d_ca, tol=1e-4):
    """Clasifica el triángulo en Equilátero, Isósceles o Escaleno."""
    eq_ab_bc = abs(d_ab - d_bc) < tol
    eq_bc_ca = abs(d_bc - d_ca) < tol
    eq_ca_ab = abs(d_ca - d_ab) < tol

    if eq_ab_bc and eq_bc_ca and eq_ca_ab:
        return "Equilátero"
    elif eq_ab_bc or eq_bc_ca or eq_ca_ab:
        return "Isósceles"
    return "Escaleno"


def clasificar_por_angulos(d_ab, d_bc, d_ca, tol=1e-3):
    """
    Clasifica el triángulo según sus ángulos internos:
    Rectángulo (a² + b² = c²), Acutángulo (a² + b² > c²), u Obtusángulo (a² + b² < c²).
    """
    s1, s2, s3 = sorted([d_ab, d_bc, d_ca])
    diff = (s1**2 + s2**2) - s3**2

    if abs(diff) < tol:
        return "Rectángulo"
    elif diff > 0:
        return "Acutángulo"
    else:
        return "Obtusángulo"


def calcular_pendiente_segura(x1, y1, x2, y2):
    """Calcula la pendiente m entre dos puntos, manejando rectas verticales."""
    if x2 == x1:
        return None, "Vertical (indefinida)"
    m = (y2 - y1) / (x2 - x1)
    return m, f"{m:g}"


def generar_relleno(xc, yc, pixeles_ab):
    """
    Relleno del triángulo con el método del documento: C queda como punto fijo
    y, en un ciclo que se repite N veces (N = puntos de la tabla de AB), se
    traza con DDA la línea de C a cada píxel de AB. La misma función sirve con
    cualquier vértice fijo y los píxeles de su lado opuesto.
    Retorna una lista de líneas, cada una como lista de píxeles (x, y).
    """
    return [
        rasterizar_pixeles(generar_puntos_trayectoria(xc, yc, px, py))
        for px, py in pixeles_ab
    ]


def ajustar_al_contorno(relleno, pixeles_lados):
    """
    Mantiene el relleno dentro del triángulo. Cuando una línea de relleno es casi
    paralela a un lado, el redondeo del DDA puede dejar un píxel fuera del borde;
    en cada fila Y, ese píxel se recorre hasta el píxel del borde de esa fila.
    """
    limites = {}
    for pixeles in pixeles_lados:
        for x, y in pixeles:
            izq, der = limites.get(y, (x, x))
            limites[y] = (min(izq, x), max(der, x))

    ajustado = []
    for linea in relleno:
        nueva = []
        for x, y in linea:
            izq, der = limites.get(y, (x, x))
            nueva.append((min(max(x, izq), der), y))
        ajustado.append(nueva)
    return ajustado


def render_triangle_plot(ax, figure, canvas, view=None):
    """
    Dibuja el triángulo con DDA: el relleno (líneas desde A, B y C), los lados AB, BC
    y CA uniendo sus píxeles y los vértices. view = (xlim, ylim) conserva el
    zoom y la posición actuales.
    """
    is_dark = (ctk.get_appearance_mode().lower() == "dark")
    fig_bg = "#2B2B2B" if is_dark else "#F2F2F2"
    border_color = "#444444" if is_dark else "#D0D0D0"
    text_color = "#E0E0E0" if is_dark else "#1A1A1A"

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
        for i, lado in enumerate(("AB", "BC", "CA")):
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
        x1, y1, x2, y2, x3, y3 = (redondear_pixel(v) for v in (x1, y1, x2, y2, x3, y3))

        # Vértices destacados
        ax.plot([x1], [y1], marker="o", markersize=9, color=col_a, linestyle="None", label=f"A ({x1:g}, {y1:g})")
        ax.plot([x2], [y2], marker="s", markersize=9, color=col_b, linestyle="None", label=f"B ({x2:g}, {y2:g})")
        ax.plot([x3], [y3], marker="^", markersize=9, color=col_c, linestyle="None", label=f"C ({x3:g}, {y3:g})")

        # Anotaciones con recuadros
        def annotate_pt(name, x, y, col):
            bbox_props = dict(boxstyle="round,pad=0.35", fc=fig_bg, ec=col, lw=1.2, alpha=0.95)
            ax.annotate(
                f"{name} ({x:g}, {y:g})",
                (x, y),
                textcoords="offset points",
                xytext=(0, 14),
                ha="center",
                fontsize=9,
                fontweight="bold",
                color=col,
                bbox=bbox_props
            )

        annotate_pt("A", x1, y1, col_a)
        annotate_pt("B", x2, y2, col_b)
        annotate_pt("C", x3, y3, col_c)

        # Leyenda
        legend = ax.legend(
            loc="best",
            fontsize=8.5,
            framealpha=0.88,
            facecolor=fig_bg,
            edgecolor=border_color
        )
        for text in legend.get_texts():
            text.set_color(text_color)

    if view is not None:
        ax.set_xlim(view[0])
        ax.set_ylim(view[1])

    figure.tight_layout()
    canvas.draw()


def create_triangulo_page(container):
    page = ctk.CTkFrame(container, corner_radius=0, fg_color="transparent")
    body = PaginaDesplazable(page, corner_radius=0, fg_color="transparent")
    body.pack(fill="both", expand=True)

    # --- 1. ENCABEZADO ---
    header_frame = ctk.CTkFrame(body, corner_radius=0, fg_color="transparent")
    header_frame.pack(fill="x", padx=20, pady=(12, 4))

    lbl_title = ctk.CTkLabel(
        header_frame,
        text="Trazado y Análisis de Triángulos",
        font=ctk.CTkFont(size=20, weight="bold"),
        anchor="w"
    )
    lbl_title.pack(anchor="w")

    lbl_subtitle = ctk.CTkLabel(
        header_frame,
        text="Ingreso de 3 vértices, cálculo de área (Gauss), perímetro, clasificación y rasterización.",
        font=ctk.CTkFont(size=12),
        text_color="gray",
        anchor="w"
    )
    lbl_subtitle.pack(anchor="w", pady=(2, 0))

    # --- 2. TARJETA DE FORMULARIO (INPUTS DE LOS 3 VÉRTICES) ---
    form_card = ctk.CTkFrame(body, corner_radius=12, border_width=1, border_color=("gray85", "gray25"))
    form_card.pack(fill="x", padx=20, pady=(0, 8))

    form_top = ctk.CTkFrame(form_card, fg_color="transparent")
    form_top.pack(fill="x", padx=16, pady=8)

    # Vértice A
    box_a = ctk.CTkFrame(form_top, fg_color="transparent")
    box_a.pack(side="left", padx=(0, 14))

    lbl_pt_a = ctk.CTkLabel(box_a, text="Vértice A", font=ctk.CTkFont(size=12, weight="bold"))
    lbl_pt_a.grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 4))

    lbl_xa = ctk.CTkLabel(box_a, text="X₁:", font=ctk.CTkFont(size=12))
    lbl_xa.grid(row=1, column=0, padx=(0, 4))
    entryXA = ctk.CTkEntry(box_a, width=58, height=32, corner_radius=6, justify="center")
    entryXA.grid(row=1, column=1, padx=(0, 8))

    lbl_ya = ctk.CTkLabel(box_a, text="Y₁:", font=ctk.CTkFont(size=12))
    lbl_ya.grid(row=1, column=2, padx=(0, 4))
    entryYA = ctk.CTkEntry(box_a, width=58, height=32, corner_radius=6, justify="center")
    entryYA.grid(row=1, column=3)

    # Vértice B
    box_b = ctk.CTkFrame(form_top, fg_color="transparent")
    box_b.pack(side="left", padx=(0, 14))

    lbl_pt_b = ctk.CTkLabel(box_b, text="Vértice B", font=ctk.CTkFont(size=12, weight="bold"))
    lbl_pt_b.grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 4))

    lbl_xb = ctk.CTkLabel(box_b, text="X₂:", font=ctk.CTkFont(size=12))
    lbl_xb.grid(row=1, column=0, padx=(0, 4))
    entryXB = ctk.CTkEntry(box_b, width=58, height=32, corner_radius=6, justify="center")
    entryXB.grid(row=1, column=1, padx=(0, 8))

    lbl_yb = ctk.CTkLabel(box_b, text="Y₂:", font=ctk.CTkFont(size=12))
    lbl_yb.grid(row=1, column=2, padx=(0, 4))
    entryYB = ctk.CTkEntry(box_b, width=58, height=32, corner_radius=6, justify="center")
    entryYB.grid(row=1, column=3)

    # Vértice C
    box_c = ctk.CTkFrame(form_top, fg_color="transparent")
    box_c.pack(side="left", padx=(0, 18))

    lbl_pt_c = ctk.CTkLabel(box_c, text="Vértice C", font=ctk.CTkFont(size=12, weight="bold"))
    lbl_pt_c.grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 4))

    lbl_xc = ctk.CTkLabel(box_c, text="X₃:", font=ctk.CTkFont(size=12))
    lbl_xc.grid(row=1, column=0, padx=(0, 4))
    entryXC = ctk.CTkEntry(box_c, width=58, height=32, corner_radius=6, justify="center")
    entryXC.grid(row=1, column=1, padx=(0, 8))

    lbl_yc = ctk.CTkLabel(box_c, text="Y₃:", font=ctk.CTkFont(size=12))
    lbl_yc.grid(row=1, column=2, padx=(0, 4))
    entryYC = ctk.CTkEntry(box_c, width=58, height=32, corner_radius=6, justify="center")
    entryYC.grid(row=1, column=3)

    # Acciones con Iconos Vectoriales
    actions_box = ctk.CTkFrame(form_top, fg_color="transparent")
    actions_box.pack(side="left", fill="y", padx=4)

    icon_play = get_icon("player-play", size=15, light_color="#FFFFFF", dark_color="#FFFFFF")
    btn_calc = ctk.CTkButton(
        actions_box,
        text="  Calcular Triángulo",
        image=icon_play,
        compound="left",
        height=34,
        corner_radius=8,
        font=ctk.CTkFont(size=12, weight="bold"),
        command=lambda: calculate()
    )
    btn_calc.pack(side="left", padx=(0, 8), pady=6)

    icon_clear = get_icon("rotate", size=15, light_color="#1E293B", dark_color="#F8FAFC")
    btn_clear = ctk.CTkButton(
        actions_box,
        text="  Limpiar",
        image=icon_clear,
        compound="left",
        height=34,
        corner_radius=8,
        fg_color="transparent",
        border_width=1,
        border_color=("gray70", "gray40"),
        text_color=("gray20", "gray85"),
        font=ctk.CTkFont(size=12),
        command=lambda: clear()
    )
    btn_clear.pack(side="left", pady=6)

    # --- 3. TARJETA DE MÉTRICAS (4 TILES BIEN SEPARADAS) ---
    metrics_card = ctk.CTkFrame(body, corner_radius=12, border_width=1, border_color=("gray85", "gray25"))
    metrics_card.pack(fill="x", padx=20, pady=(0, 8))
    metrics_card.columnconfigure((0, 1, 2, 3), weight=1, uniform="stat")

    # Tile 1: Área y Perímetro
    tile_area = ctk.CTkFrame(metrics_card, corner_radius=10, fg_color=("gray92", "gray20"))
    tile_area.grid(row=0, column=0, sticky="nsew", padx=6, pady=8)
    ctk.CTkLabel(tile_area, text="ÁREA Y PERÍMETRO", font=ctk.CTkFont(size=9, weight="bold"), text_color="gray", anchor="w").pack(anchor="w", padx=12, pady=(6, 0))
    val_area_num = ctk.CTkLabel(tile_area, text="--", font=ctk.CTkFont(size=17, weight="bold"), anchor="w")
    val_area_num.pack(anchor="w", padx=12, pady=(1, 0))
    val_perim_sub = ctk.CTkLabel(tile_area, text="Perímetro: --", font=ctk.CTkFont(size=10), text_color=("gray30", "gray70"), anchor="w")
    val_perim_sub.pack(anchor="w", padx=12)
    val_semi_sub = ctk.CTkLabel(tile_area, text="Semiperímetro: --", font=ctk.CTkFont(size=10), text_color=("gray30", "gray70"), anchor="w")
    val_semi_sub.pack(anchor="w", padx=12, pady=(0, 6))

    # Tile 2: Clasificación
    tile_class = ctk.CTkFrame(metrics_card, corner_radius=10, fg_color=("gray92", "gray20"))
    tile_class.grid(row=0, column=1, sticky="nsew", padx=6, pady=8)
    ctk.CTkLabel(tile_class, text="CLASIFICACIÓN", font=ctk.CTkFont(size=9, weight="bold"), text_color="gray", anchor="w").pack(anchor="w", padx=12, pady=(6, 0))
    val_class_num = ctk.CTkLabel(tile_class, text="--", font=ctk.CTkFont(size=17, weight="bold"), anchor="w")
    val_class_num.pack(anchor="w", padx=12, pady=(1, 0))
    val_ang_sub = ctk.CTkLabel(tile_class, text="Por ángulos: --", font=ctk.CTkFont(size=10), text_color=("gray30", "gray70"), anchor="w")
    val_ang_sub.pack(anchor="w", padx=12)
    val_status_sub = ctk.CTkLabel(tile_class, text="Estado: --", font=ctk.CTkFont(size=10), text_color=("gray30", "gray70"), anchor="w")
    val_status_sub.pack(anchor="w", padx=12, pady=(0, 6))

    # Tile 3: Longitudes de Lados
    tile_sides = ctk.CTkFrame(metrics_card, corner_radius=10, fg_color=("gray92", "gray20"))
    tile_sides.grid(row=0, column=2, sticky="nsew", padx=6, pady=8)
    ctk.CTkLabel(tile_sides, text="LONGITUDES DE LADOS", font=ctk.CTkFont(size=9, weight="bold"), text_color="gray", anchor="w").pack(anchor="w", padx=12, pady=(6, 0))
    val_sides_num = ctk.CTkLabel(tile_sides, text="--", font=ctk.CTkFont(size=17, weight="bold"), anchor="w")
    val_sides_num.pack(anchor="w", padx=12, pady=(1, 0))
    val_ab_sub = ctk.CTkLabel(tile_sides, text="d(A, B): --", font=ctk.CTkFont(size=10), text_color=("gray30", "gray70"), anchor="w")
    val_ab_sub.pack(anchor="w", padx=12)
    val_bcca_sub = ctk.CTkLabel(tile_sides, text="d(B, C): -- | d(C, A): --", font=ctk.CTkFont(size=10), text_color=("gray30", "gray70"), anchor="w")
    val_bcca_sub.pack(anchor="w", padx=12, pady=(0, 6))

    # Tile 4: Pendientes de Lados
    tile_slopes = ctk.CTkFrame(metrics_card, corner_radius=10, fg_color=("gray92", "gray20"))
    tile_slopes.grid(row=0, column=3, sticky="nsew", padx=6, pady=8)
    ctk.CTkLabel(tile_slopes, text="PENDIENTES DE SEGMENTOS", font=ctk.CTkFont(size=9, weight="bold"), text_color="gray", anchor="w").pack(anchor="w", padx=12, pady=(6, 0))
    val_slopes_num = ctk.CTkLabel(tile_slopes, text="--", font=ctk.CTkFont(size=17, weight="bold"), anchor="w")
    val_slopes_num.pack(anchor="w", padx=12, pady=(1, 0))
    val_mab_sub = ctk.CTkLabel(tile_slopes, text="m_AB: -- | m_BC: --", font=ctk.CTkFont(size=10), text_color=("gray30", "gray70"), anchor="w")
    val_mab_sub.pack(anchor="w", padx=12)
    val_mca_sub = ctk.CTkLabel(tile_slopes, text="m_CA: --", font=ctk.CTkFont(size=10), text_color=("gray30", "gray70"), anchor="w")
    val_mca_sub.pack(anchor="w", padx=12, pady=(0, 6))

    # Franja: caso DDA de cada lado con su notación (ocupa las 4 columnas)
    tile_casos = ctk.CTkFrame(metrics_card, corner_radius=10, fg_color=("gray92", "gray20"))
    tile_casos.grid(row=1, column=0, columnspan=4, sticky="nsew", padx=6, pady=(0, 8))
    casos_labels = {}
    for fila, lado in enumerate(("AB", "BC", "CA")):
        pad_y = (6 if fila == 0 else 0, 6 if fila == 2 else 0)
        ctk.CTkLabel(tile_casos, text=f"LÍNEA {lado}", height=22, font=ctk.CTkFont(size=9, weight="bold"), text_color="gray", anchor="w").grid(row=fila, column=0, sticky="w", padx=(12, 10), pady=pad_y)
        val_caso = ctk.CTkLabel(tile_casos, text="--", height=22, font=ctk.CTkFont(size=12, weight="bold"), anchor="w")
        val_caso.grid(row=fila, column=1, sticky="w", pady=pad_y)
        val_detalle = ctk.CTkLabel(tile_casos, text="", height=22, font=ctk.CTkFont(size=10), text_color=("gray30", "gray70"), anchor="w")
        val_detalle.grid(row=fila, column=2, sticky="w", padx=(12, 12), pady=pad_y)
        val_notacion = ctk.CTkLabel(tile_casos, text="", height=22, font=ctk.CTkFont(size=11), anchor="w")
        val_notacion.grid(row=fila, column=3, sticky="w", padx=(0, 12), pady=pad_y)
        casos_labels[lado] = (val_caso, val_detalle, val_notacion)

    # --- 4. PLANO CARTESIANO (ancho completo) ---
    split_box = ctk.CTkFrame(body, height=ALTURA_GRAFICA, corner_radius=0, fg_color="transparent")
    split_box.pack(fill="x", padx=20, pady=(0, 12))
    split_box.pack_propagate(False)

    # B) PLANO CARTESIANO GIGANTE
    graph_card = ctk.CTkFrame(split_box, corner_radius=12, border_width=1, border_color=("gray85", "gray25"))
    graph_card.pack(side="left", fill="both", expand=True)

    grp_header = ctk.CTkFrame(graph_card, fg_color="transparent")
    grp_header.pack(fill="x", padx=14, pady=(10, 4))

    icon_grid = get_icon("triangle", size=16, light_color="#2563EB", dark_color="#3B82F6")
    grp_title = ctk.CTkLabel(
        grp_header,
        text="  Geometría 2D del Triángulo",
        image=icon_grid,
        compound="left",
        font=ctk.CTkFont(size=12, weight="bold"),
        anchor="w"
    )
    grp_title.pack(side="left")

    icon_centrar = get_icon("focus-centered", size=14, light_color="#1E293B", dark_color="#F8FAFC")
    btn_centrar = ctk.CTkButton(
        grp_header,
        text=" Centrar vista",
        image=icon_centrar,
        compound="left",
        width=0,
        height=26,
        corner_radius=6,
        fg_color="transparent",
        border_width=1,
        border_color=("gray70", "gray40"),
        text_color=("gray20", "gray85"),
        font=ctk.CTkFont(size=11),
        command=lambda: restablecer_vista()
    )
    btn_centrar.pack(side="right")

    grp_info = ctk.CTkLabel(grp_header, text="Rueda: zoom · Arrastrar: mover", font=ctk.CTkFont(size=10), text_color="gray", anchor="e")
    grp_info.pack(side="right", padx=(0, 10))

    figure = Figure(figsize=(7, 5), dpi=100)
    ax = figure.add_subplot(111)
    setup_ejes(ax, figure, limit=10, is_dark=(ctk.get_appearance_mode().lower() == "dark"))

    canvas = FigureCanvasTkAgg(figure, master=graph_card)
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(0, 10))
    body.excluir_rueda(canvas.get_tk_widget())

    # --- 5. TABLAS DE LAS LÍNEAS AB, BC Y CA (una por línea, como en el documento) ---
    tables_box = ctk.CTkFrame(body, height=ALTURA_TABLAS, corner_radius=0, fg_color="transparent")
    tables_box.pack(fill="x", padx=20, pady=(0, 12))
    tables_box.pack_propagate(False)
    tables_box.columnconfigure((0, 1, 2), weight=1, uniform="tabla")
    tables_box.rowconfigure(0, weight=1)

    encabezado_tabla = ["Paso", "Xₖ", "Yₖ", "Píxel"]
    tablas = {}
    icon_tbl = get_icon("table", size=16, light_color="#1E293B", dark_color="#F8FAFC")

    for col, lado in enumerate(("AB", "BC", "CA")):
        table_card = ctk.CTkFrame(tables_box, corner_radius=12, border_width=1, border_color=("gray85", "gray25"))
        table_card.grid(row=0, column=col, sticky="nsew", padx=(0 if col == 0 else 5, 0 if col == 2 else 5))

        ctk.CTkLabel(
            table_card,
            text=f"  Línea {lado}",
            image=icon_tbl,
            compound="left",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        ).pack(fill="x", padx=12, pady=(10, 2))

        lbl_info = ctk.CTkLabel(table_card, text="0 puntos calculados", font=ctk.CTkFont(size=10), text_color="gray", anchor="w")
        lbl_info.pack(fill="x", padx=12, pady=(0, 4))

        table_scroll = ctk.CTkScrollableFrame(table_card, fg_color="transparent", corner_radius=8)
        table_scroll.pack(fill="both", expand=True, padx=4, pady=(0, 8))

        tablas[lado] = {"scroll": table_scroll, "info": lbl_info, "table": None}

    def render_table(lado, rows_data):
        datos = tablas[lado]
        if datos["table"] is not None:
            datos["table"].destroy()

        ctk_tbl = CTkTable(
            datos["scroll"],
            row=len(rows_data),
            column=4,
            width=60,
            values=rows_data,
            header_color=("#3B82F6", "#1D4ED8"),
            colors=[("gray95", "#21252D"), ("gray90", "#1A1D24")],
            hover=True,
            hover_color=("#BFDBFE", "#1E3A8A"),
            corner_radius=8,
            font=ctk.CTkFont(size=11),
            justify="center"
        )
        ctk_tbl.pack(fill="x", expand=True)
        datos["table"] = ctk_tbl

    for lado in tablas:
        render_table(lado, [encabezado_tabla])
    canvas.draw()
    habilitar_navegacion(ax, canvas)

    # --- LÓGICA DE CONTROL ---
    def calculate():
        try:
            x1 = float(entryXA.get().strip())
            y1 = float(entryYA.get().strip())
            x2 = float(entryXB.get().strip())
            y2 = float(entryYB.get().strip())
            x3 = float(entryXC.get().strip())
            y3 = float(entryYC.get().strip())

            if x1.is_integer(): x1 = int(x1)
            if y1.is_integer(): y1 = int(y1)
            if x2.is_integer(): x2 = int(x2)
            if y2.is_integer(): y2 = int(y2)
            if x3.is_integer(): x3 = int(x3)
            if y3.is_integer(): y3 = int(y3)
        except ValueError:
            messagebox.showerror("Dato Inválido", "Por favor ingresa coordenadas numéricas válidas para los tres vértices.")
            return

        # Comprobación de puntos coincidentes
        if (x1 == x2 and y1 == y2) or (x2 == x3 and y2 == y3) or (x3 == x1 and y3 == y1):
            messagebox.showwarning(
                "Vértices Coincidentes",
                "Al menos dos de los vértices tienen exactamente las mismas coordenadas.\n"
                "Para formar un triángulo los tres vértices deben ser distintos."
            )
            return

        # Cálculo de distancias (longitudes de lados)
        d_ab = distancia_euclidiana(x1, y1, x2, y2)
        d_bc = distancia_euclidiana(x2, y2, x3, y3)
        d_ca = distancia_euclidiana(x3, y3, x1, y1)

        perimetro = calcular_perimetro_triangulo(d_ab, d_bc, d_ca)
        semiperimetro = perimetro / 2.0
        area = calcular_area_triangulo(x1, y1, x2, y2, x3, y3)

        es_colineal = (area < 1e-6)

        # Clasificaciones
        if es_colineal:
            tipo_lados = "Colineal"
            tipo_angulos = "Plano (180°)"
            estado_texto = "Puntos Colineales (Degenerado)"
        else:
            tipo_lados = clasificar_por_lados(d_ab, d_bc, d_ca)
            tipo_angulos = clasificar_por_angulos(d_ab, d_bc, d_ca)
            estado_texto = "Triángulo Válido"

        # El DDA trabaja con píxeles: cada vértice se ubica primero en su píxel para
        # que los lados y el relleno partan exactamente de los mismos puntos
        pa = (redondear_pixel(x1), redondear_pixel(y1))
        pb = (redondear_pixel(x2), redondear_pixel(y2))
        pc = (redondear_pixel(x3), redondear_pixel(y3))

        # Pendientes de las líneas que se trazan
        m_ab, str_m_ab = calcular_pendiente_segura(*pa, *pb)
        m_bc, str_m_bc = calcular_pendiente_segura(*pb, *pc)
        m_ca, str_m_ca = calcular_pendiente_segura(*pc, *pa)

        # Las 3 líneas del triángulo con el programa de la línea (DDA): AB, BC y CA
        lados = {
            "AB": (*pa, *pb),
            "BC": (*pb, *pc),
            "CA": (*pc, *pa),
        }
        pasos = {lado: generar_puntos_trayectoria(*coords) for lado, coords in lados.items()}
        pixeles = {lado: rasterizar_pixeles(puntos) for lado, puntos in pasos.items()}
        casos = {
            lado: clasificar_recta(xb - xa, yb - ya)
            for lado, (xa, ya, xb, yb) in lados.items()
        }

        # Relleno: el método del documento (C fijo hacia cada píxel de AB) se repite
        # con A hacia BC y con B hacia CA; las líneas se cruzan y tapan los huecos
        relleno = ajustar_al_contorno(
            generar_relleno(*pc, pixeles["AB"])
            + generar_relleno(*pa, pixeles["BC"])
            + generar_relleno(*pb, pixeles["CA"]),
            pixeles.values(),
        )

        # Unificar tabla con etiqueta de segmento
        all_table_points = [
            (lado, paso, px, py)
            for lado in ("AB", "BC", "CA")
            for paso, px, py in pasos[lado]
        ]

        # Límite para ejes del plano
        max_val = max(abs(x1), abs(y1), abs(x2), abs(y2), abs(x3), abs(y3))
        if max_val == 0:
            max_val = 10
        margin = max(2, int(max_val * 0.2) + 1)
        limit = max_val + margin

        current_triangle_data.clear()
        current_triangle_data.update({
            "has_data": True,
            "x1": x1, "y1": y1,
            "x2": x2, "y2": y2,
            "x3": x3, "y3": y3,
            "d_ab": d_ab, "d_bc": d_bc, "d_ca": d_ca,
            "perimetro": perimetro,
            "semiperimetro": semiperimetro,
            "area": area,
            "es_colineal": es_colineal,
            "tipo_lados": tipo_lados,
            "tipo_angulos": tipo_angulos,
            "m_ab": m_ab, "m_bc": m_bc, "m_ca": m_ca,
            "str_m_ab": str_m_ab, "str_m_bc": str_m_bc, "str_m_ca": str_m_ca,
            "limit": limit,
            "table_points": all_table_points,
            "pixeles": pixeles,
            "casos": casos,
            "relleno": relleno,
        })

        # Si son colineales, notificar al usuario
        if es_colineal:
            messagebox.showwarning(
                "Puntos Colineales",
                "Los tres puntos ingresados están sobre la misma línea recta (Área = 0).\n"
                "No forman un triángulo con superficie, sino un segmento colineal."
            )

        # Actualizar Tarjetas de Métricas
        # 1. Área y Perímetro
        val_area_num.configure(text=f"{area:.2f} u²")
        val_perim_sub.configure(text=f"Perímetro: {perimetro:.2f} u")
        val_semi_sub.configure(text=f"Semiperímetro: {semiperimetro:.2f} u")

        # 2. Clasificación
        val_class_num.configure(text=tipo_lados)
        val_ang_sub.configure(text=f"Por ángulos: {tipo_angulos}")
        val_status_sub.configure(text=f"Estado: {estado_texto}")

        # 3. Longitudes de lados
        max_side = max(d_ab, d_bc, d_ca)
        val_sides_num.configure(text=f"L_máx: {max_side:.2f} u")
        val_ab_sub.configure(text=f"d(A, B) = {d_ab:.2f} u")
        val_bcca_sub.configure(text=f"d(B, C): {d_bc:.2f} | d(C, A): {d_ca:.2f}")

        # 4. Pendientes
        val_slopes_num.configure(text=f"m_AB = {str_m_ab}")
        val_mab_sub.configure(text=f"m_BC: {str_m_bc}")
        val_mca_sub.configure(text=f"m_CA: {str_m_ca}")

        # 5. Caso DDA de cada lado
        for lado, (val_caso, val_detalle, val_notacion) in casos_labels.items():
            caso, detalle, notacion = casos[lado]
            val_caso.configure(text=caso)
            val_detalle.configure(text=detalle)
            val_notacion.configure(text=notacion)

        # Llenar la tabla de cada línea: valores con decimales y el píxel redondeado
        nombres = {"AB": ("A", "B"), "BC": ("B", "C"), "CA": ("C", "A")}
        for lado, (xa, ya, xb, yb) in lados.items():
            filas = [list(encabezado_tabla)]
            for paso, px, py in pasos[lado]:
                filas.append([str(paso), f"{px:.2f}", f"{py:.2f}", f"({redondear_pixel(px)}, {redondear_pixel(py)})"])
            render_table(lado, filas)
            ini, fin = nombres[lado]
            tablas[lado]["info"].configure(
                text=f"{ini}({xa:g}, {ya:g}) → {fin}({xb:g}, {yb:g}) · {len(pasos[lado])} puntos calculados"
            )

        # Repintar gráfica
        render_triangle_plot(ax, figure, canvas)

    def clear():
        entryXA.delete(0, "end")
        entryYA.delete(0, "end")
        entryXB.delete(0, "end")
        entryYB.delete(0, "end")
        entryXC.delete(0, "end")
        entryYC.delete(0, "end")

        val_area_num.configure(text="--")
        val_perim_sub.configure(text="Perímetro: --")
        val_semi_sub.configure(text="Semiperímetro: --")

        val_class_num.configure(text="--")
        val_ang_sub.configure(text="Por ángulos: --")
        val_status_sub.configure(text="Estado: --")

        val_sides_num.configure(text="--")
        val_ab_sub.configure(text="d(A, B): --")
        val_bcca_sub.configure(text="d(B, C): -- | d(C, A): --")

        val_slopes_num.configure(text="--")
        val_mab_sub.configure(text="m_AB: -- | m_BC: --")
        val_mca_sub.configure(text="m_CA: --")

        for val_caso, val_detalle, val_notacion in casos_labels.values():
            val_caso.configure(text="--")
            val_detalle.configure(text="")
            val_notacion.configure(text="")

        for lado in tablas:
            render_table(lado, [encabezado_tabla])
            tablas[lado]["info"].configure(text="0 puntos calculados")
        current_triangle_data.clear()

        render_triangle_plot(ax, figure, canvas)
        entryXA.focus_set()

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
    entryXA.insert(0, "1")
    entryYA.insert(0, "1")
    entryXB.insert(0, "7")
    entryYB.insert(0, "2")
    entryXC.insert(0, "3")
    entryYC.insert(0, "7")

    return page
