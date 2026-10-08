"""
Gestor de páginas y navegación de la aplicación en CustomTkinter.
"""
from pages.triangulo import create_triangulo_page
from pages.puntos_colineales import create_puntos_colineales_page

_pages = {}
_current_page = None
_nav_listeners = []


def register_nav_listener(callback):
    if callback not in _nav_listeners:
        _nav_listeners.append(callback)


def init_pages(container):
    global _pages, _current_page
    puntos_page = create_puntos_colineales_page(container)
    triangulo_page = create_triangulo_page(container)

    _pages.update({
        "puntos_colineales": puntos_page,
        "triangulo": triangulo_page,
        "futuro": triangulo_page,
    })

    for page in {puntos_page, triangulo_page}:
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