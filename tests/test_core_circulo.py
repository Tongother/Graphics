"""Pruebas rápidas de core/circulo.py (sin ventanas)."""
import math
import unittest

from core.circulo import (
    METODOS_RELLENO,
    algoritmo_punto_medio_circunferencia,
    analizar_circulo,
    fila_octante,
    formula_octante,
    generar_relleno_cuerdas_scanlines,
    generar_relleno_dda_radial,
    get_ecuaciones_circunferencia,
    nombre_octante,
)
from core.recta import generar_puntos_trayectoria, rasterizar_pixeles


class TestCirculo(unittest.TestCase):

    def test_algoritmo_punto_medio(self):
        # Caso del PDF del profesor: Centro (150, 100), Radio R = 10
        pasos, pixeles, _, oct_dict = algoritmo_punto_medio_circunferencia(150, 100, 10)
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
        self.assertEqual(pixeles, {(x + 150, y + 100) for (x, y) in pixeles_origen})

    def test_relleno_dda_radial_y_cuerdas(self):
        xc, yc, r = 150, 100, 10
        _, pixeles_contorno, pts_ordenados, _ = algoritmo_punto_medio_circunferencia(xc, yc, r)

        # 1. Relleno DDA Radial (Pág. 4 del PDF)
        segs_radial, px_radial, lineas_info = generar_relleno_dda_radial(xc, yc, pts_ordenados)
        self.assertEqual(len(segs_radial), len(pts_ordenados))
        self.assertEqual(len(lineas_info), len(pts_ordenados))
        self.assertTrue(pixeles_contorno.issubset(px_radial))
        self.assertIn((xc, yc), px_radial)

        # 2. Relleno por Cuerdas / Scanlines
        _, px_cuerdas = generar_relleno_cuerdas_scanlines(xc, yc, r, pixeles_contorno)
        self.assertTrue(pixeles_contorno.issubset(px_cuerdas))
        ys = {pt[1] for pt in px_cuerdas}
        self.assertEqual(min(ys), yc - r)
        self.assertEqual(max(ys), yc + r)

    def test_ecuaciones(self):
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

    def test_octantes(self):
        self.assertEqual(nombre_octante(1), "Octante 1: (+X, +Y)")
        self.assertEqual(nombre_octante(3), "Octante 3: (-Y, +X)")
        self.assertEqual(formula_octante(3), "(Xc - Y, Yc + X)")
        self.assertEqual(formula_octante(7), "(Xc + Y, Yc - X)")

        pasos, _, _, _ = algoritmo_punto_medio_circunferencia(150, 100, 10)
        # Paso 0: (X, Y) = (1, 10); en el octante 3 queda (-10, 1) -> (140, 101)
        self.assertEqual(fila_octante(pasos[0], 3, 150, 100), ["0", "-10", "1", "(150 - 10, 100 + 1)", "(140, 101)"])
        # La fila siempre coincide con el punto de simetría del algoritmo
        for num_oct in range(1, 9):
            for p in pasos:
                fila = fila_octante(p, num_oct, 150, 100)
                self.assertEqual((150 + int(fila[1]), 100 + int(fila[2])), p["pts"][num_oct - 1])

    # Casos asignados para corroborar la app:
    # (Xc, Yc, R, pasos, primer paso, último paso (N, Pk, X, Y), px de borde, ec. general, huecos DDA radial)
    CASOS_ASIGNADOS = [
        (100, 100, 51, 36, (0, -50, 1, 51), (35, 27, 36, 36), 288, "X² + Y² - 200X - 200Y + 17399 = 0", 580),
        (50, 50, 9, 7, (0, -8, 1, 9), (6, 10, 7, 6), 52, "X² + Y² - 100X - 100Y + 4919 = 0", 20),
        (200, 150, 91, 65, (0, -90, 1, 91), (64, 104, 65, 64), 516, "X² + Y² - 400X - 300Y + 54219 = 0", 1792),
    ]

    def test_casos_asignados(self):
        for xc, yc, r, n_pasos, primero, ultimo, n_borde, general, n_huecos in self.CASOS_ASIGNADOS:
            with self.subTest(C=(xc, yc), R=r):
                datos = analizar_circulo(xc, yc, r)
                filas = [(p["k"], p["pk"], p["x_sig"], p["y_sig"]) for p in datos["pasos"]]
                self.assertEqual(len(filas), n_pasos)
                self.assertEqual(filas[0], primero)
                self.assertEqual(filas[-1], ultimo)
                self.assertGreaterEqual(ultimo[2], ultimo[3])  # termina cuando X >= Y
                self.assertEqual(len(datos["pixeles_contorno"]), n_borde)
                self.assertEqual(datos["general"], general)
                self.assertEqual(len(datos["pixeles_huecos"]), n_huecos)

                # Cada píxel del borde queda a menos de medio píxel del círculo real
                for px, py in datos["pixeles_contorno"]:
                    self.assertLess(abs(math.hypot(px - xc, py - yc) - r), 0.5)

    def test_relleno_radial_usa_programa_de_la_linea(self):
        for xc, yc, r, *_ in self.CASOS_ASIGNADOS:
            with self.subTest(C=(xc, yc), R=r):
                datos = analizar_circulo(xc, yc, r, METODOS_RELLENO[0])
                esperado = set()
                lineas = zip(datos["lineas_info"], datos["segmentos_relleno"], datos["puntos_ordenados"])
                for info, linea, (bx, by) in lineas:
                    # Cada línea que se dibuja son los píxeles del DDA de C a B
                    pixeles = rasterizar_pixeles(generar_puntos_trayectoria(xc, yc, bx, by))
                    self.assertEqual(linea, pixeles)
                    self.assertEqual(info["num_px"], len(pixeles))
                    esperado.update(pixeles)
                self.assertEqual(datos["pixeles_relleno"], esperado)

                # Concéntricos: un anillo cerrado por cada radio entero de 1 a r
                anillos = analizar_circulo(xc, yc, r, METODOS_RELLENO[2])["segmentos_relleno"]
                self.assertEqual(len(anillos), r)
                self.assertTrue(all(anillo[0] == anillo[-1] for anillo in anillos))

                # Método puro: el relleno queda dentro del contorno y lo que falta son huecos
                interior = analizar_circulo(xc, yc, r, METODOS_RELLENO[1])["pixeles_relleno"]
                self.assertTrue(datos["pixeles_relleno"] <= interior)
                self.assertEqual(datos["pixeles_relleno"] | datos["pixeles_huecos"], interior)

    def test_analizar_circulo(self):
        for metodo in METODOS_RELLENO:
            with self.subTest(metodo=metodo):
                datos = analizar_circulo(150, 100, 10, metodo)
                self.assertEqual(len(datos["pasos"]), 7)
                self.assertEqual(datos["p0"], -9)
                self.assertTrue(datos["pixeles_relleno"])
                self.assertEqual(bool(datos["lineas_info"]), "DDA Radial" in metodo)


if __name__ == "__main__":
    unittest.main()
