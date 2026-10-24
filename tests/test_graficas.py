"""Pruebas del plano y del dibujo de cada página con el backend Agg (sin ventanas)."""
import math
import unittest

from matplotlib.backend_bases import MouseEvent
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.collections import LineCollection
from matplotlib.figure import Figure

from core.circulo import METODOS_RELLENO, analizar_circulo
from core.recta import generar_puntos_trayectoria, rasterizar_pixeles
from core.triangulo import generar_relleno
from pages.circulo import current_circle_data, render_circle_plot
from pages.puntos_colineales import current_data, render_plot
from pages.triangulo import current_triangle_data, render_triangle_plot
from ui.plano import habilitar_navegacion, setup_ejes


def nuevo_plano():
    figure = Figure(figsize=(5, 5), dpi=100)
    ax = figure.add_subplot(111)
    return figure, ax, FigureCanvasAgg(figure)


class TestGraficas(unittest.TestCase):

    def test_zoom_y_arrastre(self):
        figure, ax, canvas = nuevo_plano()
        setup_ejes(ax, figure, limit=10)
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
        figure, ax, canvas = nuevo_plano()
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

    def test_grafica_triangulo(self):
        # El plano del triángulo dibuja el relleno y los 3 lados con sus píxeles
        pixeles_ab = rasterizar_pixeles(generar_puntos_trayectoria(0, 0, 6, 0))
        relleno = generar_relleno(3, 4, pixeles_ab)
        figure, ax, canvas = nuevo_plano()
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

    def test_grafica_circulo(self):
        figure, ax, canvas = nuevo_plano()
        current_circle_data.clear()
        current_circle_data.update(analizar_circulo(150, 100, 10), has_data=True, modo_vista="Ambos")
        try:
            render_circle_plot(ax, figure, canvas)
            # Sin view se encuadra el círculo: span = max(10 * 1.5, 12) = 15
            self.assertEqual(ax.get_xlim(), (135, 165))
            centro = next(l for l in ax.get_lines() if l.get_label().startswith("Centro"))
            self.assertEqual(centro.get_label(), "Centro C(150, 100)")

            # Relleno con rectas ideales de C a cada píxel B del borde (sin disco sólido)
            self.assertEqual(len(ax.patches), 1)  # solo el círculo de referencia punteado
            segmentos = self._lineas_relleno(ax)
            self.assertEqual(len(segmentos), len(current_circle_data["lineas_info"]))
            for segmento, info in zip(segmentos, current_circle_data["lineas_info"]):
                self.assertEqual([tuple(p) for p in segmento], [info["a"], info["b"]])

            # Escalonado (opcional): cada línea une los píxeles que encendió el DDA
            render_circle_plot(ax, figure, canvas, escalonado=True)
            segmentos = self._lineas_relleno(ax)
            self.assertEqual(
                [[tuple(p) for p in s] for s in segmentos],
                current_circle_data["segmentos_relleno"],
            )

            # Concéntricos ideales: un anillo continuo por cada radio entero
            current_circle_data.update(analizar_circulo(150, 100, 10, METODOS_RELLENO[2]))
            render_circle_plot(ax, figure, canvas)
            anillos = self._lineas_relleno(ax)
            self.assertEqual(len(anillos), 10)
            self.assertAlmostEqual(max(math.hypot(x - 150, y - 100) for x, y in anillos[-1]), 10)

            current_circle_data["modo_vista"] = "Solo Contorno"
            render_circle_plot(ax, figure, canvas, view=((0, 4), (1, 5)))
            self.assertFalse(any(isinstance(c, LineCollection) for c in ax.collections))
            self.assertEqual(ax.get_xlim(), (0, 4))
        finally:
            current_circle_data.clear()

    @staticmethod
    def _lineas_relleno(ax):
        lineas = [c for c in ax.collections if isinstance(c, LineCollection)]
        assert len(lineas) == 1
        return lineas[0].get_segments()


if __name__ == "__main__":
    unittest.main()
