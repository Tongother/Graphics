"""
Pruebas automatizadas de lógica, navegación y renderizado con CustomTkinter.
"""
import unittest
import customtkinter as ctk

from pages.puntos_colineales import (
    get_pendiente,
    get_ordenada,
    get_ecuacion_recta,
    get_direccion_x,
    get_direccion_y,
    generar_puntos_trayectoria,
    create_puntos_colineales_page,
    current_data,
    notify_theme_to_plot
)
from pages.index import init_pages, show_page, get_current_page


class TestGraphicsApp(unittest.TestCase):

    def test_math_logic(self):
        # Pendiente m = (8 - 2) / (5 - 1) = 6 / 4 = 1.5
        m = get_pendiente(1, 2, 5, 8)
        self.assertAlmostEqual(m, 1.5)

        # Ordenada b = 2 - 1.5 * 1 = 0.5
        b = get_ordenada(1, 2, m)
        self.assertAlmostEqual(b, 0.5)

        # Ecuación
        eq = get_ecuacion_recta(1, 2, m)
        self.assertIn("1.5x", eq)
        self.assertIn("0.5", eq)

        # Direcciones
        self.assertEqual(get_direccion_x(4), "Izquierda a Derecha")
        self.assertEqual(get_direccion_x(-3), "Derecha a Izquierda")
        self.assertEqual(get_direccion_y(6), "Abajo a Arriba")
        self.assertEqual(get_direccion_y(-5), "Arriba a Abajo")

        # Trayectoria
        puntos = generar_puntos_trayectoria(1, 2, 5, 8)
        self.assertEqual(len(puntos), 7)  # max(|4|, |6|) = 6 pasos -> 7 puntos (0 a 6)
        self.assertEqual(puntos[0], (0, 1, 2))
        self.assertEqual(puntos[-1], (6, 5, 8))

    def test_customtkinter_appearance_modes(self):
        ctk.set_appearance_mode("Dark")
        self.assertEqual(ctk.get_appearance_mode(), "Dark")

        ctk.set_appearance_mode("Light")
        self.assertEqual(ctk.get_appearance_mode(), "Light")

        ctk.set_appearance_mode("Dark")

    def test_navigation(self):
        app = ctk.CTk()
        app.withdraw()
        container = ctk.CTkFrame(app)
        container.pack()

        init_pages(container)
        self.assertEqual(get_current_page(), "puntos_colineales")

        show_page("futuro")
        self.assertEqual(get_current_page(), "futuro")

        show_page("puntos_colineales")
        self.assertEqual(get_current_page(), "puntos_colineales")

        app.destroy()

    def test_interactive_calculation_and_clear(self):
        app = ctk.CTk()
        app.withdraw()

        container = ctk.CTkFrame(app)
        container.pack()
        page = create_puntos_colineales_page(container)
        page.pack()

        # Encontrar botones de calcular y limpiar dentro de la página
        calc_btn = None
        clear_btn = None

        def search_buttons(widget):
            nonlocal calc_btn, clear_btn
            if isinstance(widget, ctk.CTkButton):
                text = widget.cget("text")
                if "Calcular" in text:
                    calc_btn = widget
                elif "Limpiar" in text:
                    clear_btn = widget
            for child in widget.winfo_children():
                search_buttons(child)

        search_buttons(page)
        self.assertIsNotNone(calc_btn)
        self.assertIsNotNone(clear_btn)

        # Ejecutar cálculo (valores por defecto 1, 2, 5, 8)
        calc_btn.invoke()
        self.assertTrue(current_data.get("has_data"))
        self.assertEqual(current_data.get("pendiente"), 1.5)
        self.assertEqual(len(current_data.get("table_points")), 7)

        # Probar notificación de tema al plano
        notify_theme_to_plot()

        # Ejecutar limpieza
        clear_btn.invoke()
        self.assertFalse(current_data.get("has_data", False))

        app.destroy()


if __name__ == "__main__":
    unittest.main()
