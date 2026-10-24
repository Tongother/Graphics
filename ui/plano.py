"""
Plano cartesiano con Matplotlib: ejes con los colores del tema, zoom con la
rueda, arrastre con el mouse y utilidades comunes de dibujo (leyenda y etiquetas).
"""
from matplotlib.backend_tools import Cursors
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from ui.tema import es_oscuro


def colores_plano(is_dark):
    """Colores de fondo y texto del plano que comparten todas las gráficas."""
    return {
        "fig_bg": "#2B2B2B" if is_dark else "#F2F2F2",
        "border": "#444444" if is_dark else "#D0D0D0",
        "text": "#E0E0E0" if is_dark else "#1A1A1A",
    }


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


def anotar_punto(ax, texto, x, y, color, is_dark, **kwargs):
    """Etiqueta con recuadro redondeado 14 px arriba del punto."""
    bbox = dict(boxstyle="round,pad=0.35", fc=colores_plano(is_dark)["fig_bg"], ec=color, lw=1.2, alpha=0.95)
    ax.annotate(
        texto,
        (x, y),
        textcoords="offset points",
        xytext=(0, 14),
        ha="center",
        fontsize=9,
        fontweight="bold",
        color=color,
        bbox=bbox,
        **kwargs
    )


def dibujar_leyenda(ax, is_dark):
    colores = colores_plano(is_dark)
    legend = ax.legend(
        loc="best",
        fontsize=8.5,
        framealpha=0.88,
        facecolor=colores["fig_bg"],
        edgecolor=colores["border"]
    )
    for text in legend.get_texts():
        text.set_color(colores["text"])


def aplicar_vista(ax, view):
    """view = (xlim, ylim) conserva el zoom y la posición actuales; None no cambia nada."""
    if view is not None:
        ax.set_xlim(view[0])
        ax.set_ylim(view[1])


def habilitar_navegacion(ax, canvas):
    """
    Zoom con la rueda del mouse (centrado en el cursor) y arrastre con clic
    izquierdo para mover el plano. Solo cambian los límites de los ejes, así que
    la gráfica conserva su tamaño.
    """
    arrastre = {}

    def on_scroll(event):
        if event.inaxes is not ax:
            return
        # Rueda hacia arriba acerca; cada muesca escala 1.2x
        factor = 1.2 ** -event.step
        (x0, x1), (y0, y1) = ax.get_xlim(), ax.get_ylim()
        if not 1 <= (x1 - x0) * factor <= 10000:
            return
        cx, cy = event.xdata, event.ydata
        ax.set_xlim(cx - (cx - x0) * factor, cx + (x1 - cx) * factor)
        ax.set_ylim(cy - (cy - y0) * factor, cy + (y1 - cy) * factor)
        canvas.draw_idle()

    def on_press(event):
        if event.inaxes is not ax or event.button != 1:
            return
        arrastre.update(x=event.x, y=event.y, xlim=ax.get_xlim(), ylim=ax.get_ylim())
        canvas.set_cursor(Cursors.MOVE)

    def on_motion(event):
        if not arrastre:
            return
        # Desplazamiento en píxeles de pantalla convertido a unidades del plano
        (x0, x1), (y0, y1) = arrastre["xlim"], arrastre["ylim"]
        dx = (event.x - arrastre["x"]) * (x1 - x0) / ax.bbox.width
        dy = (event.y - arrastre["y"]) * (y1 - y0) / ax.bbox.height
        ax.set_xlim(x0 - dx, x1 - dx)
        ax.set_ylim(y0 - dy, y1 - dy)
        canvas.draw_idle()

    def on_release(event):
        if arrastre:
            arrastre.clear()
            canvas.set_cursor(Cursors.POINTER)

    canvas.mpl_connect("scroll_event", on_scroll)
    canvas.mpl_connect("button_press_event", on_press)
    canvas.mpl_connect("motion_notify_event", on_motion)
    canvas.mpl_connect("button_release_event", on_release)


def crear_plano(graph_card, body, limit=10):
    """
    Figura + canvas Tk dentro de graph_card, con zoom y arrastre activos.
    body (PaginaDesplazable) deja de hacer scroll cuando la rueda está sobre la gráfica.
    Retorna (figure, ax, canvas).
    """
    figure = Figure(figsize=(7, 5), dpi=100)
    ax = figure.add_subplot(111)
    setup_ejes(ax, figure, limit=limit, is_dark=es_oscuro())

    canvas = FigureCanvasTkAgg(figure, master=graph_card)
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(0, 10))
    body.excluir_rueda(canvas.get_tk_widget())
    canvas.draw()
    habilitar_navegacion(ax, canvas)
    return figure, ax, canvas
