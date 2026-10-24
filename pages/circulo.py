"""
Página de Trazo de Circunferencia y Círculo Relleno.
La lógica (Bresenham, octantes, rellenos y ecuaciones) está en core/circulo.py.
Las tablas viven en pestañas que se generan solo al abrirse (lazy) y la de
líneas DDA está paginada para que la interfaz siga fluida con radios grandes.
"""
import math
from tkinter import messagebox
import customtkinter as ctk

from matplotlib.collections import LineCollection
from matplotlib.patches import Circle

from core.circulo import (
    METODOS_RELLENO,
    analizar_circulo,
    fila_octante,
    formula_octante,
    nombre_octante,
)
from core.recta import redondear_pixel
from ui.plano import anotar_punto, aplicar_vista, crear_plano, dibujar_leyenda, setup_ejes
from ui.tema import es_oscuro, register_plot_updater
from ui.widgets import (
    ALTURA_GRAFICA,
    BORDE_TARJETA,
    ESTILO_SECUNDARIO,
    TablaDinamica,
    boton_primario,
    crear_pagina,
    encabezado_grafica,
    escribir_valores,
    grupo_entradas,
    leer_numeros,
    tarjeta,
)

# Estado reactivo global del módulo de circunferencia
current_circle_data = {}

ALTURA_TABLA_CIRCULO = 450
LINEAS_POR_PAGINA_DDA = 25

# Cómo se dibuja el relleno. False: rectas ideales de C a cada B, como la figura
# del documento. True: cada línea une los píxeles que encendió el DDA (escalonado
# al acercar, igual que en la recta y el triángulo). Los cálculos no cambian.
RELLENO_ESCALONADO = False

ENCABEZADO_GENERAL = [
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
ENCABEZADO_OCTANTE = ["Paso N", "X relativo", "Y relativo", "Fórmula Traslación", "Píxel Resultante (X, Y)"]
ENCABEZADO_DDA = ["Línea", "Punto A (Centro)", "Punto B (Octante)", "Longitud (u)", "Caso DDA (11 casos)", "Píxeles Encendidos"]


def lineas_de_relleno(datos, escalonado=RELLENO_ESCALONADO):
    """
    Líneas a dibujar para el relleno. Escalonado: los píxeles de cada línea tal
    como los calculó core/circulo.py. Ideal: radiales rectas de C a B y anillos
    concéntricos como circunferencias continuas (las cuerdas ya son rectas).
    """
    lineas = datos["segmentos_relleno"]
    if escalonado:
        return lineas

    metodo = datos["metodo_relleno"]
    if "DDA Radial" in metodo:
        return [(linea[0], linea[-1]) for linea in lineas]
    if "Concéntrico" in metodo:
        xc, yc = redondear_pixel(datos["xc"]), redondear_pixel(datos["yc"])
        angulos = [2 * math.pi * i / 72 for i in range(73)]
        return [
            [(xc + rad * math.cos(a), yc + rad * math.sin(a)) for a in angulos]
            for rad in range(1, len(lineas) + 1)
        ]
    return lineas


def render_circle_plot(ax, figure, canvas, view=None, escalonado=RELLENO_ESCALONADO):
    """
    Renderiza la circunferencia y el círculo relleno en el plano cartesiano.
    Sin view, encuadra el círculo; con view = (xlim, ylim) conserva la vista actual.
    escalonado elige cómo se dibujan las líneas de relleno (ver RELLENO_ESCALONADO).
    """
    is_dark = es_oscuro()
    color_centro = "#F59E0B" if is_dark else "#D97706"
    color_primer_pto = "#10B981" if is_dark else "#059669"
    color_contorno = "#38BDF8" if is_dark else "#0284C7"
    color_relleno = "#EAB308" if is_dark else "#CA8A04"
    color_ideal = "#64748B" if is_dark else "#94A3B8"

    ax.clear()
    limit = current_circle_data.get("limit", 20)
    setup_ejes(ax, figure, limit=limit, is_dark=is_dark)

    if current_circle_data.get("has_data"):
        xc = current_circle_data["xc"]
        yc = current_circle_data["yc"]
        r = current_circle_data["r"]
        modo_vista = current_circle_data.get("modo_vista", "Ambos")
        metodo_relleno = current_circle_data.get("metodo_relleno", METODOS_RELLENO[0])
        mostrar_contorno = modo_vista in ("Ambos", "Solo Contorno")
        mostrar_relleno = modo_vista in ("Ambos", "Solo Relleno")

        pixeles_contorno = current_circle_data["pixeles_contorno"]
        segmentos_relleno = current_circle_data.get("segmentos_relleno", [])
        pixeles_relleno = current_circle_data.get("pixeles_relleno", set())

        # 1. Círculo continuo de referencia
        ax.add_patch(Circle(
            (xc, yc),
            r,
            fill=False,
            edgecolor=color_ideal,
            linestyle="--",
            linewidth=1.2,
            alpha=0.6,
            label=f"Radio continuo (R={r:g})"
        ))

        # 2. Relleno con las líneas del método (sin disco sólido)
        if mostrar_relleno and segmentos_relleno:
            if "DDA Radial" in metodo_relleno:
                etiqueta = f"Relleno: líneas DDA desde C ({len(segmentos_relleno)} líneas, {len(pixeles_relleno)} px)"
            elif "Cuerdas" in metodo_relleno:
                etiqueta = f"Relleno: cuerdas ({len(segmentos_relleno)} líneas, {len(pixeles_relleno)} px)"
            else:
                etiqueta = f"Relleno: círculos concéntricos ({len(segmentos_relleno)} anillos, {len(pixeles_relleno)} px)"
            ax.add_collection(LineCollection(
                lineas_de_relleno(current_circle_data, escalonado),
                colors=color_relleno,
                linewidths=0.9,
                alpha=0.55,
                zorder=2,
                label=etiqueta
            ))

        # 3. Píxeles del contorno (Punto Medio Bresenham en 8 Octantes)
        if mostrar_contorno and pixeles_contorno:
            ax.scatter(
                [pt[0] for pt in pixeles_contorno],
                [pt[1] for pt in pixeles_contorno],
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
        ax.plot(
            [xc], [yc + r],
            marker="^",
            markersize=9,
            color=color_primer_pto,
            markeredgecolor="#FFFFFF",
            markeredgewidth=1.2,
            zorder=5,
            label=f"(0, r) = ({xc:g}, {yc + r:g})"
        )

        # 5. Centro trasladado (Xc, Yc) con líneas guía a los ejes
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
        anotar_punto(ax, f"C ({xc:g}, {yc:g})", xc, yc, color_centro, is_dark, zorder=6)

        dibujar_leyenda(ax, is_dark)

    if view is not None:
        aplicar_vista(ax, view)
    elif current_circle_data.get("has_data"):
        encuadrar_circulo(ax)

    figure.tight_layout()
    canvas.draw_idle()


def encuadrar_circulo(ax):
    xc = current_circle_data["xc"]
    yc = current_circle_data["yc"]
    span = max(current_circle_data["r"] * 1.5, 12)
    ax.set_xlim(xc - span, xc + span)
    ax.set_ylim(yc - span, yc + span)


def _tarjeta_metrica(parent, col, titulo, valor_inicial, subtexto):
    """Tarjeta con borde propia de esta página (texto más compacto que TileMetrica)."""
    card = ctk.CTkFrame(parent, corner_radius=10, border_width=1, border_color=BORDE_TARJETA)
    card.grid(row=0, column=col, padx=(0 if col == 0 else 4, 0 if col == 3 else 4), sticky="nsew")

    ctk.CTkLabel(card, text=titulo, font=ctk.CTkFont(size=10, weight="bold"), text_color="gray", anchor="w").pack(fill="x", padx=10, pady=(8, 1))
    lbl_v = ctk.CTkLabel(card, text=valor_inicial, font=ctk.CTkFont(size=13, weight="bold"), anchor="w")
    lbl_v.pack(fill="x", padx=10, pady=(0, 1))
    lbl_s = ctk.CTkLabel(card, text=subtexto, font=ctk.CTkFont(size=10), text_color="gray", anchor="w")
    lbl_s.pack(fill="x", padx=10, pady=(0, 8))
    return {"val": lbl_v, "sub": lbl_s}


def create_circulo_page(container):
    """
    Construye la página de Trazo de Circunferencia y Círculo Relleno con
    visualizador interactivo y pestañas de tablas generadas bajo demanda.
    """
    page, body = crear_pagina(
        container,
        "Trazo de Circunferencia y Círculo Relleno",
        "Algoritmo de Punto Medio de Bresenham · Simetría de 8 Octantes · Traslación Bidimensional C(Xc, Yc) · Relleno DDA Radial y Scanline.",
    )

    # --- 1. FORMULARIO (INPUTS) ---
    form_card = tarjeta(body)
    form_card.pack(fill="x", padx=20, pady=(0, 8))

    form_top = ctk.CTkFrame(form_card, fg_color="transparent")
    form_top.pack(fill="x", padx=16, pady=8)

    entryXC, entryYC = grupo_entradas(form_top, "Centro Trasladado (Xc, Yc)", ("Xc:", "Yc:"), separacion=10)
    (entryR,) = grupo_entradas(form_top, "Dimensión", ("Radio (R):",))
    entradas = (entryXC, entryYC, entryR)
    escribir_valores(entradas, (150, 100, 10))

    # Método de Relleno
    box_fill_method = ctk.CTkFrame(form_top, fg_color="transparent")
    box_fill_method.pack(side="left", padx=(0, 16))
    ctk.CTkLabel(box_fill_method, text="Método de Relleno", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(0, 4))
    opt_metodo = ctk.CTkOptionMenu(
        box_fill_method,
        values=list(METODOS_RELLENO),
        font=ctk.CTkFont(size=11),
        width=230,
        height=32,
        command=lambda _: calculate()
    )
    opt_metodo.pack(anchor="w")

    # Modo de Visualización
    box_mode = ctk.CTkFrame(form_top, fg_color="transparent")
    box_mode.pack(side="left", padx=(0, 16))
    ctk.CTkLabel(box_mode, text="Visualización", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(0, 4))
    seg_modo = ctk.CTkSegmentedButton(
        box_mode,
        values=["Ambos", "Solo Contorno", "Solo Relleno"],
        font=ctk.CTkFont(size=11),
        height=32,
        command=lambda _: on_mode_change()
    )
    seg_modo.pack(anchor="w")
    seg_modo.set("Ambos")

    # Botón de Acción
    box_btn = ctk.CTkFrame(form_top, fg_color="transparent")
    box_btn.pack(side="right", padx=(10, 0))
    boton_primario(
        box_btn, " Calcular y Trazar", lambda: calculate(), icon_size=16, fg_color=["#3B82F6", "#2563EB"]
    ).pack(side="left", padx=(0, 8))

    # Barra inferior de plantillas y traslación interactiva
    trans_bar = ctk.CTkFrame(form_card, fg_color=("gray95", "gray17"), corner_radius=8)
    trans_bar.pack(fill="x", padx=16, pady=(0, 8))

    ctk.CTkLabel(trans_bar, text="Plantillas de Prueba:", font=ctk.CTkFont(size=11, weight="bold"), text_color="gray").pack(side="left", padx=(10, 6), pady=4)

    def cargar_ejemplo(xc, yc, r):
        escribir_valores(entradas, (xc, yc, r))
        calculate()

    ctk.CTkButton(
        trans_bar,
        text="Ejemplo 1: C(150, 100), R=10",
        height=24,
        font=ctk.CTkFont(size=10, weight="bold"),
        fg_color=["#3B82F6", "#1D4ED8"],
        command=lambda: cargar_ejemplo(150, 100, 10)
    ).pack(side="left", padx=3, pady=4)

    for texto, valores in (("Ejemplo 2: C(100, 100), R=51", (100, 100, 51)), ("Origen: C(0, 0), R=10", (0, 0, 10))):
        ctk.CTkButton(
            trans_bar,
            text=texto,
            height=24,
            font=ctk.CTkFont(size=10),
            command=lambda v=valores: cargar_ejemplo(*v),
            **ESTILO_SECUNDARIO
        ).pack(side="left", padx=3, pady=4)

    # Traslación interactiva del centro
    ctk.CTkFrame(trans_bar, width=1, height=18, fg_color=("gray80", "gray35")).pack(side="left", padx=8, pady=4)
    ctk.CTkLabel(trans_bar, text="Trasladar Centro:", font=ctk.CTkFont(size=11, weight="bold"), text_color="gray").pack(side="left", padx=(2, 6), pady=4)

    def trasladar_centro(dx, dy):
        try:
            cur_xc = float(entryXC.get().strip())
            cur_yc = float(entryYC.get().strip())
        except ValueError:
            return
        escribir_valores((entryXC, entryYC), (int(round(cur_xc + dx)), int(round(cur_yc + dy))))
        calculate()

    for txt, dx, dy in (("◀ X - 5", -5, 0), ("X + 5 ▶", 5, 0), ("▼ Y - 5", 0, -5), ("▲ Y + 5", 0, 5)):
        ctk.CTkButton(
            trans_bar,
            text=txt,
            width=58,
            height=24,
            font=ctk.CTkFont(size=10),
            command=lambda x=dx, y=dy: trasladar_centro(x, y),
            **ESTILO_SECUNDARIO
        ).pack(side="left", padx=2, pady=4)

    # --- 2. TARJETAS DE MÉTRICAS ANALÍTICAS ---
    metrics_frame = ctk.CTkFrame(body, corner_radius=0, fg_color="transparent")
    metrics_frame.pack(fill="x", padx=20, pady=(0, 8))
    metrics_frame.columnconfigure((0, 1, 2, 3), weight=1, uniform="metric")

    cards = {
        "ec_ord": _tarjeta_metrica(metrics_frame, 0, "ECUACIÓN ORDINARIA", "(X - 150)² + (Y - 100)² = 100", "Primer punto (0, r): (150, 110)"),
        "ec_exp": _tarjeta_metrica(metrics_frame, 1, "ECUACIÓN EXPLÍCITA", "Y = 100 ± √(100 - (150 - X)²)", "Y = Yc ± √(r² - (Xc - X)²)"),
        "geom": _tarjeta_metrica(metrics_frame, 2, "MÉTRICAS GEOMÉTRICAS", "Área: 314.16 u²", "Perímetro: 62.83 u · Diám: 20"),
        "pix": _tarjeta_metrica(metrics_frame, 3, "PÍXELES Y OCTANTES", "7 pasos · P₀ = -9", "Simetría de 8 Octantes con Traslación"),
    }

    # --- 3. GRÁFICA / PLANO CARTESIANO ---
    graph_card = tarjeta(body, height=ALTURA_GRAFICA)
    graph_card.pack(fill="x", padx=20, pady=(0, 8))
    graph_card.pack_propagate(False)
    encabezado_grafica(
        graph_card,
        "  Visualizador de Circunferencia, Octantes y Relleno",
        "grid-dots",
        lambda: restablecer_vista_circulo(),
        texto_centrar=" Centrar en Círculo",
        extras=[(" Ver con Origen (0,0)", lambda: vista_completa_origen())],
        pady=8,
    )
    figure, ax, canvas = crear_plano(graph_card, body, limit=20)

    # --- 4. PESTAÑAS DE TABLAS (se generan al abrirse) ---
    tabview_card = tarjeta(body, height=ALTURA_TABLA_CIRCULO)
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

    # Pestañas ya generadas con los datos actuales
    tabs_actualizadas = {TAB_GEN_NAME: False, TAB_OCT_NAME: False, TAB_DDA_NAME: False}

    # --- TAB 1: GENERAL ---
    scroll_gen = ctk.CTkScrollableFrame(tab_general, fg_color="transparent", corner_radius=8)
    scroll_gen.pack(fill="both", expand=True, padx=4, pady=4)
    tabla_general = TablaDinamica(scroll_gen, width=54, font_size=10)

    # --- TAB 2: OCTANTES DE SIMETRÍA ---
    box_oct_controls = ctk.CTkFrame(tab_octantes, fg_color="transparent")
    box_oct_controls.pack(fill="x", padx=4, pady=(2, 6))

    ctk.CTkLabel(box_oct_controls, text="Seleccionar Octante:", font=ctk.CTkFont(size=11, weight="bold")).pack(side="left", padx=(4, 8))

    seg_octante = ctk.CTkSegmentedButton(
        box_oct_controls,
        values=[f"Oct {n}" for n in range(1, 9)],
        font=ctk.CTkFont(size=10),
        command=lambda _: actualizar_tabla_octante()
    )
    seg_octante.pack(side="left", padx=4)
    seg_octante.set("Oct 1")

    lbl_oct_desc = ctk.CTkLabel(box_oct_controls, text="", font=ctk.CTkFont(size=11, weight="bold"), text_color=["#2563EB", "#38BDF8"])
    lbl_oct_desc.pack(side="left", padx=12)

    scroll_oct = ctk.CTkScrollableFrame(tab_octantes, fg_color="transparent", corner_radius=8)
    scroll_oct.pack(fill="both", expand=True, padx=4, pady=4)
    tabla_octante = TablaDinamica(scroll_oct, width=80, font_size=11)

    # --- TAB 3: LÍNEAS DDA PAGINADAS ---
    box_dda_controls = ctk.CTkFrame(tab_dda, fg_color="transparent")
    box_dda_controls.pack(fill="x", padx=4, pady=(2, 6))

    dda_pag_state = {"page": 1, "max_pages": 1}

    def cambiar_pag_dda(delta):
        nueva = dda_pag_state["page"] + delta
        if 1 <= nueva <= dda_pag_state["max_pages"]:
            dda_pag_state["page"] = nueva
            actualizar_tabla_dda()

    btn_prev_dda = ctk.CTkButton(box_dda_controls, text="◀ Anterior", width=70, height=26, font=ctk.CTkFont(size=10), command=lambda: cambiar_pag_dda(-1))
    btn_prev_dda.pack(side="left", padx=4)

    lbl_dda_page = ctk.CTkLabel(box_dda_controls, text="Página 1 de 1", font=ctk.CTkFont(size=11, weight="bold"))
    lbl_dda_page.pack(side="left", padx=10)

    btn_next_dda = ctk.CTkButton(box_dda_controls, text="Siguiente ▶", width=70, height=26, font=ctk.CTkFont(size=10), command=lambda: cambiar_pag_dda(1))
    btn_next_dda.pack(side="left", padx=4)

    lbl_dda_info = ctk.CTkLabel(box_dda_controls, text="", font=ctk.CTkFont(size=10), text_color="gray")
    lbl_dda_info.pack(side="left", padx=14)

    scroll_dda = ctk.CTkScrollableFrame(tab_dda, fg_color="transparent", corner_radius=8)
    scroll_dda.pack(fill="both", expand=True, padx=4, pady=4)
    tabla_dda = TablaDinamica(scroll_dda, width=70, font_size=10)

    def actualizar_tabla_general():
        if not current_circle_data.get("has_data"):
            return
        rows = [ENCABEZADO_GENERAL]
        for p in current_circle_data["pasos"]:
            rows.append([
                str(p["k"]),
                f"{p['pk']:g}",
                p["formula"],
                f"{p['x_sig']} + Xc",
                f"{p['y_sig']} + Yc",
                f"({p['base_trans'][0]}, {p['base_trans'][1]})",
                *(f"({x}, {y})" for x, y in p["pts"]),
            ])
        tabla_general.mostrar(rows)
        tabs_actualizadas[TAB_GEN_NAME] = True

    def actualizar_tabla_octante():
        if not current_circle_data.get("has_data"):
            return
        num_oct = int(seg_octante.get().replace("Oct ", ""))
        xc = current_circle_data["xc"]
        yc = current_circle_data["yc"]
        lbl_oct_desc.configure(text=f"{nombre_octante(num_oct)}  ·  Traslación: {formula_octante(num_oct)}")

        rows = [ENCABEZADO_OCTANTE]
        for p in current_circle_data["pasos"]:
            rows.append(fila_octante(p, num_oct, xc, yc))
        tabla_octante.mostrar(rows)
        tabs_actualizadas[TAB_OCT_NAME] = True

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

        rows = [ENCABEZADO_DDA]
        for info in lineas[ini:fin]:
            rows.append([
                str(info["num"]),
                f"({info['a'][0]}, {info['a'][1]})",
                f"({info['b'][0]}, {info['b'][1]})",
                f"{info['dist']:.2f}",
                info["caso"],
                str(info["num_px"])
            ])
        tabla_dda.mostrar(rows)
        tabs_actualizadas[TAB_DDA_NAME] = True

    actualizadores = {
        TAB_GEN_NAME: actualizar_tabla_general,
        TAB_OCT_NAME: actualizar_tabla_octante,
        TAB_DDA_NAME: actualizar_tabla_dda,
    }

    def on_tabview_change():
        tab_activa = tabview.get()
        if not tabs_actualizadas.get(tab_activa, False):
            actualizadores[tab_activa]()

    # --- LÓGICA DE CONTROL ---
    def calculate():
        try:
            xc, yc, r = leer_numeros(entradas)
        except ValueError:
            messagebox.showerror("Dato Inválido", "Por favor ingresa valores numéricos válidos para Centro (Xc, Yc) y Radio (R).")
            return

        if r <= 0:
            messagebox.showwarning("Radio Inválido", "El radio (R) debe ser un número positivo mayor a 0.")
            return

        datos = analizar_circulo(xc, yc, r, opt_metodo.get())
        current_circle_data.clear()
        current_circle_data.update(datos, has_data=True, modo_vista=seg_modo.get())

        cards["ec_ord"]["val"].configure(text=datos["ordinaria"])
        cards["ec_ord"]["sub"].configure(text=f"Primer punto (0, r): ({xc:g}, {yc + r:g})")

        cards["ec_exp"]["val"].configure(text=datos["explicita"])
        cards["ec_exp"]["sub"].configure(text=f"Ecuación general: {datos['general']}")

        cards["geom"]["val"].configure(text=f"Área: {datos['area']:.2f} u²")
        cards["geom"]["sub"].configure(text=f"Perímetro: {datos['perimetro']:.2f} u · Diám: {datos['diametro']:g}")

        cards["pix"]["val"].configure(text=f"{len(datos['pasos'])} pasos · P₀ = {datos['p0']}")
        cards["pix"]["sub"].configure(
            text=f"{len(datos['pixeles_contorno'])} px borde · {len(datos['pixeles_relleno'])} px relleno"
                 f" · {len(datos['pixeles_huecos'])} huecos"
        )

        render_circle_plot(ax, figure, canvas)

        # Las tablas quedan desactualizadas; solo se regenera la pestaña visible
        for tab in tabs_actualizadas:
            tabs_actualizadas[tab] = False
        dda_pag_state["page"] = 1
        actualizadores[tabview.get()]()

    def on_mode_change():
        if current_circle_data.get("has_data"):
            current_circle_data["modo_vista"] = seg_modo.get()
            render_circle_plot(ax, figure, canvas, view=(ax.get_xlim(), ax.get_ylim()))

    def restablecer_vista_circulo():
        if current_circle_data.get("has_data"):
            encuadrar_circulo(ax)
        else:
            ax.set_xlim(-15, 15)
            ax.set_ylim(-15, 15)
        canvas.draw_idle()

    def vista_completa_origen():
        if current_circle_data.get("has_data"):
            xc = current_circle_data["xc"]
            yc = current_circle_data["yc"]
            r = current_circle_data["r"]
            min_x, max_x = min(0, xc - r), max(0, xc + r)
            min_y, max_y = min(0, yc - r), max(0, yc + r)
            margin_x = max((max_x - min_x) * 0.15, 5)
            margin_y = max((max_y - min_y) * 0.15, 5)
            ax.set_xlim(min_x - margin_x, max_x + margin_x)
            ax.set_ylim(min_y - margin_y, max_y + margin_y)
        else:
            ax.set_xlim(-20, 20)
            ax.set_ylim(-20, 20)
        canvas.draw_idle()

    def on_theme_updated():
        render_circle_plot(ax, figure, canvas, view=(ax.get_xlim(), ax.get_ylim()))

    register_plot_updater(on_theme_updated)

    # Calcular valores iniciales al abrir
    calculate()

    return page
