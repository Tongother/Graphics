"""Pruebas rápidas de core/recta.py (sin ventanas)."""
import unittest

from core.recta import (
    analizar_recta,
    clasificar_recta,
    generar_puntos_trayectoria,
    get_direccion_x,
    get_direccion_y,
    get_ecuacion_recta,
    get_ordenada,
    get_pendiente,
    rasterizar_pixeles,
    redondear_pixel,
)
from tests.casos import CASOS_RECTA


class TestRecta(unittest.TestCase):

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

    def test_clasificacion_casos(self):
        for (x1, y1), (x2, y2), esperado, notacion in CASOS_RECTA:
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
        self.assertEqual(rasterizar_pixeles(puntos), [(0, 0), (1, 0), (2, 1), (3, 1), (4, 2), (5, 2)])

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

    def test_ecuaciones_casos(self):
        self.assertEqual(get_ecuacion_recta(1, 2, get_pendiente(1, 2, 6, 2)), "y = 2")
        self.assertEqual(get_ecuacion_recta(6, 2, get_pendiente(6, 2, 1, 2)), "y = 2")
        self.assertEqual(get_ecuacion_recta(0, 0, get_pendiente(0, 0, 5, 5)), "y = x")
        self.assertEqual(get_ecuacion_recta(0, 3, get_pendiente(0, 3, 3, 0)), "y = -x + 3")
        self.assertEqual(get_ecuacion_recta(0, -3, get_pendiente(0, -3, 1, -1)), "y = 2x - 3")

    def test_analizar_recta(self):
        datos = analizar_recta(1, 2, 5, 8)
        self.assertEqual(datos["pendiente"], 1.5)
        self.assertEqual(datos["caso"], "Positivo 3")
        self.assertEqual(len(datos["table_points"]), 7)
        self.assertEqual(datos["limit"], 10)

        vertical = analizar_recta(3, 1, 3, 7)
        self.assertIsNone(vertical["pendiente"])
        self.assertEqual(vertical["equation"], "x = 3")
        self.assertEqual(vertical["angulo"], 90.0)

        punto = analizar_recta(2, 3, 2, 3)
        self.assertIsNone(punto["angulo"])
        self.assertEqual(punto["caso"], "Un solo punto")


if __name__ == "__main__":
    unittest.main()
