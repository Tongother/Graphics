from pages.Futuro import future_page
from pages.puntos_colineales import create_puntos_colineales_page

_pages = {}

def init_pages(container):
  _pages.update({
    "puntos_colineales": create_puntos_colineales_page(container),
    "futuro": future_page(container)
  })

  for page in _pages.values():
    page.grid(row=0, column=0, sticky="nsew")

def show_page(page_name):
  page = _pages.get(page_name)
  if page:
    page.tkraise()