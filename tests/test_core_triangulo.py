"""Pruebas rápidas de core/triangulo.py (sin ventanas)."""
import unittest

from core.recta import generar_puntos_trayectoria, rasterizar_pixeles
from core.triangulo import (
    ajustar_al_contorno,
    analizar_triangulo,
    calcular_area_triangulo,
    calcular_pendiente_segura,
    calcular_perimetro_triangulo,
    clasificar_por_angulos,
    clasificar_por_lados,
    distancia_euclidiana,
    generar_relleno,
    vertices_coinciden,
)


class TestTriangulo(unittest.TestCase):

    def test_triangle_math_and_classifications(self):
        # Triángulo rectángulo notable (3, 4, 5): (0,0), (4,0), (0,3)
        d_ab = distancia_euclidiana(0, 0, 4, 0)  # 4
        d_bc = distancia_euclidiana(4, 0, 0, 3)  # 5
        d_ca = distancia_euclidiana(0, 3, 0, 0)  # 3

        self.assertAlmostEqual(d_ab, 4.0)
        self.assertAlmostEqual(d_bc, 5.0)
        self.assertAlmostEqual(d_ca, 3.0)

        # Área = (base * altura) / 2 = (4 * 3) / 2 = 6
        self.assertAlmostEqual(calcular_area_triangulo(0, 0, 4, 0, 0, 3), 6.0)

        # Perímetro = 3 + 4 + 5 = 12
        self.assertAlmostEqual(calcular_perimetro_triangulo(d_ab, d_bc, d_ca), 12.0)

        # Clasificación por lados: Escaleno; por ángulos: Rectángulo (4² + 3² = 5²)
        self.assertEqual(clasificar_por_lados(d_ab, d_bc, d_ca), "Escaleno")
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
        d_ob1 = distancia_euclidiana(0, 0, 5, 0)
        d_ob2 = distancia_euclidiana(5, 0, 1, 1)
        d_ob3 = distancia_euclidiana(1, 1, 0, 0)
        self.assertEqual(clasificar_por_angulos(d_ob1, d_ob2, d_ob3), "Obtusángulo")

        # Puntos Colineales: Área debe ser 0
        self.assertAlmostEqual(calcular_area_triangulo(1, 1, 2, 2, 3, 3), 0.0)

        # Pendiente segura
        m_normal, str_m = calcular_pendiente_segura(1, 1, 3, 5)
        self.assertAlmostEqual(m_normal, 2.0)
        self.assertEqual(str_m, "2")

        m_vert, str_vert = calcular_pendiente_segura(2, 1, 2, 8)
        self.assertIsNone(m_vert)
        self.assertIn("Vertical", str_vert)

    def test_relleno_desde_c(self):
        pixeles_ab = rasterizar_pixeles(generar_puntos_trayectoria(0, 0, 6, 0))
        relleno = generar_relleno(3, 4, pixeles_ab)
        self.assertEqual(len(relleno), len(pixeles_ab))
        for linea, destino in zip(relleno, pixeles_ab):
            # Cada línea empieza en C y termina en un píxel de AB
            self.assertEqual(linea[0], (3, 4))
            self.assertEqual(linea[-1], destino)

    def test_ajustar_al_contorno(self):
        # Un píxel fuera del borde de su fila se recorre al borde; los de adentro no cambian
        contorno = [[(0, 0), (4, 0)], [(4, 0), (3, 1), (2, 2)], [(2, 2), (1, 1), (0, 0)]]
        self.assertEqual(ajustar_al_contorno([[(5, 0), (0, 1), (2, 1)]], contorno), [[(4, 0), (1, 1), (2, 1)]])

    def test_analizar_triangulo(self):
        # Vértices por defecto de la página: (1,1), (7,2), (3,7)
        datos = analizar_triangulo(1, 1, 7, 2, 3, 7)
        self.assertFalse(datos["es_colineal"])
        self.assertGreater(datos["area"], 0)

        # Caso DDA de cada lado: AB (1,1)→(7,2), BC (7,2)→(3,7), CA (3,7)→(1,1)
        self.assertEqual(datos["casos"]["AB"][0], "Positivo 1")
        self.assertEqual(datos["casos"]["BC"][0], "Negativo 3")
        self.assertEqual(datos["casos"]["CA"][0], "Positivo 4")

        # Relleno: una línea DDA desde cada vértice por cada píxel de su lado opuesto
        pixeles, relleno = datos["pixeles"], datos["relleno"]
        self.assertEqual(len(relleno), sum(len(p) for p in pixeles.values()))
        self.assertEqual(relleno[0][0], (3, 7))                     # C -> AB
        self.assertEqual(relleno[len(pixeles["AB"])][0], (1, 1))    # A -> BC

    def test_equilatero_relleno_dentro(self):
        # C decimal: los vértices se ubican en su píxel y ningún píxel del relleno sale de los lados
        datos = analizar_triangulo(0, 0, 10, 0, 5, 8.660254)
        self.assertEqual(datos["tipo_lados"], "Equilátero")
        self.assertEqual(datos["pixeles"]["CA"][0], (5, 9))
        filas = {}
        for pixeles in datos["pixeles"].values():
            for x, y in pixeles:
                filas.setdefault(y, []).append(x)
        for linea in datos["relleno"]:
            for x, y in linea:
                self.assertTrue(min(filas[y]) <= x <= max(filas[y]))

    def test_colineales_y_coincidentes(self):
        datos = analizar_triangulo(1, 1, 2, 2, 3, 3)
        self.assertTrue(datos["es_colineal"])
        self.assertEqual(datos["tipo_lados"], "Colineal")
        self.assertTrue(vertices_coinciden(1, 1, 1, 1, 3, 3))
        self.assertFalse(vertices_coinciden(1, 1, 2, 2, 3, 3))


if __name__ == "__main__":
    unittest.main()
