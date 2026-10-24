"""
Módulo de Trazo de Circunferencia y Círculo Relleno.
1. Ecuaciones analíticas: Teorema de Pitágoras (X - Xc)² + (Y - Yc)² = r², ecuación explícita
   Y = Yc ± √(r² - (Xc - X)²) y ecuación general X² + Y² + DX + EY + F = 0.
2. Algoritmo de Punto Medio de Bresenham para circunferencia con parámetro inicial
   P0 = 1 - r (o 5/4 - r) y prueba en cada Xk:
     - Si Pk < 0: Pk+1 = Pk + 2*Xk+1 + 1, con (Xk+1, Yk)
     - Si Pk >= 0: Pk+1 = Pk + 2*Xk+1 + 1 - 2*Yk+1, con (Xk+1, Yk-1)
     - Ciclo hasta X >= Y.
3. Simetría de 8 Octantes con traslación bidimensional C(Xc, Yc).
4. Relleno del círculo:
   - DDA Radial: Centro fijo A(Xc, Yc) hacia cada píxel B de los 8 octantes trazado con DDA (11 casos).
   - Cuerdas (Scanlines horizontales) y Círculos concéntricos.
5. Visualización interactiva con Matplotlib y pestañas optimizadas (renderizado bajo demanda
   y paginación eficiente de líneas para máxima fluidez).
"""
import math
from tkinter import messagebox
import customtkinter as ctk
from CTkTable import CTkTable

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.collections import LineCollection
from matplotlib.figure import Figure
from matplotlib.patches import Circle

from pages.icons import get_icon
from pages.puntos_colineales import (
    ALTURA_GRAFICA,
    PaginaDesplazable,
    clasificar_recta,
    habilitar_navegacion,
    register_plot_updater,
    setup_ejes,
)

# Estado reactivo global del módulo de circunferencia
current_circle_data = {}

ALTURA_TABLA_CIRCULO = 450
LINEAS_POR_PAGINA_DDA = 25


def algoritmo_punto_medio_circunferencia(xc, yc, r, usar_fraccion=False):
    """
    Algoritmo de Punto Medio de Bresenham para la Circunferencia.
    Punto inicial: (X0, Y0) = (0, r).
    P0 = 5/4 - r o P0 = 1 - r.
    Repite hasta que X >= Y.
    """
    r = int(round(r))
    xc = int(round(xc))
    yc = int(round(yc))

    x = 0
    y = r
    p0 = (1.25 - r) if usar_fraccion else (1 - r)
    p = p0

    pasos = []
    pixeles_contorno = set()
    octantes_dict = {i: [] for i in range(1, 9)}

    # Puntos cardinales del punto inicial (0, r)
    puntos_iniciales = [
        (xc + 0, yc + r),
        (xc + 0, yc - r),
        (xc + r, yc + 0),
        (xc - r, yc + 0),
    ]
    for pt in puntos_iniciales:
        pixeles_contorno.add(pt)

    k = 0
    while x < y:
        x_sig = x + 1
        p_actual = p

        if p < 0:
            y_sig = y
            delta = 2 * x_sig + 1
            p_sig = p + delta
            formula_txt = f"{p_actual:g} + 2({x_sig}) + 1 = {p_sig:g}"
            decision_txt = f"Pₖ < 0 → (Xₖ₊₁, Yₖ) = ({x_sig}, {y_sig})"
        else:
            y_sig = y - 1
            delta = 2 * x_sig + 1 - 2 * y_sig
            p_sig = p + delta
            formula_txt = f"{p_actual:g} + 2({x_sig}) + 1 - 2({y_sig}) = {p_sig:g}"
            decision_txt = f"Pₖ ≥ 0 → (Xₖ₊₁, Yₖ₋₁) = ({x_sig}, {y_sig})"

        # Simetría en los 8 Octantes con traslación del centro (Xc, Yc)
        pts_simetria = [
            (xc + x_sig, yc + y_sig),  # Oct 1: (+x, +y)
            (xc + y_sig, yc + x_sig),  # Oct 2: (+y, +x)
            (xc - y_sig, yc + x_sig),  # Oct 3: (-y, +x)
            (xc - x_sig, yc + y_sig),  # Oct 4: (-x, +y)
            (xc - x_sig, yc - y_sig),  # Oct 5: (-x, -y)
            (xc - y_sig, yc - x_sig),  # Oct 6: (-y, -x)
            (xc + y_sig, yc - x_sig),  # Oct 7: (+y, -x)
            (xc + x_sig, yc - y_sig),  # Oct 8: (+x, -y)
        ]

        for idx, pt in enumerate(pts_simetria, start=1):
            octantes_dict[idx].append(pt)
            pixeles_contorno.add(pt)

        pasos.append({
            "k": k,
            "pk": p_actual,
            "x_sig": x_sig,
            "y_sig": y_sig,
            "formula": formula_txt,
            "decision": decision_txt,
            "base_trans": (xc + x_sig, yc + y_sig),
            "pts": pts_simetria
        })

        x = x_sig
        y = y_sig
        p = p_sig
        k += 1

        if x >= y:
            break

    puntos_ordenados = sorted(
        pixeles_contorno,
        key=lambda pt: math.atan2(pt[1] - yc, pt[0] - xc)
    )

    return pasos, pixeles_contorno, puntos_ordenados, octantes_dict


def generar_relleno_dda_radial(xc, yc, puntos_borde):
    """
    Relleno del Círculo trazando líneas DDA desde el centro fijo A(Xc, Yc)
    hacia cada píxel B de los 8 octantes del contorno.
    Optimizado con interpolación directa de píxeles para máxima velocidad.
    """
    lineas_segmentos = []
    lineas_info = []
    pixeles_relleno = set()

    for idx, (bx, by) in enumerate(puntos_borde, start=1):
        dx = bx - xc
        dy = by - yc
        pasos = max(abs(dx), abs(dy))

        if pasos == 0:
            pixeles_relleno.add((xc, yc))
            num_px = 1
        else:
            step_x = dx / pasos
            step_y = dy / pasos
            for i in range(pasos + 1):
                px = int(round(xc + i * step_x))
                py = int(round(yc + i * step_y))
                pixeles_relleno.add((px, py))
            num_px = pasos + 1

        lineas_segmentos.append(((xc, yc), (bx, by)))
        dist = math.hypot(dx, dy)
        caso, _, notacion = clasificar_recta(dx, dy)

        lineas_info.append({
            "num": idx,
            "a": (xc, yc),
            "b": (bx, by),
            "dist": dist,
            "caso": caso,
            "notacion": notacion,
            "num_px": num_px
        })

    return lineas_segmentos, pixeles_relleno, lineas_info


def generar_relleno_cuerdas_scanlines(xc, yc, r, pixeles_contorno):
    """
    Método de Cuerdas (Scanlines): Conecta de extremo a extremo cada fila horizontal.
    """
    filas = {}
    for px, py in pixeles_contorno:
        if py not in filas:
            filas[py] = [px, px]
        else:
            if px < filas[py][0]:
                filas[py][0] = px
            if px > filas[py][1]:
                filas[py][1] = px

    segmentos = []
    pixeles_relleno = set()

    for py in sorted(filas.keys()):
        xmin, xmax = filas[py]
        segmentos.append(((xmin, py), (xmax, py)))
        for x in range(xmin, xmax + 1):
            pixeles_relleno.add((x, py))

    return segmentos, pixeles_relleno


def generar_relleno_concentrico(xc, yc, r):
    """
    Método de Círculos Concéntricos: Dibuja circunferencias con radios enteros de 1 a r.
    Optimizado para calcular arcos concéntricos sin sobrecargar.
    """
    segmentos = []
    pixeles_relleno = set()
    r_int = int(round(r))

    for rad in range(1, r_int + 1):
        x = 0
        y = rad
        p = 1 - rad
        while x <= y:
            pixeles_relleno.add((xc + x, yc + y))
            pixeles_relleno.add((xc + y, yc + x))
            pixeles_relleno.add((xc - y, yc + x))
            pixeles_relleno.add((xc - x, yc + y))
            pixeles_relleno.add((xc - x, yc - y))
            pixeles_relleno.add((xc - y, yc - x))
            pixeles_relleno.add((xc + y, yc - x))
            pixeles_relleno.add((xc + x, yc - y))
            x += 1
            if p < 0:
                p += 2 * x + 1
            else:
                y -= 1
                p += 2 * (x - y) + 1

    return segmentos, pixeles_relleno


def get_ecuaciones_circunferencia(xc, yc, r):
    """
    Genera las ecuaciones de la circunferencia:
    - Ordinaria: (X - Xc)² + (Y - Yc)² = r²
    - Explícita: Y = Yc ± √(r² - (Xc - X)²)
    - General:   X² + Y² + DX + EY + F = 0
    """
    r_sq = r ** 2

    if xc == 0:
        term_x = "X²"
    elif xc > 0:
        term_x = f"(X - {xc:g})²"
    else:
        term_x = f"(X + {abs(xc):g})²"

    if yc == 0:
        term_y = "Y²"
    elif yc > 0:
        term_y = f"(Y - {yc:g})²"
    else:
        term_y = f"(Y + {abs(yc):g})²"

    ordinaria = f"{term_x} + {term_y} = {r_sq:g}"

    base_x = "X" if xc == 0 else (f"({xc:g} - X)" if xc > 0 else f"({xc:g} - X)")
    if yc == 0:
        explicita = f"Y = ± √({r_sq:g} - {base_x}²)"
    else:
        explicita = f"Y = {yc:g} ± √({r_sq:g} - {base_x}²)"

    D = -2 * xc
    E = -2 * yc
    F = xc ** 2 + yc ** 2 - r_sq

    partes_gen = ["X² + Y²"]
    if D != 0:
        signo_d = "+ " if D > 0 else "- "
        val_d = abs(D)
        partes_gen.append(f"{signo_d}{val_d:g}X" if val_d != 1 else f"{signo_d}X")
    if E != 0:
        signo_e = "+ " if E > 0 else "- "
        val_e = abs(E)
        partes_gen.append(f"{signo_e}{val_e:g}Y" if val_e != 1 else f"{signo_e}Y")
    if F != 0:
        signo_f = "+ " if F > 0 else "- "
        partes_gen.append(f"{signo_f}{abs(F):g}")

    partes_gen.append("= 0")
    general = " ".join(partes_gen)

    return ordinaria, explicita, general


def render_circle_plot(ax, figure, canvas, view=None):
    """
    Renderiza la circunferencia y el círculo relleno en el plano cartesiano.
    Diseñado para respuesta ágil con draw_idle y colecciones optimizadas.
    """
    is_dark = (ctk.get_appearance_mode().lower() == "dark")
    fig_bg = "#2B2B2B" if is_dark else "#F2F2F2"
    border_color = "#444444" if is_dark else "#D0D0D0"
    text_color = "#E0E0E0" if is_dark else "#1A1A1A"

    color_centro = "#F59E0B" if is_dark else "#D97706"
    color_primer_pto = "#10B981" if is_dark else "#059669"
    color_contorno = "#38BDF8" if is_dark else "#0284C7"
    color_relleno = "#3B82F6" if is_dark else "#2563EB"
    color_ideal = "#64748B" if is_dark else "#94A3B8"
    color_relleno_solido = "#EAB308" if is_dark else "#FACC15"

    ax.clear()
    limit = current_circle_data.get("limit", 20)
    setup_ejes(ax, figure, limit=limit, is_dark=is_dark)

    if current_circle_data.get("has_data"):
        xc = current_circle_data["xc"]
        yc = current_circle_data["yc"]
        r = current_circle_data["r"]
        modo_vista = current_circle_data.get("modo_vista", "Ambos")
        metodo_relleno = current_circle_data.get("metodo_relleno", "DDA Radial (Centro a Octantes)")
        mostrar_contorno = modo_vista in ("Ambos", "Solo Contorno")
        mostrar_relleno = modo_vista in ("Ambos", "Solo Relleno")

        pixeles_contorno = current_circle_data["pixeles_contorno"]
        segmentos_relleno = current_circle_data.get("segmentos_relleno", [])
        pixeles_relleno = current_circle_data.get("pixeles_relleno", set())

        # 1. Círculo continuo de referencia
        circle_ideal = Circle(
            (xc, yc),
            r,
            fill=False,
            edgecolor=color_ideal,
            linestyle="--",
            linewidth=1.2,
            alpha=0.6,
            label=f"Radio continuo (R={r:g})"
        )
        ax.add_patch(circle_ideal)

        # 2. Relleno según el método
        if mostrar_relleno:
            circle_fill_patch = Circle(
                (xc, yc),
                r,
                fill=True,
                facecolor=color_relleno_solido,
                edgecolor="none",
                alpha=0.35,
                zorder=2,
                label=f"Círculo Relleno ({len(pixeles_relleno)} px)"
            )
            ax.add_patch(circle_fill_patch)

            if "DDA Radial" in metodo_relleno and segmentos_relleno:
                lc_radial = LineCollection(
                    segmentos_relleno,
                    colors=color_relleno,
                    linewidths=1.2,
                    alpha=0.55,
                    zorder=3,
                    label=f"Líneas DDA ({len(segmentos_relleno)})"
                )
                ax.add_collection(lc_radial)
            elif "Cuerdas" in metodo_relleno and segmentos_relleno:
                lc_cuerdas = LineCollection(
                    segmentos_relleno,
                    colors=color_relleno,
                    linewidths=4.0,
                    alpha=0.6,
                    capstyle="projecting",
                    zorder=3,
                    label=f"Scanlines ({len(pixeles_relleno)} px)"
                )
                ax.add_collection(lc_cuerdas)
            elif "Concéntrico" in metodo_relleno and pixeles_relleno:
                pxs = [pt[0] for pt in pixeles_relleno]
                pys = [pt[1] for pt in pixeles_relleno]
                ax.scatter(
                    pxs, pys,
                    s=14,
                    c=color_relleno,
                    marker="s",
                    alpha=0.45,
                    edgecolors="none",
                    zorder=3,
                    label=f"Concéntricos ({len(pixeles_relleno)} px)"
                )

        # 3. Píxeles del contorno (Punto Medio Bresenham en 8 Octantes)
        if mostrar_contorno and pixeles_contorno:
            pxs = [pt[0] for pt in pixeles_contorno]
            pys = [pt[1] for pt in pixeles_contorno]
            ax.scatter(
                pxs,
                pys,
                s=28,
                c=color_contorno,
                marker="s",
                alpha=0.95,
                edgecolors="#FFFFFF" if is_dark else "#0F172A",
                linewidths=0.5,
                zorder=4,
                label=f"Borde 8 Octantes ({len(pixeles_contorno)} px)"
            )

        # 4. Primer punto (0, r) trasladado -> (Xc, Yc + r)
        pto_cero_r = (xc, yc + r)
        ax.plot(
            [pto_cero_r[0]], [pto_cero_r[1]],
            marker="^",
            markersize=9,
            color=color_primer_pto,
            markeredgecolor="#FFFFFF",
            markeredgewidth=1.2,
            zorder=5,
            label=f"(0, r) = ({pto_cero_r[0]:g}, {pto_cero_r[1]:g})"
        )

        # 5. Centro trasladado (Xc, Yc) con cruz y punto destacado
        ax.plot(
            [xc], [yc],
            marker="o",
            markersize=8,
            color=color_centro,
            markeredgecolor="#FFFFFF",
            markeredgewidth=1.5,
            zorder=5,
            label=f"Centro C({xc:g}, {yc:g})"
        )

        ax.plot([xc, xc], [0, yc], linestyle=":", color=color_centro, linewidth=1.0, alpha=0.7)
        ax.plot([0, xc], [yc, yc], linestyle=":", color=color_centro, linewidth=1.0, alpha=0.7)

        bbox_c = dict(boxstyle="round,pad=0.35", fc=fig_bg, ec=color_centro, lw=1.2, alpha=0.95)
        ax.annotate(
            f"C ({xc:g}, {yc:g})",
            (xc, yc),
            textcoords="offset points",
            xytext=(0, 14),
            ha="center",
            fontsize=9,
            fontweight="bold",
            color=color_centro,
            bbox=bbox_c,
            zorder=6
        )

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
    elif current_circle_data.get("has_data"):
        xc = current_circle_data["xc"]
        yc = current_circle_data["yc"]
        r = current_circle_data["r"]
        span = max(r * 1.5, 12)
        ax.set_xlim(xc - span, xc + span)
        ax.set_ylim(yc - span, yc + span)

    figure.tight_layout()
    canvas.draw_idle()


def create_circulo_page(container):
    """
    Construye la página de Trazo de Circunferencia y Círculo Relleno con
    CustomTkinter, visualizador interactivo y sistema de pestañas de alto rendimiento.
    """
    page = ctk.CTkFrame(container, corner_radius=0, fg_color="transparent")
    body = PaginaDesplazable(page, corner_radius=0, fg_color="transparent")
    body.pack(fill="both", expand=True)

    # --- 1. ENCABEZADO ---
    header_frame = ctk.CTkFrame(body, corner_radius=0, fg_color="transparent")
    header_frame.pack(fill="x", padx=20, pady=(12, 4))

    lbl_title = ctk.CTkLabel(
        header_frame,
        text="Trazo de Circunferencia y Círculo Relleno",
        font=ctk.CTkFont(size=20, weight="bold"),
        anchor="w"
    )
    lbl_title.pack(anchor="w")

    lbl_subtitle = ctk.CTkLabel(
        header_frame,
        text="Algoritmo de Punto Medio de Bresenham · Simetría de 8 Octantes · Traslación Bidimensional C(Xc, Yc) · Relleno DDA Radial y Scanline.",
        font=ctk.CTkFont(size=12),
        text_color="gray",
        anchor="w"
    )
    lbl_subtitle.pack(anchor="w", pady=(2, 0))

    # --- 2. FORMULARIO (INPUTS) ---
    form_card = ctk.CTkFrame(body, corner_radius=12, border_width=1, border_color=("gray85", "gray25"))
    form_card.pack(fill="x", padx=20, pady=(0, 8))

    form_top = ctk.CTkFrame(form_card, fg_color="transparent")
    form_top.pack(fill="x", padx=16, pady=8)

    # Centro (Xc, Yc)
    box_c = ctk.CTkFrame(form_top, fg_color="transparent")
    box_c.pack(side="left", padx=(0, 16))

    lbl_c_title = ctk.CTkLabel(box_c, text="Centro Trasladado (Xc, Yc)", font=ctk.CTkFont(size=12, weight="bold"))
    lbl_c_title.grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 4))

    lbl_xc = ctk.CTkLabel(box_c, text="Xc:", font=ctk.CTkFont(size=12))
    lbl_xc.grid(row=1, column=0, padx=(0, 4))
    entryXC = ctk.CTkEntry(box_c, width=65, height=32, corner_radius=6, justify="center")
    entryXC.grid(row=1, column=1, padx=(0, 10))
    entryXC.insert(0, "150")

    lbl_yc = ctk.CTkLabel(box_c, text="Yc:", font=ctk.CTkFont(size=12))
    lbl_yc.grid(row=1, column=2, padx=(0, 4))
    entryYC = ctk.CTkEntry(box_c, width=65, height=32, corner_radius=6, justify="center")
    entryYC.grid(row=1, column=3)
    entryYC.insert(0, "100")

    # Radio (R)
    box_r = ctk.CTkFrame(form_top, fg_color="transparent")
    box_r.pack(side="left", padx=(0, 16))

    lbl_r_title = ctk.CTkLabel(box_r, text="Dimensión", font=ctk.CTkFont(size=12, weight="bold"))
    lbl_r_title.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 4))

    lbl_r = ctk.CTkLabel(box_r, text="Radio (R):", font=ctk.CTkFont(size=12))
    lbl_r.grid(row=1, column=0, padx=(0, 4))
    entryR = ctk.CTkEntry(box_r, width=65, height=32, corner_radius=6, justify="center")
    entryR.grid(row=1, column=1)
    entryR.insert(0, "10")

    # Método de Relleno
    box_fill_method = ctk.CTkFrame(form_top, fg_color="transparent")
    box_fill_method.pack(side="left", padx=(0, 16))

    lbl_fm_title = ctk.CTkLabel(box_fill_method, text="Método de Relleno", font=ctk.CTkFont(size=12, weight="bold"))
    lbl_fm_title.pack(anchor="w", pady=(0, 4))

    opt_metodo = ctk.CTkOptionMenu(
        box_fill_method,
        values=[
            "DDA Radial (Centro a Octantes)",
            "Cuerdas (Líneas Horizontales / Scanline)",
            "Círculos Concéntricos"
        ],
        font=ctk.CTkFont(size=11),
        width=230,
        height=32,
        command=lambda _: on_method_change()
    )
    opt_metodo.pack(anchor="w")

    # Modo de Visualización
    box_mode = ctk.CTkFrame(form_top, fg_color="transparent")
    box_mode.pack(side="left", padx=(0, 16))

    lbl_m_title = ctk.CTkLabel(box_mode, text="Visualización", font=ctk.CTkFont(size=12, weight="bold"))
    lbl_m_title.pack(anchor="w", pady=(0, 4))

    seg_modo = ctk.CTkSegmentedButton(
        box_mode,
        values=["Ambos", "Solo Contorno", "Solo Relleno"],
        font=ctk.CTkFont(size=11),
        height=32,
        command=lambda _: on_mode_change()
    )
    seg_modo.pack(anchor="w")
    seg_modo.set("Ambos")

    # Botones de Acción
    box_btn = ctk.CTkFrame(form_top, fg_color="transparent")
    box_btn.pack(side="right", padx=(10, 0))

    icon_play = get_icon("player-play", size=16, light_color="#FFFFFF", dark_color="#FFFFFF")
    btn_calc = ctk.CTkButton(
        box_btn,
        text=" Calcular y Trazar",
        image=icon_play,
        compound="left",
        font=ctk.CTkFont(size=12, weight="bold"),
        height=34,
        corner_radius=8,
        fg_color=["#3B82F6", "#2563EB"],
        command=lambda: calculate()
    )
    btn_calc.pack(side="left", padx=(0, 8))

    # Barra inferior de plantillas y traslación interactiva
    trans_bar = ctk.CTkFrame(form_card, fg_color=("gray95", "gray17"), corner_radius=8)
    trans_bar.pack(fill="x", padx=16, pady=(0, 8))

    ctk.CTkLabel(
        trans_bar,
        text="Plantillas de Prueba:",
        font=ctk.CTkFont(size=11, weight="bold"),
        text_color="gray"
    ).pack(side="left", padx=(10, 6), pady=4)

    def cargar_ejemplo_1():
        entryXC.delete(0, "end"); entryXC.insert(0, "150")
        entryYC.delete(0, "end"); entryYC.insert(0, "100")
        entryR.delete(0, "end"); entryR.insert(0, "10")
        calculate()

    def cargar_ejemplo_2():
        entryXC.delete(0, "end"); entryXC.insert(0, "100")
        entryYC.delete(0, "end"); entryYC.insert(0, "100")
        entryR.delete(0, "end"); entryR.insert(0, "51")
        calculate()

    def cargar_ejemplo_origen():
        entryXC.delete(0, "end"); entryXC.insert(0, "0")
        entryYC.delete(0, "end"); entryYC.insert(0, "0")
        entryR.delete(0, "end"); entryR.insert(0, "10")
        calculate()

    btn_ex1 = ctk.CTkButton(
        trans_bar,
        text="Ejemplo 1: C(150, 100), R=10",
        height=24,
        font=ctk.CTkFont(size=10, weight="bold"),
        fg_color=["#3B82F6", "#1D4ED8"],
        command=cargar_ejemplo_1
    )
    btn_ex1.pack(side="left", padx=3, pady=4)

    btn_ex2 = ctk.CTkButton(
        trans_bar,
        text="Ejemplo 2: C(100, 100), R=51",
        height=24,
        font=ctk.CTkFont(size=10),
        fg_color="transparent",
        border_width=1,
        border_color=("gray70", "gray40"),
        text_color=("gray20", "gray85"),
        command=cargar_ejemplo_2
    )
    btn_ex2.pack(side="left", padx=3, pady=4)

    btn_orig_ex = ctk.CTkButton(
        trans_bar,
        text="Origen: C(0, 0), R=10",
        height=24,
        font=ctk.CTkFont(size=10),
        fg_color="transparent",
        border_width=1,
        border_color=("gray70", "gray40"),
        text_color=("gray20", "gray85"),
        command=cargar_ejemplo_origen
    )
    btn_orig_ex.pack(side="left", padx=3, pady=4)

    # Traslación interactiva del centro
    sep_trans = ctk.CTkFrame(trans_bar, width=1, height=18, fg_color=("gray80", "gray35"))
    sep_trans.pack(side="left", padx=8, pady=4)

    ctk.CTkLabel(
        trans_bar,
        text="Trasladar Centro:",
        font=ctk.CTkFont(size=11, weight="bold"),
        text_color="gray"
    ).pack(side="left", padx=(2, 6), pady=4)

    def trasladar_centro(dx, dy):
        try:
            cur_xc = float(entryXC.get().strip())
            cur_yc = float(entryYC.get().strip())
            new_xc = int(round(cur_xc + dx))
            new_yc = int(round(cur_yc + dy))
            entryXC.delete(0, "end"); entryXC.insert(0, str(new_xc))
            entryYC.delete(0, "end"); entryYC.insert(0, str(new_yc))
            calculate()
        except ValueError:
            pass

    for txt, dx, dy in (("◀ X - 5", -5, 0), ("X + 5 ▶", 5, 0), ("▼ Y - 5", 0, -5), ("▲ Y + 5", 0, 5)):
        b = ctk.CTkButton(
            trans_bar,
            text=txt,
            width=58,
            height=24,
            font=ctk.CTkFont(size=10),
            fg_color="transparent",
            border_width=1,
            border_color=("gray70", "gray40"),
            text_color=("gray20", "gray85"),
            command=lambda x=dx, y=dy: trasladar_centro(x, y)
        )
        b.pack(side="left", padx=2, pady=4)

    # --- 3. TARJETAS DE MÉTRICAS ANALÍTICAS ---
    metrics_frame = ctk.CTkFrame(body, corner_radius=0, fg_color="transparent")
    metrics_frame.pack(fill="x", padx=20, pady=(0, 8))
    metrics_frame.columnconfigure((0, 1, 2, 3), weight=1, uniform="metric")

    cards = {}

    def crear_tarjeta_metrica(col, titulo, valor_inicial, subtexto):
        card = ctk.CTkFrame(metrics_frame, corner_radius=10, border_width=1, border_color=("gray85", "gray25"))
        card.grid(row=0, column=col, padx=(0 if col == 0 else 4, 0 if col == 3 else 4), sticky="nsew")

        lbl_t = ctk.CTkLabel(card, text=titulo, font=ctk.CTkFont(size=10, weight="bold"), text_color="gray", anchor="w")
        lbl_t.pack(fill="x", padx=10, pady=(8, 1))

        lbl_v = ctk.CTkLabel(card, text=valor_inicial, font=ctk.CTkFont(size=13, weight="bold"), anchor="w")
        lbl_v.pack(fill="x", padx=10, pady=(0, 1))

        lbl_s = ctk.CTkLabel(card, text=subtexto, font=ctk.CTkFont(size=10), text_color="gray", anchor="w")
        lbl_s.pack(fill="x", padx=10, pady=(0, 8))

        return {"val": lbl_v, "sub": lbl_s}

    cards["ec_ord"] = crear_tarjeta_metrica(0, "ECUACIÓN ORDINARIA", "(X - 150)² + (Y - 100)² = 100", "Primer punto (0, r): (150, 110)")
    cards["ec_exp"] = crear_tarjeta_metrica(1, "ECUACIÓN EXPLÍCITA", "Y = 100 ± √(100 - (150 - X)²)", "Y = Yc ± √(r² - (Xc - X)²)")
    cards["geom"] = crear_tarjeta_metrica(2, "MÉTRICAS GEOMÉTRICAS", "Área: 314.16 u²", "Perímetro: 62.83 u · Diám: 20")
    cards["pix"] = crear_tarjeta_metrica(3, "PÍXELES Y OCTANTES", "7 pasos · P₀ = -9", "Simetría de 8 Octantes con Traslación")

    # --- 4. GRÁFICA / PLANO CARTESIANO ---
    graph_card = ctk.CTkFrame(body, height=ALTURA_GRAFICA, corner_radius=12, border_width=1, border_color=("gray85", "gray25"))
    graph_card.pack(fill="x", padx=20, pady=(0, 8))
    graph_card.pack_propagate(False)

    grp_header = ctk.CTkFrame(graph_card, fg_color="transparent")
    grp_header.pack(fill="x", padx=14, pady=8)

    icon_grid = get_icon("grid-dots", size=16, light_color="#2563EB", dark_color="#3B82F6")
    grp_title = ctk.CTkLabel(
        grp_header,
        text="  Visualizador de Circunferencia, Octantes y Relleno",
        image=icon_grid,
        compound="left",
        font=ctk.CTkFont(size=12, weight="bold"),
        anchor="w"
    )
    grp_title.pack(side="left")

    icon_centrar = get_icon("focus-centered", size=14, light_color="#1E293B", dark_color="#F8FAFC")
    btn_centrar = ctk.CTkButton(
        grp_header,
        text=" Centrar en Círculo",
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
        command=lambda: restablecer_vista_circulo()
    )
    btn_centrar.pack(side="right")

    btn_ver_origen = ctk.CTkButton(
        grp_header,
        text=" Ver con Origen (0,0)",
        width=0,
        height=26,
        corner_radius=6,
        fg_color="transparent",
        border_width=1,
        border_color=("gray70", "gray40"),
        text_color=("gray20", "gray85"),
        font=ctk.CTkFont(size=11),
        command=lambda: vista_completa_origen()
    )
    btn_ver_origen.pack(side="right", padx=(0, 6))

    grp_info = ctk.CTkLabel(grp_header, text="Rueda: zoom · Arrastrar: mover", font=ctk.CTkFont(size=10), text_color="gray", anchor="e")
    grp_info.pack(side="right", padx=(0, 10))

    figure = Figure(figsize=(7, 5), dpi=100)
    ax = figure.add_subplot(111)
    setup_ejes(ax, figure, limit=20, is_dark=(ctk.get_appearance_mode().lower() == "dark"))

    canvas = FigureCanvasTkAgg(figure, master=graph_card)
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(0, 10))
    body.excluir_rueda(canvas.get_tk_widget())
    canvas.draw()
    habilitar_navegacion(ax, canvas)

    # --- 5. PESTAÑAS DE TABLAS CON OPTIMIZACIÓN Y LAZY LOADING ---
    tabview_card = ctk.CTkFrame(body, height=ALTURA_TABLA_CIRCULO, corner_radius=12, border_width=1, border_color=("gray85", "gray25"))
    tabview_card.pack(fill="x", padx=20, pady=(0, 12))
    tabview_card.pack_propagate(False)

    TAB_GEN_NAME = "  Tabla General de Iteraciones  "
    TAB_OCT_NAME = "  Octantes de Simetría  "
    TAB_DDA_NAME = "  Detalle de Líneas DDA  "

    tabview = ctk.CTkTabview(tabview_card, corner_radius=8, command=lambda: on_tabview_change())
    tabview.pack(fill="both", expand=True, padx=8, pady=6)

    tab_general = tabview.add(TAB_GEN_NAME)
    tab_octantes = tabview.add(TAB_OCT_NAME)
    tab_dda = tabview.add(TAB_DDA_NAME)

    # Estado de renderizado perezoso (Lazy)
    tabs_actualizadas = {
        TAB_GEN_NAME: False,
        TAB_OCT_NAME: False,
        TAB_DDA_NAME: False,
    }

    # --- TAB 1: GENERAL ---
    scroll_gen = ctk.CTkScrollableFrame(tab_general, fg_color="transparent", corner_radius=8)
    scroll_gen.pack(fill="both", expand=True, padx=4, pady=4)
    tbl_gen_holder = {"table": None}

    encabezado_general = [
        "N",
        "Pₖ",
        "Cálculo Pₖ₊₁ (Fórmula)",
        "Xₖ₊₁ (Base)",
        "Yₖ₊₁ (Base)",
        "Punto Trasladado",
        "Oct 1 (+x,+y)",
        "Oct 2 (+y,+x)",
        "Oct 3 (-y,+x)",
        "Oct 4 (-x,+y)",
        "Oct 5 (-x,-y)",
        "Oct 6 (-y,-x)",
        "Oct 7 (+y,-x)",
        "Oct 8 (+x,-y)"
    ]

    def render_general_table(rows_data):
        if tbl_gen_holder["table"] is not None:
            tbl_gen_holder["table"].destroy()

        ctk_tbl = CTkTable(
            scroll_gen,
            row=len(rows_data),
            column=len(encabezado_general),
            width=54,
            values=rows_data,
            header_color=("#3B82F6", "#1D4ED8"),
            colors=[("gray95", "#21252D"), ("gray90", "#1A1D24")],
            hover=True,
            hover_color=("#BFDBFE", "#1E3A8A"),
            corner_radius=8,
            font=ctk.CTkFont(size=10),
            justify="center"
        )
        ctk_tbl.pack(fill="x", expand=True)
        tbl_gen_holder["table"] = ctk_tbl
        tabs_actualizadas[TAB_GEN_NAME] = True

    # --- TAB 2: OCTANTES DE SIMETRÍA ---
    box_oct_controls = ctk.CTkFrame(tab_octantes, fg_color="transparent")
    box_oct_controls.pack(fill="x", padx=4, pady=(2, 6))

    ctk.CTkLabel(
        box_oct_controls,
        text="Seleccionar Octante:",
        font=ctk.CTkFont(size=11, weight="bold")
    ).pack(side="left", padx=(4, 8))

    nombres_octantes = [
        "Octante 1: (+X, +Y)",
        "Octante 2: (+Y, +X)",
        "Octante 3: (-Y, +X)",
        "Octante 4: (-X, +Y)",
        "Octante 5: (-X, -Y)",
        "Octante 6: (-Y, -X)",
        "Octante 7: (+Y, -X)",
        "Octante 8: (+X, -Y)",
    ]

    seg_octante = ctk.CTkSegmentedButton(
        box_oct_controls,
        values=["Oct 1", "Oct 2", "Oct 3", "Oct 4", "Oct 5", "Oct 6", "Oct 7", "Oct 8"],
        font=ctk.CTkFont(size=10),
        command=lambda _: actualizar_tabla_octante()
    )
    seg_octante.pack(side="left", padx=4)
    seg_octante.set("Oct 1")

    lbl_oct_desc = ctk.CTkLabel(box_oct_controls, text="", font=ctk.CTkFont(size=11, weight="bold"), text_color=["#2563EB", "#38BDF8"])
    lbl_oct_desc.pack(side="left", padx=12)

    scroll_oct = ctk.CTkScrollableFrame(tab_octantes, fg_color="transparent", corner_radius=8)
    scroll_oct.pack(fill="both", expand=True, padx=4, pady=4)
    tbl_oct_holder = {"table": None}

    encabezado_octante = ["Paso N", "X relativo", "Y relativo", "Fórmula Traslación", "Píxel Resultante (X, Y)"]

    def render_octante_table(rows_data):
        if tbl_oct_holder["table"] is not None:
            tbl_oct_holder["table"].destroy()

        ctk_tbl = CTkTable(
            scroll_oct,
            row=len(rows_data),
            column=len(encabezado_octante),
            width=80,
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
        tbl_oct_holder["table"] = ctk_tbl
        tabs_actualizadas[TAB_OCT_NAME] = True

    # --- TAB 3: LÍNEAS DDA CON PAGINACIÓN INTELIGENTE (MAX RENDIMIENTO) ---
    box_dda_controls = ctk.CTkFrame(tab_dda, fg_color="transparent")
    box_dda_controls.pack(fill="x", padx=4, pady=(2, 6))

    dda_pag_state = {"page": 1, "max_pages": 1}

    def cambiar_pag_dda(delta):
        nueva = dda_pag_state["page"] + delta
        if 1 <= nueva <= dda_pag_state["max_pages"]:
            dda_pag_state["page"] = nueva
            actualizar_tabla_dda()

    btn_prev_dda = ctk.CTkButton(
        box_dda_controls,
        text="◀ Anterior",
        width=70,
        height=26,
        font=ctk.CTkFont(size=10),
        command=lambda: cambiar_pag_dda(-1)
    )
    btn_prev_dda.pack(side="left", padx=4)

    lbl_dda_page = ctk.CTkLabel(
        box_dda_controls,
        text="Página 1 de 1",
        font=ctk.CTkFont(size=11, weight="bold")
    )
    lbl_dda_page.pack(side="left", padx=10)

    btn_next_dda = ctk.CTkButton(
        box_dda_controls,
        text="Siguiente ▶",
        width=70,
        height=26,
        font=ctk.CTkFont(size=10),
        command=lambda: cambiar_pag_dda(1)
    )
    btn_next_dda.pack(side="left", padx=4)

    lbl_dda_info = ctk.CTkLabel(
        box_dda_controls,
        text="",
        font=ctk.CTkFont(size=10),
        text_color="gray"
    )
    lbl_dda_info.pack(side="left", padx=14)

    scroll_dda = ctk.CTkScrollableFrame(tab_dda, fg_color="transparent", corner_radius=8)
    scroll_dda.pack(fill="both", expand=True, padx=4, pady=4)
    tbl_dda_holder = {"table": None}

    encabezado_dda = ["Línea", "Punto A (Centro)", "Punto B (Octante)", "Longitud (u)", "Caso DDA (11 casos)", "Píxeles Encendidos"]

    def render_dda_table(rows_data):
        if tbl_dda_holder["table"] is not None:
            tbl_dda_holder["table"].destroy()

        ctk_tbl = CTkTable(
            scroll_dda,
            row=len(rows_data),
            column=len(encabezado_dda),
            width=70,
            values=rows_data,
            header_color=("#3B82F6", "#1D4ED8"),
            colors=[("gray95", "#21252D"), ("gray90", "#1A1D24")],
            hover=True,
            hover_color=("#BFDBFE", "#1E3A8A"),
            corner_radius=8,
            font=ctk.CTkFont(size=10),
            justify="center"
        )
        ctk_tbl.pack(fill="x", expand=True)
        tbl_dda_holder["table"] = ctk_tbl
        tabs_actualizadas[TAB_DDA_NAME] = True

    def actualizar_tabla_dda():
        if not current_circle_data.get("has_data"):
            return
        lineas = current_circle_data.get("lineas_info", [])
        total = len(lineas)
        max_p = max(1, math.ceil(total / LINEAS_POR_PAGINA_DDA))
        dda_pag_state["max_pages"] = max_p
        cur_p = min(dda_pag_state["page"], max_p)
        dda_pag_state["page"] = cur_p

        lbl_dda_page.configure(text=f"Página {cur_p} de {max_p}")
        btn_prev_dda.configure(state="normal" if cur_p > 1 else "disabled")
        btn_next_dda.configure(state="normal" if cur_p < max_p else "disabled")

        ini = (cur_p - 1) * LINEAS_POR_PAGINA_DDA
        fin = min(ini + LINEAS_POR_PAGINA_DDA, total)
        lbl_dda_info.configure(text=f"Mostrando líneas {ini + 1} a {fin} de {total} totales")

        rows = [encabezado_dda]
        for info in lineas[ini:fin]:
            rows.append([
                str(info["num"]),
                f"({info['a'][0]}, {info['a'][1]})",
                f"({info['b'][0]}, {info['b'][1]})",
                f"{info['dist']:.2f}",
                info["caso"],
                str(info["num_px"])
            ])
        render_dda_table(rows)

    def actualizar_tabla_octante():
        if not current_circle_data.get("has_data"):
            return
        sel = seg_octante.get()
        num_oct = int(sel.replace("Oct ", ""))
        xc = current_circle_data["xc"]
        yc = current_circle_data["yc"]
        pasos = current_circle_data["pasos"]

        formulas_oct = [
            "(Xc + X, Yc + Y)",
            "(Xc + Y, Yc + X)",
            "(Xc - Y, Yc + X)",
            "(Xc - X, Yc + Y)",
            "(Xc - X, Yc - Y)",
            "(Xc - Y, Yc - X)",
            "(Xc + Y, Yc - X)",
            "(Xc + X, Yc - Y)",
        ]
        formula_txt = formulas_oct[num_oct - 1]
        lbl_oct_desc.configure(text=f"{nombres_octantes[num_oct - 1]}  ·  Traslación: {formula_txt}")

        rows = [encabezado_octante]
        for p in pasos:
            k = p["k"]
            xs = p["x_sig"]
            ys = p["y_sig"]
            pt = p["pts"][num_oct - 1]

            if num_oct == 1:
                rel_x, rel_y = xs, ys
                calc_str = f"({xc} + {xs}, {yc} + {ys})"
            elif num_oct == 2:
                rel_x, rel_y = ys, xs
                calc_str = f"({xc} + {ys}, {yc} + {xs})"
            elif num_oct == 3:
                rel_x, rel_y = -ys, xs
                calc_str = f"({xc} - {ys}, {yc} + {xs})"
            elif num_oct == 4:
                rel_x, rel_y = -xs, ys
                calc_str = f"({xc} - {xs}, {yc} + {ys})"
            elif num_oct == 5:
                rel_x, rel_y = -xs, -ys
                calc_str = f"({xc} - {xs}, {yc} - {ys})"
            elif num_oct == 6:
                rel_x, rel_y = -ys, -xs
                calc_str = f"({xc} - {ys}, {yc} - {xs})"
            elif num_oct == 7:
                rel_x, rel_y = ys, -xs
                calc_str = f"({xc} + {ys}, {yc} - {xs})"
            else:
                rel_x, rel_y = xs, -ys
                calc_str = f"({xc} + {xs}, {yc} - {ys})"

            rows.append([str(k), str(rel_x), str(rel_y), calc_str, f"({pt[0]}, {pt[1]})"])

        render_octante_table(rows)

    def on_tabview_change():
        tab_activa = tabview.get()
        if not tabs_actualizadas.get(tab_activa, False):
            if tab_activa == TAB_GEN_NAME:
                actualizar_tabla_general()
            elif tab_activa == TAB_OCT_NAME:
                actualizar_tabla_octante()
            elif tab_activa == TAB_DDA_NAME:
                actualizar_tabla_dda()

    def actualizar_tabla_general():
        if not current_circle_data.get("has_data"):
            return
        pasos = current_circle_data["pasos"]
        rows_gen = [encabezado_general]
        for p in pasos:
            n_str = str(p["k"])
            pk_str = f"{p['pk']:g}"
            formula_str = p["formula"]
            xk_base = f"{p['x_sig']}"
            yk_base = f"{p['y_sig']}"
            trans_str = f"({p['base_trans'][0]}, {p['base_trans'][1]})"
            pts = p["pts"]
            row = [
                n_str,
                pk_str,
                formula_str,
                f"{xk_base} + Xc",
                f"{yk_base} + Yc",
                trans_str,
                f"({pts[0][0]}, {pts[0][1]})",
                f"({pts[1][0]}, {pts[1][1]})",
                f"({pts[2][0]}, {pts[2][1]})",
                f"({pts[3][0]}, {pts[3][1]})",
                f"({pts[4][0]}, {pts[4][1]})",
                f"({pts[5][0]}, {pts[5][1]})",
                f"({pts[6][0]}, {pts[6][1]})",
                f"({pts[7][0]}, {pts[7][1]})"
            ]
            rows_gen.append(row)
        render_general_table(rows_gen)

    # --- LÓGICA DE CONTROL ---
    def calculate():
        try:
            xc = float(entryXC.get().strip())
            yc = float(entryYC.get().strip())
            r = float(entryR.get().strip())

            if xc.is_integer(): xc = int(xc)
            if yc.is_integer(): yc = int(yc)
            if r.is_integer(): r = int(r)
        except ValueError:
            messagebox.showerror("Dato Inválido", "Por favor ingresa valores numéricos válidos para Centro (Xc, Yc) y Radio (R).")
            return

        if r <= 0:
            messagebox.showwarning("Radio Inválido", "El radio (R) debe ser un número positivo mayor a 0.")
            return

        # 1. Algoritmo de punto medio de Bresenham
        pasos, pixeles_contorno, puntos_ordenados, octantes_dict = algoritmo_punto_medio_circunferencia(xc, yc, r)

        # 2. Algoritmos de Relleno según el método seleccionado
        metodo = opt_metodo.get()
        lineas_info = []
        if "DDA Radial" in metodo:
            segmentos_relleno, pixeles_relleno, lineas_info = generar_relleno_dda_radial(xc, yc, puntos_ordenados)
        elif "Cuerdas" in metodo:
            segmentos_relleno, pixeles_relleno = generar_relleno_cuerdas_scanlines(xc, yc, r, pixeles_contorno)
        else:  # Concéntrico
            segmentos_relleno, pixeles_relleno = generar_relleno_concentrico(xc, yc, r)

        # 3. Métricas analíticas
        ordinaria, explicita, general = get_ecuaciones_circunferencia(xc, yc, r)
        perimetro = 2.0 * math.pi * r
        area = math.pi * (r ** 2)
        diametro = 2.0 * r
        p0_val = 1 - r

        # 4. Guardar en estado global
        current_circle_data.clear()
        current_circle_data.update({
            "has_data": True,
            "xc": xc,
            "yc": yc,
            "r": r,
            "p0": p0_val,
            "modo_vista": seg_modo.get(),
            "metodo_relleno": metodo,
            "pasos": pasos,
            "pixeles_contorno": pixeles_contorno,
            "puntos_ordenados": puntos_ordenados,
            "octantes_dict": octantes_dict,
            "segmentos_relleno": segmentos_relleno,
            "pixeles_relleno": pixeles_relleno,
            "lineas_info": lineas_info,
        })

        # 5. Actualizar Tarjetas
        cards["ec_ord"]["val"].configure(text=ordinaria)
        cards["ec_ord"]["sub"].configure(text=f"Primer punto (0, r): ({xc:g}, {yc + r:g})")

        cards["ec_exp"]["val"].configure(text=explicita)
        cards["ec_exp"]["sub"].configure(text=f"Ecuación general: {general}")

        cards["geom"]["val"].configure(text=f"Área: {area:.2f} u²")
        cards["geom"]["sub"].configure(text=f"Perímetro: {perimetro:.2f} u · Diám: {diametro:g}")

        cards["pix"]["val"].configure(text=f"{len(pasos)} pasos · P₀ = {p0_val}")
        cards["pix"]["sub"].configure(text=f"{len(pixeles_contorno)} px borde · {len(pixeles_relleno)} px relleno")

        # 6. Actualizar Gráfica
        render_circle_plot(ax, figure, canvas)

        # 7. Invalidar estado de tablas para lazy loading y actualizar solo la activa
        tabs_actualizadas[TAB_GEN_NAME] = False
        tabs_actualizadas[TAB_OCT_NAME] = False
        tabs_actualizadas[TAB_DDA_NAME] = False
        dda_pag_state["page"] = 1

        tab_activa = tabview.get()
        if tab_activa == TAB_GEN_NAME:
            actualizar_tabla_general()
        elif tab_activa == TAB_OCT_NAME:
            actualizar_tabla_octante()
        elif tab_activa == TAB_DDA_NAME:
            actualizar_tabla_dda()

    def on_mode_change():
        if current_circle_data.get("has_data"):
            current_circle_data["modo_vista"] = seg_modo.get()
            view = (ax.get_xlim(), ax.get_ylim())
            render_circle_plot(ax, figure, canvas, view=view)

    def on_method_change():
        calculate()

    def restablecer_vista_circulo():
        if current_circle_data.get("has_data"):
            xc = current_circle_data["xc"]
            yc = current_circle_data["yc"]
            r = current_circle_data["r"]
            span = max(r * 1.5, 12)
            ax.set_xlim(xc - span, xc + span)
            ax.set_ylim(yc - span, yc + span)
        else:
            ax.set_xlim(-15, 15)
            ax.set_ylim(-15, 15)
        canvas.draw_idle()

    def vista_completa_origen():
        if current_circle_data.get("has_data"):
            xc = current_circle_data["xc"]
            yc = current_circle_data["yc"]
            r = current_circle_data["r"]
            min_x = min(0, xc - r)
            max_x = max(0, xc + r)
            min_y = min(0, yc - r)
            max_y = max(0, yc + r)
            margin_x = max((max_x - min_x) * 0.15, 5)
            margin_y = max((max_y - min_y) * 0.15, 5)
            ax.set_xlim(min_x - margin_x, max_x + margin_x)
            ax.set_ylim(min_y - margin_y, max_y + margin_y)
        else:
            ax.set_xlim(-20, 20)
            ax.set_ylim(-20, 20)
        canvas.draw_idle()

    def on_theme_updated():
        view = (ax.get_xlim(), ax.get_ylim())
        render_circle_plot(ax, figure, canvas, view=view)

    register_plot_updater(on_theme_updated)

    # Calcular valores iniciales al abrir
    calculate()

    return page
