"""
Página informativa para futuras herramientas y algoritmos gráficos construida con CustomTkinter.
"""
import customtkinter as ctk
from pages.icons import get_icon


def future_page(container):
    page = ctk.CTkFrame(container, corner_radius=0, fg_color="transparent")

    # Contenedor central tipo tarjeta
    card = ctk.CTkFrame(page, corner_radius=16, border_width=1, border_color=("gray80", "gray30"))
    card.place(relx=0.5, rely=0.5, anchor="center")

    rocket_icon = get_icon("rocket", size=44, light_color="#2563EB", dark_color="#3B82F6")
    icon_label = ctk.CTkLabel(card, text="", image=rocket_icon)
    icon_label.pack(pady=(35, 10))

    title_label = ctk.CTkLabel(
        card,
        text="Módulo en Desarrollo",
        font=ctk.CTkFont(size=20, weight="bold")
    )
    title_label.pack(padx=50, pady=(0, 10))

    desc_label = ctk.CTkLabel(
        card,
        text="Este espacio está reservado para nuevos algoritmos de computación gráfica:\n\n"
             "• Rasterización DDA y Bresenham\n"
             "• Trazado de circunferencias y elipses\n"
             "• Transformaciones geométricas 2D y curvas paramétricas",
        font=ctk.CTkFont(size=13),
        justify="left",
        text_color=("gray40", "gray70")
    )
    desc_label.pack(padx=50, pady=(0, 25))

    badge = ctk.CTkButton(
        card,
        text="Próximamente",
        width=130,
        height=28,
        corner_radius=14,
        state="disabled",
        fg_color=("gray85", "gray25"),
        text_color_disabled=("gray40", "gray75")
    )
    badge.pack(pady=(0, 35))

    return page