"""
Pruebas de las páginas con ventanas reales de CustomTkinter (lentas, ~20 s).
En Windows pueden aparecer mensajes "invalid command name ..._windows_set_titlebar_icon":
son ruido de CustomTkinter al destruir la ventana y no indican un fallo.
"""
import unittest

import customtkinter as ctk

from pages.circulo import create_circulo_page, current_circle_data
from pages.index import PAGINAS, get_current_page, init_pages, show_page
from pages.puntos_colineales import create_puntos_colineales_page, current_data
from pages.triangulo import create_triangulo_page, current_triangle_data
from tests.casos import CASOS_RECTA
from ui.tema import notify_theme_to_plot
from ui.widgets import escribir_valores


def todos(widget):
    yield widget
    for hijo in widget.winfo_children():
        yield from todos(hijo)


def boton(page, texto):
    return next(w for w in todos(page) if isinstance(w, ctk.CTkButton) and texto in w.cget("text"))


def entradas(page):
    return [w for w in todos(page) if isinstance(w, ctk.CTkEntry)]


class TestInterfaz(unittest.TestCase):

    def setUp(self):
        self.app = ctk.CTk()
        self.app.withdraw()
        self.container = ctk.CTkFrame(self.app)
        self.container.pack()

    def tearDown(self):
        self.app.destroy()

    def test_customtkinter_appearance_modes(self):
        ctk.set_appearance_mode("Light")
        self.assertEqual(ctk.get_appearance_mode(), "Light")
        ctk.set_appearance_mode("Dark")
        self.assertEqual(ctk.get_appearance_mode(), "Dark")

    def test_navigation(self):
        init_pages(self.container)
        self.assertEqual(get_current_page(), "puntos_colineales")

        for clave, _, _, _ in PAGINAS:
            show_page(clave)
            self.assertEqual(get_current_page(), clave)

        # El círculo carga el ejemplo del PDF al abrir
        self.assertTrue(current_circle_data.get("has_data"))
        self.assertEqual(current_circle_data.get("xc"), 150)
        self.assertEqual(current_circle_data.get("yc"), 100)
        self.assertEqual(current_circle_data.get("r"), 10)

    def test_puntos_calcular_y_limpiar(self):
        page = create_puntos_colineales_page(self.container)
        page.pack()

        boton(page, "Calcular").invoke()
        self.assertTrue(current_data.get("has_data"))
        self.assertEqual(current_data.get("pendiente"), 1.5)
        self.assertEqual(len(current_data.get("table_points")), 7)

        notify_theme_to_plot()

        boton(page, "Limpiar").invoke()
        self.assertFalse(current_data.get("has_data", False))

    def test_puntos_todos_los_casos(self):
        page = create_puntos_colineales_page(self.container)
        page.pack()
        campos = entradas(page)
        self.assertEqual(len(campos), 4)
        calcular = boton(page, "Calcular")

        for (x1, y1), (x2, y2), esperado, notacion in CASOS_RECTA:
            with self.subTest(A=(x1, y1), B=(x2, y2)):
                escribir_valores(campos, (x1, y1, x2, y2))
                calcular.invoke()
                self.assertTrue(current_data.get("has_data"))
                self.assertEqual(current_data.get("caso"), esperado)
                self.assertEqual(current_data.get("notacion"), notacion)

        # Recta vertical: pendiente indefinida
        escribir_valores(campos, (3, 1, 3, 7))
        calcular.invoke()
        self.assertIsNone(current_data.get("pendiente"))
        self.assertEqual(current_data.get("equation"), "x = 3")

    def test_triangulo_calcular_y_limpiar(self):
        page = create_triangulo_page(self.container)
        page.pack()

        # Por defecto tiene vértices (1,1), (7,2), (3,7)
        boton(page, "Calcular").invoke()
        self.assertTrue(current_triangle_data.get("has_data"))
        self.assertGreater(current_triangle_data.get("area"), 0)
        self.assertGreater(len(current_triangle_data.get("table_points")), 0)
        self.assertEqual(current_triangle_data["casos"]["BC"][0], "Negativo 3")

        boton(page, "Limpiar").invoke()
        self.assertFalse(current_triangle_data.get("has_data", False))

    def test_triangulo_equilatero_decimal(self):
        page = create_triangulo_page(self.container)
        escribir_valores(entradas(page), ("0", "0", "10", "0", "5", "8.660254"))
        boton(page, "Calcular").invoke()
        try:
            self.assertEqual(current_triangle_data["tipo_lados"], "Equilátero")
            self.assertEqual(current_triangle_data["pixeles"]["CA"][0], (5, 9))
        finally:
            current_triangle_data.clear()

    def test_circulo_traslacion_y_metodos(self):
        page = create_circulo_page(self.container)
        page.pack()
        self.assertEqual(current_circle_data.get("xc"), 150)

        boton(page, "X + 5").invoke()
        self.assertEqual(current_circle_data.get("xc"), 155)

        boton(page, "Origen").invoke()
        self.assertEqual((current_circle_data["xc"], current_circle_data["yc"]), (0, 0))

        menu = next(w for w in todos(page) if isinstance(w, ctk.CTkOptionMenu))
        for metodo in menu.cget("values"):
            with self.subTest(metodo=metodo):
                menu.set(metodo)
                boton(page, "Calcular y Trazar").invoke()
                self.assertEqual(current_circle_data["metodo_relleno"], metodo)


if __name__ == "__main__":
    unittest.main()
