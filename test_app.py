"""
Pruebas automatizadas de lógica, navegación y renderizado con CustomTkinter.
"""
import unittest
import customtkinter as ctk
from matplotlib.backend_bases import MouseEvent
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

from pages.puntos_colineales import (
    get_pendiente,
    get_ordenada,
    get_ecuacion_recta,
    get_direccion_x,
    get_direccion_y,
    generar_puntos_trayectoria,
    clasificar_recta,
    redondear_pixel,
    setup_ejes,
    render_plot,
    habilitar_navegacion,
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


    # (A, B, caso, notación): 4 positivos, 4 negativos y 3 especiales del documento
    CASOS = [
        ((0, 0), (5, 2), "Positivo 1", "+m<1, m = 2/5 · Xₖ₊₁ = Xₖ + 1 · Yₖ₊₁ = Yₖ + m"),
        ((5, 2), (0, 0), "Positivo 2", "+m<1, m = 2/5 · Xₖ₊₁ = Xₖ − 1 · Yₖ₊₁ = Yₖ − m"),
        ((0, 0), (2, 5), "Positivo 3", "+m>1, m = 5/2 · Yₖ₊₁ = Yₖ + 1 · Xₖ₊₁ = Xₖ + 1/m"),
        ((2, 5), (0, 0), "Positivo 4", "+m>1, m = 5/2 · Yₖ₊₁ = Yₖ − 1 · Xₖ₊₁ = Xₖ − 1/m"),
        ((5, 0), (0, 2), "Negativo 1", "|−m|<1, m = −2/5 · Xₖ₊₁ = Xₖ − 1 · Yₖ₊₁ = Yₖ + |m|"),
        ((0, 2), (5, 0), "Negativo 2", "|−m|<1, m = −2/5 · Xₖ₊₁ = Xₖ + 1 · Yₖ₊₁ = Yₖ − |m|"),
        ((2, 0), (0, 5), "Negativo 3", "|−m|>1, m = −5/2 · Yₖ₊₁ = Yₖ + 1 · Xₖ₊₁ = Xₖ − 1/|m|"),
        ((0, 5), (2, 0), "Negativo 4", "|−m|>1, m = −5/2 · Yₖ₊₁ = Yₖ − 1 · Xₖ₊₁ = Xₖ + 1/|m|"),
        ((0, 0), (4, 4), "Especial 45° a) ↗", "m = 1 · Xₖ₊₁ = Xₖ + 1 · Yₖ₊₁ = Yₖ + 1"),
        ((0, 4), (4, 0), "Especial 45° b) ↘", "m = −1 · Xₖ₊₁ = Xₖ + 1 · Yₖ₊₁ = Yₖ − 1"),
        ((4, 4), (0, 0), "Especial 45° c) ↙", "m = 1 · Xₖ₊₁ = Xₖ − 1 · Yₖ₊₁ = Yₖ − 1"),
        ((4, 0), (0, 4), "Especial 45° d) ↖", "m = −1 · Xₖ₊₁ = Xₖ − 1 · Yₖ₊₁ = Yₖ + 1"),
        ((0, 2), (5, 2), "Especial: horizontal", "m = 0 · Xₖ₊₁ = Xₖ + 1 · Y no cambia"),
        ((5, 2), (0, 2), "Especial: horizontal", "m = 0 · Xₖ₊₁ = Xₖ − 1 · Y no cambia"),
        ((3, 0), (3, 5), "Especial: vertical", "m = Error (indefinida) · Yₖ₊₁ = Yₖ + 1 · X no cambia"),
        ((3, 5), (3, 0), "Especial: vertical", "m = Error (indefinida) · Yₖ₊₁ = Yₖ − 1 · X no cambia"),
        # No es caso del documento, solo protección
        ((2, 3), (2, 3), "Un solo punto", "Sin recorrido: ΔX = 0 y ΔY = 0"),
    ]

    def test_clasificacion_casos(self):
        for (x1, y1), (x2, y2), esperado, notacion in self.CASOS:
            with self.subTest(A=(x1, y1), B=(x2, y2)):
                caso, _, obtenida = clasificar_recta(x2 - x1, y2 - y1)
                self.assertEqual(caso, esperado)
                self.assertEqual(obtenida, notacion)

        # Sentido del dibujo en el detalle
        self.assertEqual(clasificar_recta(-5, 2)[1], "Acostada \\, derecha → izquierda")
        self.assertEqual(clasificar_recta(0, -5)[1], "arriba → abajo")

        # Pendiente no fraccionaria: se muestra en decimal
        self.assertIn("m = 0.3333", clasificar_recta(3, 0.9999)[2])

    def test_trayectorias_casos_especiales(self):
        # Vertical hacia abajo: X constante, Y baja de 1 en 1
        puntos = generar_puntos_trayectoria(3, 7, 3, 1)
        self.assertEqual(len(puntos), 7)
        self.assertTrue(all(px == 3 for _, px, _ in puntos))
        self.assertEqual(puntos[-1], (6, 3, 1))

        # Horizontal hacia la izquierda: Y constante, X baja de 1 en 1
        puntos = generar_puntos_trayectoria(6, 2, 1, 2)
        self.assertEqual([px for _, px, _ in puntos], [6, 5, 4, 3, 2, 1])

        # Al revés: empieza en A y termina en B
        puntos = generar_puntos_trayectoria(5, 8, 1, 2)
        self.assertEqual(puntos[0], (0, 5, 8))
        self.assertEqual(puntos[-1], (6, 1, 2))

        # Puntos distintos a menos de una unidad: A y B
        self.assertEqual(len(generar_puntos_trayectoria(0, 0, 0.5, 0.2)), 2)

    def test_pasos_y_pixeles(self):
        # Positivo 1: X avanza 1 y Y avanza m = 0.4
        puntos = generar_puntos_trayectoria(0, 0, 5, 2)
        self.assertEqual([px for _, px, _ in puntos], [0, 1, 2, 3, 4, 5])
        self.assertEqual([py for _, _, py in puntos], [0, 0.4, 0.8, 1.2, 1.6, 2])
        self.assertEqual([redondear_pixel(py) for _, _, py in puntos], [0, 0, 1, 1, 2, 2])

        # Negativo 4: Y baja 1 y X avanza 1/|m| = 0.4
        puntos = generar_puntos_trayectoria(0, 5, 2, 0)
        self.assertEqual([py for _, _, py in puntos], [5, 4, 3, 2, 1, 0])
        self.assertEqual([px for _, px, _ in puntos], [0, 0.4, 0.8, 1.2, 1.6, 2])

        # Las mitades se redondean hacia arriba (round() daría 2 y 0)
        self.assertEqual(redondear_pixel(2.5), 3)
        self.assertEqual(redondear_pixel(0.5), 1)
        self.assertEqual(redondear_pixel(-0.5), 0)
        self.assertEqual(redondear_pixel(-1.6), -2)

        # Positivo 2 con Y bajando 0.67 por paso: en X = 19 la Y es 36.00 y nunca sube
        puntos = generar_puntos_trayectoria(25, 40, 10, 30)
        ys = [py for _, _, py in puntos]
        self.assertEqual(dict((px, py) for _, px, py in puntos)[19], 36)
        self.assertTrue(all(a > b for a, b in zip(ys, ys[1:])))

    def test_zoom_y_arrastre(self):
        figure = Figure(figsize=(5, 5), dpi=100)
        ax = figure.add_subplot(111)
        setup_ejes(ax, figure, limit=10)
        canvas = FigureCanvasAgg(figure)
        habilitar_navegacion(ax, canvas)
        canvas.draw()
        tamano_caja = ax.bbox.bounds

        def evento(nombre, x, y, **kwargs):
            # MouseEvent trunca x, y a píxeles enteros
            ev = MouseEvent(nombre, canvas, x, y, **kwargs)
            canvas.callbacks.process(nombre, ev)
            return ev

        # Rueda hacia arriba sobre (2, 3): acerca 1.2x y el punto bajo el cursor no se mueve
        px, py = ax.transData.transform((2, 3))
        ev = evento("scroll_event", px, py, button="up", step=1)
        x0, x1 = ax.get_xlim()
        y0, y1 = ax.get_ylim()
        self.assertAlmostEqual(x1 - x0, 20 / 1.2)
        self.assertAlmostEqual(y1 - y0, 20 / 1.2)
        self.assertAlmostEqual((ev.xdata - x0) / (x1 - x0), (ev.xdata + 10) / 20)
        self.assertAlmostEqual((ev.ydata - y0) / (y1 - y0), (ev.ydata + 10) / 20)

        # Rueda hacia abajo regresa al tamaño original
        evento("scroll_event", px, py, button="down", step=-1)
        self.assertAlmostEqual(ax.get_xlim()[1] - ax.get_xlim()[0], 20)

        # Arrastrar 40 píxeles a la derecha mueve el plano 40 píxeles en unidades
        xlim_antes, ylim_antes = ax.get_xlim(), ax.get_ylim()
        corrimiento = 40 * (xlim_antes[1] - xlim_antes[0]) / ax.bbox.width
        cx, cy = map(int, ax.transData.transform((0, 0)))
        evento("button_press_event", cx, cy, button=1)
        evento("motion_notify_event", cx + 40, cy)
        evento("button_release_event", cx + 40, cy, button=1)
        self.assertAlmostEqual(ax.get_xlim()[0], xlim_antes[0] - corrimiento)
        self.assertAlmostEqual(ax.get_xlim()[1], xlim_antes[1] - corrimiento)
        self.assertEqual(ax.get_ylim(), ylim_antes)

        # Después de soltar, mover el mouse ya no arrastra
        xlim_suelto = ax.get_xlim()
        evento("motion_notify_event", cx + 100, cy + 100)
        self.assertEqual(ax.get_xlim(), xlim_suelto)

        # La gráfica conserva su tamaño en pantalla
        canvas.draw()
        self.assertEqual(ax.bbox.bounds, tamano_caja)

        # Redibujar (cambio de tema) conserva la vista si se pasa view
        render_plot(ax, figure, canvas, view=((0, 4), (1, 5)))
        self.assertEqual(ax.get_xlim(), (0, 4))
        self.assertEqual(ax.get_ylim(), (1, 5))

    def test_ecuaciones_casos(self):
        self.assertEqual(get_ecuacion_recta(1, 2, get_pendiente(1, 2, 6, 2)), "y = 2")
        self.assertEqual(get_ecuacion_recta(6, 2, get_pendiente(6, 2, 1, 2)), "y = 2")
        self.assertEqual(get_ecuacion_recta(0, 0, get_pendiente(0, 0, 5, 5)), "y = x")
        self.assertEqual(get_ecuacion_recta(0, 3, get_pendiente(0, 3, 3, 0)), "y = -x + 3")
        self.assertEqual(get_ecuacion_recta(0, -3, get_pendiente(0, -3, 1, -1)), "y = 2x - 3")

    def test_interfaz_todos_los_casos(self):
        app = ctk.CTk()
        app.withdraw()
        container = ctk.CTkFrame(app)
        container.pack()
        page = create_puntos_colineales_page(container)
        page.pack()

        entries = []
        calc_btn = None

        def search(widget):
            nonlocal calc_btn
            if isinstance(widget, ctk.CTkEntry):
                entries.append(widget)
            elif isinstance(widget, ctk.CTkButton) and "Calcular" in widget.cget("text"):
                calc_btn = widget
            for child in widget.winfo_children():
                search(child)

        search(page)
        self.assertEqual(len(entries), 4)

        for (x1, y1), (x2, y2), esperado, notacion in self.CASOS:
            with self.subTest(A=(x1, y1), B=(x2, y2)):
                for entry, valor in zip(entries, (x1, y1, x2, y2)):
                    entry.delete(0, "end")
                    entry.insert(0, str(valor))
                calc_btn.invoke()
                self.assertTrue(current_data.get("has_data"))
                self.assertEqual(current_data.get("caso"), esperado)
                self.assertEqual(current_data.get("notacion"), notacion)

        # Casos sin pendiente definida
        self.assertEqual(current_data.get("caso"), "Un solo punto")
        entries[0].delete(0, "end"); entries[0].insert(0, "3")
        entries[1].delete(0, "end"); entries[1].insert(0, "1")
        entries[2].delete(0, "end"); entries[2].insert(0, "3")
        entries[3].delete(0, "end"); entries[3].insert(0, "7")
        calc_btn.invoke()
        self.assertIsNone(current_data.get("pendiente"))
        self.assertEqual(current_data.get("equation"), "x = 3")

        app.destroy()


if __name__ == "__main__":
    unittest.main()
