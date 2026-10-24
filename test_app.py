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
    rasterizar_pixeles,
    clasificar_recta,
    redondear_pixel,
    setup_ejes,
    render_plot,
    habilitar_navegacion,
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
    generar_relleno,
    ajustar_al_contorno,
    render_triangle_plot,
    create_triangulo_page,
    current_triangle_data,
)
from pages.circulo import (
    algoritmo_punto_medio_circunferencia,
    generar_relleno_dda_radial,
    generar_relleno_cuerdas_scanlines,
    get_ecuaciones_circunferencia,
    render_circle_plot,
    create_circulo_page,
    current_circle_data,
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

        # Caso DDA de cada lado: AB (1,1)→(7,2), BC (7,2)→(3,7), CA (3,7)→(1,1)
        casos = current_triangle_data["casos"]
        self.assertEqual(casos["AB"][0], "Positivo 1")
        self.assertEqual(casos["BC"][0], "Negativo 3")
        self.assertEqual(casos["CA"][0], "Positivo 4")

        # Relleno: una línea DDA desde cada vértice por cada píxel de su lado opuesto
        pixeles = current_triangle_data["pixeles"]
        relleno = current_triangle_data["relleno"]
        self.assertEqual(len(relleno), len(pixeles["AB"]) + len(pixeles["BC"]) + len(pixeles["CA"]))
        self.assertEqual(relleno[0][0], (3, 7))                     # C -> AB
        self.assertEqual(relleno[len(pixeles["AB"])][0], (1, 1))    # A -> BC

        # Probar limpieza
        clear_btn.invoke()
        self.assertFalse(current_triangle_data.get("has_data", False))

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

    def test_grafica_con_pixeles_dda(self):
        # Positivo 1: la gráfica une los píxeles redondeados, no la recta ideal
        puntos = generar_puntos_trayectoria(0, 0, 5, 2)
        self.assertEqual(rasterizar_pixeles(puntos), [(0, 0), (1, 0), (2, 1), (3, 1), (4, 2), (5, 2)])

        figure = Figure(figsize=(5, 5), dpi=100)
        ax = figure.add_subplot(111)
        canvas = FigureCanvasAgg(figure)
        current_data.clear()
        current_data.update(has_data=True, x1=0, y1=0, x2=5, y2=2, equation="y = 0.4x", table_points=puntos)
        try:
            render_plot(ax, figure, canvas)
        finally:
            current_data.clear()
        recta = next(l for l in ax.get_lines() if l.get_label().startswith("Recta DDA"))
        self.assertEqual(list(zip(recta.get_xdata(), recta.get_ydata())), rasterizar_pixeles(puntos))

        # B con decimales se marca en su píxel: (11, 30.67) -> (11, 31), sobre la recta
        puntos = generar_puntos_trayectoria(10, 30, 11, 30.67)
        current_data.update(has_data=True, x1=10, y1=30, x2=11, y2=30.67, equation="y", table_points=puntos)
        try:
            render_plot(ax, figure, canvas)
        finally:
            current_data.clear()
        marca_b = next(l for l in ax.get_lines() if l.get_label().startswith("B "))
        self.assertEqual((marca_b.get_xdata()[0], marca_b.get_ydata()[0]), (11, 31))
        self.assertEqual(marca_b.get_label(), "B (11, 31)")

    def test_relleno_triangulo_desde_c(self):
        pixeles_ab = rasterizar_pixeles(generar_puntos_trayectoria(0, 0, 6, 0))
        relleno = generar_relleno(3, 4, pixeles_ab)
        self.assertEqual(len(relleno), len(pixeles_ab))
        for linea, destino in zip(relleno, pixeles_ab):
            # Cada línea empieza en C y termina en un píxel de AB
            self.assertEqual(linea[0], (3, 4))
            self.assertEqual(linea[-1], destino)

        # El plano del triángulo dibuja el relleno y los 3 lados con sus píxeles
        figure = Figure(figsize=(5, 5), dpi=100)
        ax = figure.add_subplot(111)
        canvas = FigureCanvasAgg(figure)
        current_triangle_data.clear()
        current_triangle_data.update(
            has_data=True, x1=0, y1=0, x2=6, y2=0, x3=3, y3=4, area=12, relleno=relleno,
            pixeles={
                "AB": pixeles_ab,
                "BC": rasterizar_pixeles(generar_puntos_trayectoria(6, 0, 3, 4)),
                "CA": rasterizar_pixeles(generar_puntos_trayectoria(3, 4, 0, 0)),
            },
        )
        try:
            render_triangle_plot(ax, figure, canvas, view=((0, 4), (1, 5)))
        finally:
            current_triangle_data.clear()
        self.assertEqual(len(ax.collections[0].get_segments()), len(pixeles_ab))
        self.assertEqual(ax.get_xlim(), (0, 4))

    def test_relleno_no_sale_del_triangulo(self):
        # Un píxel fuera del borde de su fila se recorre al borde; los de adentro no cambian
        contorno = [[(0, 0), (4, 0)], [(4, 0), (3, 1), (2, 2)], [(2, 2), (1, 1), (0, 0)]]
        self.assertEqual(ajustar_al_contorno([[(5, 0), (0, 1), (2, 1)]], contorno), [[(4, 0), (1, 1), (2, 1)]])

        # Equilátero con C decimal: los vértices se ubican en su píxel y ningún
        # píxel del relleno queda fuera de los lados
        app = ctk.CTk()
        app.withdraw()
        page = create_triangulo_page(app)
        entradas = [w for w in self._todos(page) if isinstance(w, ctk.CTkEntry)]
        for entrada, valor in zip(entradas, ["0", "0", "10", "0", "5", "8.660254"]):
            entrada.delete(0, "end")
            entrada.insert(0, valor)
        next(w for w in self._todos(page) if isinstance(w, ctk.CTkButton) and "Calcular" in w.cget("text")).invoke()
        try:
            datos = current_triangle_data
            self.assertEqual(datos["tipo_lados"], "Equilátero")
            self.assertEqual(datos["pixeles"]["CA"][0], (5, 9))
            filas = {}
            for pixeles in datos["pixeles"].values():
                for x, y in pixeles:
                    filas.setdefault(y, []).append(x)
            for linea in datos["relleno"]:
                for x, y in linea:
                    self.assertTrue(min(filas[y]) <= x <= max(filas[y]))
        finally:
            current_triangle_data.clear()
            app.destroy()

    @staticmethod
    def _todos(widget):
        yield widget
        for hijo in widget.winfo_children():
            yield from TestGraphicsApp._todos(hijo)

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

    def test_circulo_algoritmo_punto_medio(self):
        # Caso del PDF del profesor: Centro (150, 100), Radio R = 10
        pasos, pixeles, pts_ordenados, oct_dict = algoritmo_punto_medio_circunferencia(150, 100, 10)
        self.assertEqual(len(pasos), 7)
        self.assertEqual(len(oct_dict), 8)

        # Primer paso k=0: P0 = 1 - 10 = -9, (X1, Y1) = (1, 10) -> Trasladado (151, 110)
        self.assertEqual(pasos[0]["k"], 0)
        self.assertEqual(pasos[0]["pk"], -9)
        self.assertEqual(pasos[0]["x_sig"], 1)
        self.assertEqual(pasos[0]["y_sig"], 10)
        self.assertEqual(pasos[0]["base_trans"], (151, 110))

        # Último paso k=6: P6 = 5 >= 0 -> (7, 7) -> Se detiene por X >= Y
        self.assertEqual(pasos[6]["k"], 6)
        self.assertEqual(pasos[6]["pk"], 5)
        self.assertEqual(pasos[6]["x_sig"], 7)
        self.assertEqual(pasos[6]["y_sig"], 7)
        self.assertEqual(pasos[6]["base_trans"], (157, 107))

        # Simetría y traslación: probar con centro en origen (0, 0)
        _, pixeles_origen, _, _ = algoritmo_punto_medio_circunferencia(0, 0, 10)
        pts_esperados = {(x + 150, y + 100) for (x, y) in pixeles_origen}
        self.assertEqual(pixeles, pts_esperados)

    def test_circulo_relleno_dda_radial_y_cuerdas(self):
        xc, yc, r = 150, 100, 10
        pasos, pixeles_contorno, pts_ordenados, _ = algoritmo_punto_medio_circunferencia(xc, yc, r)

        # 1. Relleno DDA Radial (Pág. 4 del PDF)
        segs_radial, px_radial, lineas_info = generar_relleno_dda_radial(xc, yc, pts_ordenados)
        self.assertEqual(len(segs_radial), len(pts_ordenados))
        self.assertEqual(len(lineas_info), len(pts_ordenados))
        self.assertTrue(pixeles_contorno.issubset(px_radial))
        self.assertIn((xc, yc), px_radial)

        # 2. Relleno por Cuerdas / Scanlines
        segs_cuerdas, px_cuerdas = generar_relleno_cuerdas_scanlines(xc, yc, r, pixeles_contorno)
        self.assertTrue(pixeles_contorno.issubset(px_cuerdas))
        ys = {pt[1] for pt in px_cuerdas}
        self.assertEqual(min(ys), yc - r)
        self.assertEqual(max(ys), yc + r)

    def test_circulo_ecuaciones(self):
        # Caso del PDF: Centro (150, 100), R = 10
        ord_pdf, exp_pdf, gen_pdf = get_ecuaciones_circunferencia(150, 100, 10)
        self.assertEqual(ord_pdf, "(X - 150)² + (Y - 100)² = 100")
        self.assertIn("100", exp_pdf)
        self.assertIn("150 - X", exp_pdf)
        self.assertIn("X² + Y²", gen_pdf)
        # D = -300, E = -200, F = 150² + 100² - 100 = 22500 + 10000 - 100 = 32400
        self.assertIn("- 300X", gen_pdf)
        self.assertIn("- 200Y", gen_pdf)
        self.assertIn("+ 32400", gen_pdf)

    def test_circulo_gui_and_navigation(self):
        app = ctk.CTk()
        app.withdraw()
        container = ctk.CTkFrame(app)
        container.pack()

        init_pages(container)
        show_page("circulo")
        self.assertEqual(get_current_page(), "circulo")

        # Verificar que current_circle_data cargue el ejemplo del PDF por defecto
        self.assertTrue(current_circle_data.get("has_data"))
        self.assertEqual(current_circle_data.get("xc"), 150)
        self.assertEqual(current_circle_data.get("yc"), 100)
        self.assertEqual(current_circle_data.get("r"), 10)

        # Renderizado en figura
        fig = Figure(figsize=(5, 4))
        ax = fig.add_subplot(111)
        canvas = FigureCanvasAgg(fig)
        render_circle_plot(ax, fig, canvas)
        self.assertIsNotNone(ax.get_lines())

        app.destroy()


if __name__ == "__main__":
    unittest.main()
