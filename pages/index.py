"""
Gestor de páginas y navegación de la aplicación en CustomTkinter.
"""
from pages.Futuro import future_page
from pages.puntos_colineales import create_puntos_colineales_page

_pages = {}
_current_page = None
_nav_listeners = []


def register_nav_listener(callback):
    if callback not in _nav_listeners:
        _nav_listeners.append(callback)


def init_pages(container):
    global _pages, _current_page
    _pages.update({
        "puntos_colineales": create_puntos_colineales_page(container),
        "futuro": future_page(container),
    })

    for page in _pages.values():
        page.grid(row=0, column=0, sticky="nsew")

    show_page("puntos_colineales")


def show_page(page_name):
    global _current_page
    page = _pages.get(page_name)
    if page:
        page.tkraise()
        _current_page = page_name
        for cb in _nav_listeners:
            try:
                cb(page_name)
            except Exception:
                pass


def get_current_page():
    return _current_page