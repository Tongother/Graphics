"""
Ventana Principal - Computación Gráfica
Construida con CustomTkinter, iconos vectoriales nativos (CTkImage) y switch interactivo.
"""
import customtkinter as ctk

from pages.index import init_pages, show_page, register_nav_listener
from pages.puntos_colineales import notify_theme_to_plot
from pages.icons import get_icon

# 1. Configuración de tema visual
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# 2. Ventana Principal
root = ctk.CTk()
root.title("Computación Gráfica - Visualizador de Rectas")
root.geometry("1340x840")
root.minsize(1100, 720)

root.columnconfigure(1, weight=1)
root.rowconfigure(0, weight=1)

# 3. Barra Lateral (Sidebar)
sidebar = ctk.CTkFrame(root, width=250, corner_radius=0)
sidebar.grid(row=0, column=0, sticky="nsew")
sidebar.grid_propagate(False)
sidebar.grid_rowconfigure(4, weight=1)

# Encabezado con icono vectorial
header_box = ctk.CTkFrame(sidebar, fg_color="transparent")
header_box.pack(fill="x", padx=18, pady=(24, 4), anchor="w")

logo_icon = get_icon("logo", size=24, light_color="#2563EB", dark_color="#3B82F6")
logo_label = ctk.CTkLabel(
    header_box,
    text="  GRAFICACIÓN",
    image=logo_icon,
    compound="left",
    font=ctk.CTkFont(size=17, weight="bold")
)
logo_label.pack(anchor="w")

logo_sub = ctk.CTkLabel(
    sidebar,
    text="Laboratorio de Algoritmos",
    font=ctk.CTkFont(size=11),
    text_color="gray"
)
logo_sub.pack(padx=22, pady=(2, 20), anchor="w")

# Separador
sep = ctk.CTkFrame(sidebar, height=1, fg_color=("gray80", "gray25"))
sep.pack(fill="x", padx=16, pady=(0, 16))

# Menú de Navegación con Iconos
nav_buttons = {}

icon_puntos = get_icon("trending-up", size=18, light_color="#1E293B", dark_color="#F8FAFC")
btn_puntos = ctk.CTkButton(
    sidebar,
    text="  Puntos Colineales",
    image=icon_puntos,
    compound="left",
    height=40,
    corner_radius=8,
    anchor="w",
    font=ctk.CTkFont(size=13, weight="bold"),
    command=lambda: show_page("puntos_colineales")
)
btn_puntos.pack(fill="x", padx=14, pady=4)
nav_buttons["puntos_colineales"] = btn_puntos

icon_futuro = get_icon("sparkles", size=18, light_color="#1E293B", dark_color="#F8FAFC")
btn_futuro = ctk.CTkButton(
    sidebar,
    text="  Módulo Futuro",
    image=icon_futuro,
    compound="left",
    height=40,
    corner_radius=8,
    anchor="w",
    font=ctk.CTkFont(size=13),
    command=lambda: show_page("futuro")
)
btn_futuro.pack(fill="x", padx=14, pady=4)
nav_buttons["futuro"] = btn_futuro


def on_page_changed(page_name):
    for name, btn in nav_buttons.items():
        if name == page_name:
            btn.configure(
                fg_color=["#3B82F6", "#2563EB"],
                text_color="#FFFFFF",
                font=ctk.CTkFont(size=13, weight="bold")
            )
        else:
            btn.configure(
                fg_color="transparent",
                text_color=("gray20", "gray80"),
                font=ctk.CTkFont(size=13, weight="normal")
            )


register_nav_listener(on_page_changed)

# Pie de barra lateral: Switch con icono nativo
footer_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
footer_frame.pack(side="bottom", fill="x", padx=16, pady=20)


def toggle_theme():
    if theme_switch.get() == 1:
        ctk.set_appearance_mode("Dark")
        theme_switch.configure(text="  Modo Oscuro")
    else:
        ctk.set_appearance_mode("Light")
        theme_switch.configure(text="  Modo Claro")
    notify_theme_to_plot()


theme_switch = ctk.CTkSwitch(
    footer_frame,
    text="  Modo Oscuro",
    font=ctk.CTkFont(size=12, weight="bold"),
    command=toggle_theme
)
theme_switch.pack(anchor="w")
theme_switch.select()

# 4. Contenedor Principal de Páginas
container = ctk.CTkFrame(root, corner_radius=0, fg_color="transparent")
container.grid(row=0, column=1, sticky="nsew")
container.rowconfigure(0, weight=1)
container.columnconfigure(0, weight=1)

# Inicializar páginas
init_pages(container)
on_page_changed("puntos_colineales")

if __name__ == "__main__":
    root.mainloop()