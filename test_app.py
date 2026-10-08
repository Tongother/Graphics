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
from pages.triangulo import (
    distancia_euclidiana,
    calcular_area_triangulo,
    calcular_perimetro_triangulo,
    clasificar_por_lados,
    clasificar_por_angulos,
    calcular_pendiente_segura,
    create_triangulo_page,
    current_triangle_data,
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

    def test_triangle_math_and_classifications(self):
        # Triángulo rectángulo notable (3, 4, 5): (0,0), (4,0), (0,3)
        d_ab = distancia_euclidiana(0, 0, 4, 0)  # 4
        d_bc = distancia_euclidiana(4, 0, 0, 3)  # 5
        d_ca = distancia_euclidiana(0, 3, 0, 0)  # 3

        self.assertAlmostEqual(d_ab, 4.0)
        self.assertAlmostEqual(d_bc, 5.0)
        self.assertAlmostEqual(d_ca, 3.0)

        # Área = (base * altura) / 2 = (4 * 3) / 2 = 6
        area = calcular_area_triangulo(0, 0, 4, 0, 0, 3)
        self.assertAlmostEqual(area, 6.0)

        # Perímetro = 3 + 4 + 5 = 12
        perimetro = calcular_perimetro_triangulo(d_ab, d_bc, d_ca)
        self.assertAlmostEqual(perimetro, 12.0)

        # Clasificación por lados: Escaleno
        self.assertEqual(clasificar_por_lados(d_ab, d_bc, d_ca), "Escaleno")

        # Clasificación por ángulos: Rectángulo (4² + 3² = 5²)
        self.assertEqual(clasificar_por_angulos(d_ab, d_bc, d_ca), "Rectángulo")

        # Triángulo Isósceles y Acutángulo: (0,0), (4,0), (2,5)
        d1 = distancia_euclidiana(0, 0, 4, 0)
        d2 = distancia_euclidiana(4, 0, 2, 5)
        d3 = distancia_euclidiana(2, 5, 0, 0)
        self.assertEqual(clasificar_por_lados(d1, d2, d3), "Isósceles")
        self.assertEqual(clasificar_por_angulos(d1, d2, d3), "Acutángulo")

        # Triángulo Equilátero
        self.assertEqual(clasificar_por_lados(5.0, 5.0, 5.0), "Equilátero")

        # Triángulo Obtusángulo: (0,0), (5,0), (1,1) -> lados sqrt(2), sqrt(17), 5
        d_ob1 = distancia_euclidiana(0, 0, 5, 0)  # 5
        d_ob2 = distancia_euclidiana(5, 0, 1, 1)  # sqrt(17) ~= 4.12
        d_ob3 = distancia_euclidiana(1, 1, 0, 0)  # sqrt(2) ~= 1.41
        self.assertEqual(clasificar_por_angulos(d_ob1, d_ob2, d_ob3), "Obtusángulo")

        # Puntos Colineales: Área debe ser 0
        area_col = calcular_area_triangulo(1, 1, 2, 2, 3, 3)
        self.assertAlmostEqual(area_col, 0.0)

        # Pendiente segura
        m_normal, str_m = calcular_pendiente_segura(1, 1, 3, 5)
        self.assertAlmostEqual(m_normal, 2.0)
        self.assertEqual(str_m, "2")

        m_vert, str_vert = calcular_pendiente_segura(2, 1, 2, 8)
        self.assertIsNone(m_vert)
        self.assertIn("Vertical", str_vert)

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

        show_page("triangulo")
        self.assertEqual(get_current_page(), "triangulo")

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

        calc_btn.invoke()
        self.assertTrue(current_data.get("has_data"))
        self.assertEqual(current_data.get("pendiente"), 1.5)
        self.assertEqual(len(current_data.get("table_points")), 7)

        notify_theme_to_plot()

        clear_btn.invoke()
        self.assertFalse(current_data.get("has_data", False))

        app.destroy()

    def test_triangle_page_interactive_calculation_and_clear(self):
        app = ctk.CTk()
        app.withdraw()

        container = ctk.CTkFrame(app)
        container.pack()
        page = create_triangulo_page(container)
        page.pack()

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

        # Por defecto tiene vértices (1,1), (7,2), (3,7)
        calc_btn.invoke()
        self.assertTrue(current_triangle_data.get("has_data"))
        self.assertGreater(current_triangle_data.get("area"), 0)
        self.assertGreater(len(current_triangle_data.get("table_points")), 0)
        self.assertFalse(current_triangle_data.get("es_colineal"))

        # Probar limpieza
        clear_btn.invoke()
        self.assertFalse(current_triangle_data.get("has_data", False))

        app.destroy()


if __name__ == "__main__":
    unittest.main()
