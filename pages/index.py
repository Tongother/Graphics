"""
Registro de páginas y navegación. Para agregar un módulo nuevo basta con
añadir su entrada a PAGINAS: main.py arma el menú lateral a partir de esta lista.
"""
from pages.circulo import create_circulo_page
from pages.puntos_colineales import create_puntos_colineales_page
from pages.triangulo import create_triangulo_page

# (clave, texto del menú, icono en public/<icono>.svg, función que crea la página)
PAGINAS = [
    ("puntos_colineales", "Puntos Colineales", "trending-up-down", create_puntos_colineales_page),
    ("triangulo", "Trazado de Triángulo", "triangle", create_triangulo_page),
    ("circulo", "Circunferencia y Círculo", "circle", create_circulo_page),
]

_pages = {}
_current_page = None
_nav_listeners = []


def register_nav_listener(callback):
    if callback not in _nav_listeners:
        _nav_listeners.append(callback)


def init_pages(container):
    for clave, _, _, crear in PAGINAS:
        page = crear(container)
        page.grid(row=0, column=0, sticky="nsew")
        _pages[clave] = page

    show_page(PAGINAS[0][0])


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
