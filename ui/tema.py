"""
Modo oscuro / claro: consulta del tema activo y aviso a las gráficas para que
se redibujen con los colores nuevos.
"""
import customtkinter as ctk

_plot_callbacks = []


def es_oscuro():
    return ctk.get_appearance_mode().lower() == "dark"


def register_plot_updater(callback):
    """Cada página registra aquí la función que redibuja su plano al cambiar el tema."""
    if callback not in _plot_callbacks:
        _plot_callbacks.append(callback)


def notify_theme_to_plot():
    for cb in _plot_callbacks:
        try:
            cb()
        except Exception:
            pass
