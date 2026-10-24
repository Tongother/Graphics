"""
Widgets reutilizables con el estilo de la aplicación: página con scroll,
encabezado, tarjetas, entradas de coordenadas, botones, tiles de métricas y tablas.
Cambiar el estilo aquí lo cambia en todas las páginas.
"""
import customtkinter as ctk
from CTkTable import CTkTable

from ui.icons import get_icon

# Alto del bloque tabla + plano; puede superar la ventana porque la página tiene scroll
ALTURA_GRAFICA = 760

BORDE_TARJETA = ("gray85", "gray25")
FONDO_TILE = ("gray92", "gray20")
TEXTO_SECUNDARIO = ("gray30", "gray70")

# Botón con contorno y fondo transparente (Limpiar, Centrar vista, plantillas...)
ESTILO_SECUNDARIO = dict(
    fg_color="transparent",
    border_width=1,
    border_color=("gray70", "gray40"),
    text_color=("gray20", "gray85"),
)


class PaginaDesplazable(ctk.CTkScrollableFrame):
    """
    Contenido de una página con scroll vertical. La rueda del mouse sobre la
    gráfica no mueve la página, porque ahí la rueda hace zoom en el plano.
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._sin_scroll = []

    def excluir_rueda(self, widget):
        self._sin_scroll.append(widget)

    def _mouse_wheel_all(self, event):
        bajo_cursor = self.winfo_containing(event.x_root, event.y_root)
        if bajo_cursor in self._sin_scroll:
            return
        super()._mouse_wheel_all(event)


def crear_pagina(container, titulo, subtitulo):
    """Marco de la página + cuerpo con scroll + título. Retorna (page, body)."""
    page = ctk.CTkFrame(container, corner_radius=0, fg_color="transparent")
    body = PaginaDesplazable(page, corner_radius=0, fg_color="transparent")
    body.pack(fill="both", expand=True)

    header_frame = ctk.CTkFrame(body, corner_radius=0, fg_color="transparent")
    header_frame.pack(fill="x", padx=20, pady=(12, 4))
    ctk.CTkLabel(header_frame, text=titulo, font=ctk.CTkFont(size=20, weight="bold"), anchor="w").pack(anchor="w")
    ctk.CTkLabel(header_frame, text=subtitulo, font=ctk.CTkFont(size=12), text_color="gray", anchor="w").pack(anchor="w", pady=(2, 0))
    return page, body


def tarjeta(parent, corner_radius=12, **kwargs):
    """Marco redondeado con borde fino; el contenedor base de cada sección."""
    return ctk.CTkFrame(parent, corner_radius=corner_radius, border_width=1, border_color=BORDE_TARJETA, **kwargs)


def grupo_entradas(parent, titulo, etiquetas, width=65, separacion=12, padx_derecho=16):
    """
    Bloque con título y una fila de entradas etiquetadas (p. ej. "X₁:", "Y₁:").
    Retorna la lista de CTkEntry en el mismo orden que etiquetas.
    """
    box = ctk.CTkFrame(parent, fg_color="transparent")
    box.pack(side="left", padx=(0, padx_derecho))

    ctk.CTkLabel(box, text=titulo, font=ctk.CTkFont(size=12, weight="bold")).grid(
        row=0, column=0, columnspan=2 * len(etiquetas), sticky="w", pady=(0, 4))

    entradas = []
    for i, etiqueta in enumerate(etiquetas):
        ctk.CTkLabel(box, text=etiqueta, font=ctk.CTkFont(size=12)).grid(row=1, column=2 * i, padx=(0, 4))
        entry = ctk.CTkEntry(box, width=width, height=32, corner_radius=6, justify="center")
        ultima = i == len(etiquetas) - 1
        entry.grid(row=1, column=2 * i + 1, padx=0 if ultima else (0, separacion))
        entradas.append(entry)
    return entradas


def leer_numeros(entradas):
    """
    Lee las entradas como números; los enteros se quedan como int para que se
    muestren sin ".0". Lanza ValueError si alguna no es numérica.
    """
    valores = []
    for entry in entradas:
        valor = float(entry.get().strip())
        valores.append(int(valor) if valor.is_integer() else valor)
    return valores


def escribir_valores(entradas, valores):
    for entry, valor in zip(entradas, valores):
        entry.delete(0, "end")
        entry.insert(0, str(valor))


def boton_primario(parent, texto, comando, icono="player-play", icon_size=15, **kwargs):
    opciones = dict(height=34, corner_radius=8, font=ctk.CTkFont(size=12, weight="bold"))
    opciones.update(kwargs)
    return ctk.CTkButton(
        parent,
        text=texto,
        image=get_icon(icono, size=icon_size, light_color="#FFFFFF", dark_color="#FFFFFF"),
        compound="left",
        command=comando,
        **opciones
    )


def botones_calcular_limpiar(parent, texto_calcular, on_calcular, on_limpiar):
    """Par de botones "Calcular ..." y "Limpiar" a la derecha de las entradas."""
    actions_box = ctk.CTkFrame(parent, fg_color="transparent")
    actions_box.pack(side="left", fill="y", padx=4)

    boton_primario(actions_box, texto_calcular, on_calcular).pack(side="left", padx=(0, 8), pady=6)

    ctk.CTkButton(
        actions_box,
        text="  Limpiar",
        image=get_icon("rotate", size=15),
        compound="left",
        height=34,
        corner_radius=8,
        font=ctk.CTkFont(size=12),
        command=on_limpiar,
        **ESTILO_SECUNDARIO
    ).pack(side="left", pady=6)


class TileMetrica:
    """
    Recuadro de métrica: título pequeño, valor grande y dos renglones de detalle.
    Guarda los textos iniciales para que limpiar() los restaure.
    """

    def __init__(self, parent, col, titulo, sub1, sub2):
        tile = ctk.CTkFrame(parent, corner_radius=10, fg_color=FONDO_TILE)
        tile.grid(row=0, column=col, sticky="nsew", padx=6, pady=8)
        ctk.CTkLabel(tile, text=titulo, font=ctk.CTkFont(size=9, weight="bold"), text_color="gray", anchor="w").pack(anchor="w", padx=12, pady=(6, 0))
        self.valor = ctk.CTkLabel(tile, text="--", font=ctk.CTkFont(size=17, weight="bold"), anchor="w")
        self.valor.pack(anchor="w", padx=12, pady=(1, 0))
        self.sub1 = ctk.CTkLabel(tile, text=sub1, font=ctk.CTkFont(size=10), text_color=TEXTO_SECUNDARIO, anchor="w")
        self.sub1.pack(anchor="w", padx=12)
        self.sub2 = ctk.CTkLabel(tile, text=sub2, font=ctk.CTkFont(size=10), text_color=TEXTO_SECUNDARIO, anchor="w")
        self.sub2.pack(anchor="w", padx=12, pady=(0, 6))
        self._iniciales = ("--", sub1, sub2)

    def mostrar(self, valor, sub1, sub2):
        self.valor.configure(text=valor)
        self.sub1.configure(text=sub1)
        self.sub2.configure(text=sub2)

    def limpiar(self):
        self.mostrar(*self._iniciales)


def tarjeta_metricas(body):
    """Tarjeta de 4 columnas iguales para TileMetrica (fila 0) y una franja (fila 1)."""
    metrics_card = tarjeta(body)
    metrics_card.pack(fill="x", padx=20, pady=(0, 8))
    metrics_card.columnconfigure((0, 1, 2, 3), weight=1, uniform="stat")
    return metrics_card


class TablaDinamica:
    """
    CTkTable que se reemplaza completa en cada cálculo (CTkTable no cambia de
    número de filas con facilidad). La primera fila es el encabezado.
    """

    def __init__(self, parent, width=70, font_size=11):
        self.parent = parent
        self.width = width
        self.font_size = font_size
        self.table = None

    def mostrar(self, filas):
        if self.table is not None:
            self.table.destroy()

        self.table = CTkTable(
            self.parent,
            row=len(filas),
            column=len(filas[0]),
            width=self.width,
            values=filas,
            header_color=("#3B82F6", "#1D4ED8"),
            colors=[("gray95", "#21252D"), ("gray90", "#1A1D24")],
            hover=True,
            hover_color=("#BFDBFE", "#1E3A8A"),
            corner_radius=8,
            font=ctk.CTkFont(size=self.font_size),
            justify="center"
        )
        self.table.pack(fill="x", expand=True)


def contenido_tabla(table_card, titulo, texto_info, width=70):
    """
    Título con icono, renglón de información y tabla con scroll dentro de table_card.
    Retorna (lbl_info, TablaDinamica).
    """
    ctk.CTkLabel(
        table_card,
        text=titulo,
        image=get_icon("table", size=16),
        compound="left",
        font=ctk.CTkFont(size=12, weight="bold"),
        anchor="w"
    ).pack(fill="x", padx=12, pady=(10, 2))

    lbl_info = ctk.CTkLabel(table_card, text=texto_info, font=ctk.CTkFont(size=10), text_color="gray", anchor="w")
    lbl_info.pack(fill="x", padx=12, pady=(0, 4))

    table_scroll = ctk.CTkScrollableFrame(table_card, fg_color="transparent", corner_radius=8)
    table_scroll.pack(fill="both", expand=True, padx=4, pady=(0, 8))
    return lbl_info, TablaDinamica(table_scroll, width=width)


def encabezado_grafica(graph_card, titulo, icono, on_centrar, texto_centrar=" Centrar vista", extras=(), pady=(10, 4)):
    """
    Barra sobre el plano: título con icono a la izquierda; a la derecha el botón
    de centrar, los botones extras [(texto, comando)] y la ayuda de navegación.
    """
    grp_header = ctk.CTkFrame(graph_card, fg_color="transparent")
    grp_header.pack(fill="x", padx=14, pady=pady)

    ctk.CTkLabel(
        grp_header,
        text=titulo,
        image=get_icon(icono, size=16, light_color="#2563EB", dark_color="#3B82F6"),
        compound="left",
        font=ctk.CTkFont(size=12, weight="bold"),
        anchor="w"
    ).pack(side="left")

    estilo_chico = dict(width=0, height=26, corner_radius=6, font=ctk.CTkFont(size=11), **ESTILO_SECUNDARIO)
    ctk.CTkButton(
        grp_header,
        text=texto_centrar,
        image=get_icon("focus-centered", size=14),
        compound="left",
        command=on_centrar,
        **estilo_chico
    ).pack(side="right")

    for texto, comando in extras:
        ctk.CTkButton(grp_header, text=texto, command=comando, **estilo_chico).pack(side="right", padx=(0, 6))

    ctk.CTkLabel(grp_header, text="Rueda: zoom · Arrastrar: mover", font=ctk.CTkFont(size=10), text_color="gray", anchor="e").pack(side="right", padx=(0, 10))
    return grp_header
