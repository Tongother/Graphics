import math
from tkinter import messagebox
import customtkinter as ctk
from CTkTable import CTkTable

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from pages.icons import get_icon

# Almacenamiento de datos actuales para repintado reactivo
current_data = {}
_plot_callbacks = []


def register_plot_updater(callback):
    if callback not in _plot_callbacks:
        _plot_callbacks.append(callback)


def notify_theme_to_plot():
    for cb in _plot_callbacks:
        try:
            cb()
        except Exception:
            pass


def get_pendiente(x1, y1, x2, y2):
    return (y2 - y1) / (x2 - x1)


def get_ordenada(x1, y1, pendiente):
    return y1 - pendiente * x1


def get_ecuacion_recta(x1, y1, pendiente):
    ordenada = get_ordenada(x1, y1, pendiente)
    signo = "+" if ordenada >= 0 else "-"
    return f"y = {pendiente:g}x {signo} {abs(ordenada):g}"


def get_direccion_x(dx):
    if dx > 0:
        return "Izquierda a Derecha"
    elif dx < 0:
        return "Derecha a Izquierda"
    return "Sin cambio horizontal"


def get_direccion_y(dy):
    if dy > 0:
        return "Abajo a Arriba"
    elif dy < 0:
        return "Arriba a Abajo"
    return "Horizontal (Constante)"


def get_comportamiento_pendiente(m):
    if m > 0:
        return "Ascendente"
    elif m < 0:
        return "Descendente"
    return "Horizontal"


def generar_puntos_trayectoria(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    pasos = int(max(abs(dx), abs(dy)))
    puntos = []

    if pasos == 0:
        return [(0, x1, y1)]

    step_x = dx / pasos
    step_y = dy / pasos

    for i in range(pasos + 1):
        px = x1 + i * step_x
        py = y1 + i * step_y
        if abs(px - round(px)) < 1e-7:
            px = int(round(px))
        else:
            px = round(px, 4)
        if abs(py - round(py)) < 1e-7:
            py = int(round(py))
        else:
            py = round(py, 4)
        puntos.append((i, px, py))

    return puntos


def plot_points(x1, x2, y1, pendiente, limit):
    ordenada = get_ordenada(x1, y1, pendiente)
    x_line = [-limit, limit]
    y_line = [pendiente * (-limit) + ordenada, pendiente * limit + ordenada]
    return {"X": x_line, "Y": y_line}


def setup_ejes(ax, figure, limit=10, is_dark=True):
    fig_bg = "#2B2B2B" if is_dark else "#F2F2F2"
    ax_bg = "#1A1A1A" if is_dark else "#FFFFFF"
    text_color = "#E0E0E0" if is_dark else "#1A1A1A"
    subtext = "#9E9E9E" if is_dark else "#616161"
    grid_color = "#2E2E2E" if is_dark else "#E0E0E0"
    origin_color = "#616161" if is_dark else "#9E9E9E"
    spine_color = "#444444" if is_dark else "#D0D0D0"

    figure.patch.set_facecolor(fig_bg)
    ax.set_facecolor(ax_bg)

    ax.set_title("Plano Cartesiano", color=text_color, fontsize=12, fontweight="bold", pad=12)
    ax.set_xlabel("Eje X", color=subtext, fontsize=10, labelpad=6)
    ax.set_ylabel("Eje Y", color=subtext, fontsize=10, labelpad=6)

    ax.tick_params(colors=subtext, labelsize=9)
    for spine in ax.spines.values():
        spine.set_color(spine_color)
        spine.set_linewidth(0.8)

    ax.grid(True, linestyle="--", linewidth=0.6, color=grid_color, alpha=0.7)
    ax.axhline(0, color=origin_color, linewidth=1.0, linestyle="-")
    ax.axvline(0, color=origin_color, linewidth=1.0, linestyle="-")
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    ax.set_aspect("equal", adjustable="box")


def render_plot(ax, figure, canvas):
    is_dark = (ctk.get_appearance_mode().lower() == "dark")
    line_color = "#3B82F6" if is_dark else "#2563EB"
    pt_color = "#38BDF8" if is_dark else "#0284C7"
    pt_a_color = "#34D399" if is_dark else "#059669"
    pt_b_color = "#A78BFA" if is_dark else "#7C3AED"
    fig_bg = "#2B2B2B" if is_dark else "#F2F2F2"
    border_color = "#444444" if is_dark else "#D0D0D0"
    text_color = "#E0E0E0" if is_dark else "#1A1A1A"

    ax.clear()
    limit = current_data.get("limit", 10)
    setup_ejes(ax, figure, limit=limit, is_dark=is_dark)

    if current_data.get("has_data"):
        points = current_data["points"]
        table_points = current_data["table_points"]
        x1, y1 = current_data["x1"], current_data["y1"]
        x2, y2 = current_data["x2"], current_data["y2"]
        equation = current_data["equation"]

        # Recta continua
        ax.plot(
            points["X"], points["Y"],
            color=line_color,
            linewidth=2.4,
            label=f"Recta: {equation}"
        )

        # Puntos de trayectoria
        if table_points and len(table_points) > 2:
            t_x = [pt[1] for pt in table_points]
            t_y = [pt[2] for pt in table_points]
            ax.plot(
                t_x, t_y,
                marker="o",
                markersize=4.5,
                color=pt_color,
                linestyle="None",
                alpha=0.6,
                label="Puntos de trayectoria"
            )

        # Punto A y Punto B
        ax.plot([x1], [y1], marker="o", markersize=9, color=pt_a_color, linestyle="None", label=f"A ({x1:g}, {y1:g})")
        ax.plot([x2], [y2], marker="s", markersize=9, color=pt_b_color, linestyle="None", label=f"B ({x2:g}, {y2:g})")

        # Anotaciones
        bbox_a = dict(boxstyle="round,pad=0.35", fc=fig_bg, ec=pt_a_color, lw=1.2, alpha=0.95)
        ax.annotate(
            f"A ({x1:g}, {y1:g})",
            (x1, y1),
            textcoords="offset points",
            xytext=(0, 14),
            ha="center",
            fontsize=9,
            fontweight="bold",
            color=pt_a_color,
            bbox=bbox_a
        )

        bbox_b = dict(boxstyle="round,pad=0.35", fc=fig_bg, ec=pt_b_color, lw=1.2, alpha=0.95)
        ax.annotate(
            f"B ({x2:g}, {y2:g})",
            (x2, y2),
            textcoords="offset points",
            xytext=(0, 14),
            ha="center",
            fontsize=9,
            fontweight="bold",
            color=pt_b_color,
            bbox=bbox_b
        )

        legend = ax.legend(
            loc="upper left",
            fontsize=8.5,
            framealpha=0.88,
            facecolor=fig_bg,
            edgecolor=border_color
        )
        for text in legend.get_texts():
            text.set_color(text_color)

    figure.tight_layout()
    canvas.draw()


def create_puntos_colineales_page(container):
    page = ctk.CTkFrame(container, corner_radius=0, fg_color="transparent")

    # --- 1. ENCABEZADO ---
    header_frame = ctk.CTkFrame(page, corner_radius=0, fg_color="transparent")
    header_frame.pack(fill="x", padx=20, pady=(12, 4))

    lbl_title = ctk.CTkLabel(
        header_frame,
        text="Trazado y Análisis de Rectas",
        font=ctk.CTkFont(size=20, weight="bold"),
        anchor="w"
    )
    lbl_title.pack(anchor="w")

    lbl_subtitle = ctk.CTkLabel(
        header_frame,
        text="Cálculo algebraico de pendiente, vector director y rasterización discreta.",
        font=ctk.CTkFont(size=12),
        text_color="gray",
        anchor="w"
    )
    lbl_subtitle.pack(anchor="w", pady=(2, 0))

    # --- 2. TARJETA DE FORMULARIO (INPUTS) ---
    form_card = ctk.CTkFrame(page, corner_radius=12, border_width=1, border_color=("gray85", "gray25"))
    form_card.pack(fill="x", padx=20, pady=(0, 8))

    form_top = ctk.CTkFrame(form_card, fg_color="transparent")
    form_top.pack(fill="x", padx=16, pady=8)

    # Punto A
    box_a = ctk.CTkFrame(form_top, fg_color="transparent")
    box_a.pack(side="left", padx=(0, 16))

    lbl_pt_a = ctk.CTkLabel(box_a, text="Punto A (Origen)", font=ctk.CTkFont(size=12, weight="bold"))
    lbl_pt_a.grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 4))

    lbl_xa = ctk.CTkLabel(box_a, text="X₁:", font=ctk.CTkFont(size=12))
    lbl_xa.grid(row=1, column=0, padx=(0, 4))
    entryXA = ctk.CTkEntry(box_a, width=65, height=32, corner_radius=6, justify="center")
    entryXA.grid(row=1, column=1, padx=(0, 12))

    lbl_ya = ctk.CTkLabel(box_a, text="Y₁:", font=ctk.CTkFont(size=12))
    lbl_ya.grid(row=1, column=2, padx=(0, 4))
    entryYA = ctk.CTkEntry(box_a, width=65, height=32, corner_radius=6, justify="center")
    entryYA.grid(row=1, column=3)

    # Punto B
    box_b = ctk.CTkFrame(form_top, fg_color="transparent")
    box_b.pack(side="left", padx=(0, 20))

    lbl_pt_b = ctk.CTkLabel(box_b, text="Punto B (Destino)", font=ctk.CTkFont(size=12, weight="bold"))
    lbl_pt_b.grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 4))

    lbl_xb = ctk.CTkLabel(box_b, text="X₂:", font=ctk.CTkFont(size=12))
    lbl_xb.grid(row=1, column=0, padx=(0, 4))
    entryXB = ctk.CTkEntry(box_b, width=65, height=32, corner_radius=6, justify="center")
    entryXB.grid(row=1, column=1, padx=(0, 12))

    lbl_yb = ctk.CTkLabel(box_b, text="Y₂:", font=ctk.CTkFont(size=12))
    lbl_yb.grid(row=1, column=2, padx=(0, 4))
    entryYB = ctk.CTkEntry(box_b, width=65, height=32, corner_radius=6, justify="center")
    entryYB.grid(row=1, column=3)

    # Botones con iconos vectoriales
    actions_box = ctk.CTkFrame(form_top, fg_color="transparent")
    actions_box.pack(side="left", fill="y", padx=4)

    icon_play = get_icon("play", size=15, light_color="#FFFFFF", dark_color="#FFFFFF")
    btn_calc = ctk.CTkButton(
        actions_box,
        text="  Calcular Trayectoria",
        image=icon_play,
        compound="left",
        height=34,
        corner_radius=8,
        font=ctk.CTkFont(size=12, weight="bold"),
        command=lambda: calculate()
    )
    btn_calc.pack(side="left", padx=(0, 8), pady=6)

    icon_clear = get_icon("rotate-ccw", size=15, light_color="#1E293B", dark_color="#F8FAFC")
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

    # --- 3. TARJETA DE MÉTRICAS (DATOS SEPARADOS Y DETALLADOS) ---
    metrics_card = ctk.CTkFrame(page, corner_radius=12, border_width=1, border_color=("gray85", "gray25"))
    metrics_card.pack(fill="x", padx=20, pady=(0, 8))
    metrics_card.columnconfigure((0, 1, 2, 3), weight=1, uniform="stat")

    # Tile 1: Pendiente
    tile_m = ctk.CTkFrame(metrics_card, corner_radius=10, fg_color=("gray92", "gray20"))
    tile_m.grid(row=0, column=0, sticky="nsew", padx=6, pady=8)
    ctk.CTkLabel(tile_m, text="PENDIENTE (m)", font=ctk.CTkFont(size=9, weight="bold"), text_color="gray", anchor="w").pack(anchor="w", padx=12, pady=(6, 0))
    val_m_num = ctk.CTkLabel(tile_m, text="--", font=ctk.CTkFont(size=17, weight="bold"), anchor="w")
    val_m_num.pack(anchor="w", padx=12, pady=(1, 0))
    val_m_sub1 = ctk.CTkLabel(tile_m, text="Comportamiento: --", font=ctk.CTkFont(size=10), text_color=("gray30", "gray70"), anchor="w")
    val_m_sub1.pack(anchor="w", padx=12)
    val_m_sub2 = ctk.CTkLabel(tile_m, text="Ángulo: --", font=ctk.CTkFont(size=10), text_color=("gray30", "gray70"), anchor="w")
    val_m_sub2.pack(anchor="w", padx=12, pady=(0, 6))

    # Tile 2: Ecuación
    tile_eq = ctk.CTkFrame(metrics_card, corner_radius=10, fg_color=("gray92", "gray20"))
    tile_eq.grid(row=0, column=1, sticky="nsew", padx=6, pady=8)
    ctk.CTkLabel(tile_eq, text="ECUACIÓN DE LA RECTA", font=ctk.CTkFont(size=9, weight="bold"), text_color="gray", anchor="w").pack(anchor="w", padx=12, pady=(6, 0))
    val_eq_num = ctk.CTkLabel(tile_eq, text="--", font=ctk.CTkFont(size=17, weight="bold"), anchor="w")
    val_eq_num.pack(anchor="w", padx=12, pady=(1, 0))
    val_eq_sub1 = ctk.CTkLabel(tile_eq, text="Ordenada (b): --", font=ctk.CTkFont(size=10), text_color=("gray30", "gray70"), anchor="w")
    val_eq_sub1.pack(anchor="w", padx=12)
    val_eq_sub2 = ctk.CTkLabel(tile_eq, text="Forma: Explícita", font=ctk.CTkFont(size=10), text_color=("gray30", "gray70"), anchor="w")
    val_eq_sub2.pack(anchor="w", padx=12, pady=(0, 6))

    # Tile 3: Incremento X
    tile_dx = ctk.CTkFrame(metrics_card, corner_radius=10, fg_color=("gray92", "gray20"))
    tile_dx.grid(row=0, column=2, sticky="nsew", padx=6, pady=8)
    ctk.CTkLabel(tile_dx, text="INCREMENTO X (ΔX)", font=ctk.CTkFont(size=9, weight="bold"), text_color="gray", anchor="w").pack(anchor="w", padx=12, pady=(6, 0))
    val_dx_num = ctk.CTkLabel(tile_dx, text="--", font=ctk.CTkFont(size=17, weight="bold"), anchor="w")
    val_dx_num.pack(anchor="w", padx=12, pady=(1, 0))
    val_dx_sub1 = ctk.CTkLabel(tile_dx, text="Sentido: --", font=ctk.CTkFont(size=10), text_color=("gray30", "gray70"), anchor="w")
    val_dx_sub1.pack(anchor="w", padx=12)
    val_dx_sub2 = ctk.CTkLabel(tile_dx, text="Magnitud: --", font=ctk.CTkFont(size=10), text_color=("gray30", "gray70"), anchor="w")
    val_dx_sub2.pack(anchor="w", padx=12, pady=(0, 6))

    # Tile 4: Incremento Y
    tile_dy = ctk.CTkFrame(metrics_card, corner_radius=10, fg_color=("gray92", "gray20"))
    tile_dy.grid(row=0, column=3, sticky="nsew", padx=6, pady=8)
    ctk.CTkLabel(tile_dy, text="INCREMENTO Y (ΔY)", font=ctk.CTkFont(size=9, weight="bold"), text_color="gray", anchor="w").pack(anchor="w", padx=12, pady=(6, 0))
    val_dy_num = ctk.CTkLabel(tile_dy, text="--", font=ctk.CTkFont(size=17, weight="bold"), anchor="w")
    val_dy_num.pack(anchor="w", padx=12, pady=(1, 0))
    val_dy_sub1 = ctk.CTkLabel(tile_dy, text="Sentido: --", font=ctk.CTkFont(size=10), text_color=("gray30", "gray70"), anchor="w")
    val_dy_sub1.pack(anchor="w", padx=12)
    val_dy_sub2 = ctk.CTkLabel(tile_dy, text="Magnitud: --", font=ctk.CTkFont(size=10), text_color=("gray30", "gray70"), anchor="w")
    val_dy_sub2.pack(anchor="w", padx=12, pady=(0, 6))

    # --- 4. CONTENIDO INFERIOR: TABLA CTkTable Y PLANO EXPANDIDO ---
    split_box = ctk.CTkFrame(page, corner_radius=0, fg_color="transparent")
    split_box.pack(fill="both", expand=True, padx=20, pady=(0, 12))

    # A) TABLA COMPACTA CON CTkTable
    table_card = ctk.CTkFrame(split_box, width=250, corner_radius=12, border_width=1, border_color=("gray85", "gray25"))
    table_card.pack(side="left", fill="y", padx=(0, 10))
    table_card.pack_propagate(False)

    tbl_header = ctk.CTkFrame(table_card, fg_color="transparent")
    tbl_header.pack(fill="x", padx=12, pady=(10, 2))

    icon_tbl = get_icon("table", size=16, light_color="#1E293B", dark_color="#F8FAFC")
    tbl_title = ctk.CTkLabel(
        tbl_header,
        text="  Puntos Discretos",
        image=icon_tbl,
        compound="left",
        font=ctk.CTkFont(size=12, weight="bold"),
        anchor="w"
    )
    tbl_title.pack(anchor="w")

    tbl_count = ctk.CTkLabel(table_card, text="0 pasos calculados", font=ctk.CTkFont(size=10), text_color="gray", anchor="w")
    tbl_count.pack(fill="x", padx=12, pady=(0, 4))

    # Scrollable frame contenedor de CTkTable
    table_scroll = ctk.CTkScrollableFrame(table_card, fg_color="transparent", corner_radius=8)
    table_scroll.pack(fill="both", expand=True, padx=4, pady=(0, 8))

    default_table_data = [["Paso", "Coord X", "Coord Y"]]
    table_holder = {"table": None}

    def render_table(rows_data):
        if table_holder["table"] is not None:
            table_holder["table"].destroy()

        ctk_tbl = CTkTable(
            table_scroll,
            row=len(rows_data),
            column=3,
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
        table_holder["table"] = ctk_tbl

    render_table(default_table_data)

    # B) PLANO CARTESIANO GIGANTE (Ocupa todo el espacio restante disponible)
    graph_card = ctk.CTkFrame(split_box, corner_radius=12, border_width=1, border_color=("gray85", "gray25"))
    graph_card.pack(side="left", fill="both", expand=True)

    grp_header = ctk.CTkFrame(graph_card, fg_color="transparent")
    grp_header.pack(fill="x", padx=14, pady=(10, 4))

    icon_grid = get_icon("grid-math", size=16, light_color="#2563EB", dark_color="#3B82F6")
    grp_title = ctk.CTkLabel(
        grp_header,
        text="  Visualizador Geométrico",
        image=icon_grid,
        compound="left",
        font=ctk.CTkFont(size=12, weight="bold"),
        anchor="w"
    )
    grp_title.pack(side="left")

    grp_info = ctk.CTkLabel(grp_header, text="Escala Proporcional 1:1", font=ctk.CTkFont(size=10), text_color="gray", anchor="e")
    grp_info.pack(side="right")

    figure = Figure(figsize=(7, 5), dpi=100)
    ax = figure.add_subplot(111)
    setup_ejes(ax, figure, limit=10, is_dark=(ctk.get_appearance_mode().lower() == "dark"))

    canvas = FigureCanvasTkAgg(figure, master=graph_card)
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(0, 10))
    canvas.draw()

    # --- LÓGICA DE CONTROL ---
    def calculate():
        try:
            x1 = float(entryXA.get().strip())
            y1 = float(entryYA.get().strip())
            x2 = float(entryXB.get().strip())
            y2 = float(entryYB.get().strip())
            if x1.is_integer(): x1 = int(x1)
            if y1.is_integer(): y1 = int(y1)
            if x2.is_integer(): x2 = int(x2)
            if y2.is_integer(): y2 = int(y2)
        except ValueError:
            messagebox.showerror("Dato Inválido", "Por favor ingresa coordenadas numéricas válidas.")
            return

        if x2 == x1:
            messagebox.showwarning(
                "Recta Vertical",
                f"X₁ es igual a X₂ ({x1}). La pendiente es indefinida (división por cero).\n"
                f"Ecuación vertical: x = {x1}"
            )
            return

        delta_x = x2 - x1
        delta_y = y2 - y1
        dir_x = get_direccion_x(delta_x)
        dir_y = get_direccion_y(delta_y)

        pendiente = get_pendiente(x1, y1, x2, y2)
        ordenada = get_ordenada(x1, y1, pendiente)
        comportamiento = get_comportamiento_pendiente(pendiente)
        angulo = math.degrees(math.atan(pendiente))
        equation = get_ecuacion_recta(x1, y1, pendiente)

        max_val = max(abs(x1), abs(y1), abs(x2), abs(y2))
        if max_val == 0:
            max_val = 10
        margin = max(2, int(max_val * 0.15) + 1)
        limit = max_val + margin

        points = plot_points(x1, x2, y1, pendiente, limit)
        table_points = generar_puntos_trayectoria(x1, y1, x2, y2)

        current_data.clear()
        current_data.update({
            "has_data": True,
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2,
            "pendiente": pendiente,
            "ordenada": ordenada,
            "comportamiento": comportamiento,
            "angulo": angulo,
            "equation": equation,
            "delta_x": delta_x,
            "delta_y": delta_y,
            "dir_x": dir_x,
            "dir_y": dir_y,
            "limit": limit,
            "points": points,
            "table_points": table_points,
        })

        # Actualizar datos separados de manera clara en las 4 tarjetas
        # 1. Pendiente
        val_m_num.configure(text=f"{pendiente:g}")
        val_m_sub1.configure(text=f"Sentido: {comportamiento}")
        val_m_sub2.configure(text=f"Ángulo: {angulo:.1f}°")

        # 2. Ecuación
        val_eq_num.configure(text=equation)
        val_eq_sub1.configure(text=f"Ordenada (b): {ordenada:g}")
        val_eq_sub2.configure(text=f"Forma: y = mx + b")

        # 3. Incremento X
        val_dx_num.configure(text=f"{delta_x:+g}" if delta_x != 0 else "0")
        val_dx_sub1.configure(text=f"Sentido: {dir_x}")
        val_dx_sub2.configure(text=f"Magnitud: |ΔX| = {abs(delta_x):g}")

        # 4. Incremento Y
        val_dy_num.configure(text=f"{delta_y:+g}" if delta_y != 0 else "0")
        val_dy_sub1.configure(text=f"Sentido: {dir_y}")
        val_dy_sub2.configure(text=f"Magnitud: |ΔY| = {abs(delta_y):g}")

        # Llenar CTkTable
        new_table_data = [["Paso", "Coord X", "Coord Y"]]
        for paso, px, py in table_points:
            new_table_data.append([str(paso), f"{px:g}", f"{py:g}"])
        render_table(new_table_data)

        tbl_count.configure(text=f"{len(table_points)} puntos calculados")

        # Repintar gráfica
        render_plot(ax, figure, canvas)

    def clear():
        entryXA.delete(0, "end")
        entryYA.delete(0, "end")
        entryXB.delete(0, "end")
        entryYB.delete(0, "end")

        val_m_num.configure(text="--")
        val_m_sub1.configure(text="Comportamiento: --")
        val_m_sub2.configure(text="Ángulo: --")

        val_eq_num.configure(text="--")
        val_eq_sub1.configure(text="Ordenada (b): --")
        val_eq_sub2.configure(text="Forma: Explícita")

        val_dx_num.configure(text="--")
        val_dx_sub1.configure(text="Sentido: --")
        val_dx_sub2.configure(text="Magnitud: --")

        val_dy_num.configure(text="--")
        val_dy_sub1.configure(text="Sentido: --")
        val_dy_sub2.configure(text="Magnitud: --")

        render_table(default_table_data)
        tbl_count.configure(text="0 pasos calculados")
        current_data.clear()

        render_plot(ax, figure, canvas)
        entryXA.focus_set()

    def update_plot():
        render_plot(ax, figure, canvas)

    register_plot_updater(update_plot)

    # Valores iniciales para facilitar la visualización inmediata
    entryXA.insert(0, "1")
    entryYA.insert(0, "2")
    entryXB.insert(0, "5")
    entryYB.insert(0, "8")

    return page
