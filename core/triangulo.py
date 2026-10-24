"""
Triángulo ABC: métricas geométricas (área, perímetro, longitudes, pendientes),
clasificación por lados y ángulos, trazo de los lados AB, BC y CA con DDA y
relleno con líneas DDA desde cada vértice fijo hacia el lado opuesto.
"""
import math

from core.recta import (
    calcular_limite,
    clasificar_recta,
    generar_puntos_trayectoria,
    rasterizar_pixeles,
    redondear_pixel,
)

LADOS = ("AB", "BC", "CA")


def distancia_euclidiana(x1, y1, x2, y2):
    """Calcula la distancia euclidiana entre dos puntos 2D."""
    return math.hypot(x2 - x1, y2 - y1)


def calcular_area_triangulo(x1, y1, x2, y2, x3, y3):
    """
    Calcula el área del triángulo usando la fórmula del determinante de Gauss (Shoelace).
    Retorna el área no negativa.
    """
    area = 0.5 * abs(x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))
    return area


def calcular_perimetro_triangulo(d_ab, d_bc, d_ca):
    """Suma las tres longitudes de lado."""
    return d_ab + d_bc + d_ca


def clasificar_por_lados(d_ab, d_bc, d_ca, tol=1e-4):
    """Clasifica el triángulo en Equilátero, Isósceles o Escaleno."""
    eq_ab_bc = abs(d_ab - d_bc) < tol
    eq_bc_ca = abs(d_bc - d_ca) < tol
    eq_ca_ab = abs(d_ca - d_ab) < tol

    if eq_ab_bc and eq_bc_ca and eq_ca_ab:
        return "Equilátero"
    elif eq_ab_bc or eq_bc_ca or eq_ca_ab:
        return "Isósceles"
    return "Escaleno"


def clasificar_por_angulos(d_ab, d_bc, d_ca, tol=1e-3):
    """
    Clasifica el triángulo según sus ángulos internos:
    Rectángulo (a² + b² = c²), Acutángulo (a² + b² > c²), u Obtusángulo (a² + b² < c²).
    """
    s1, s2, s3 = sorted([d_ab, d_bc, d_ca])
    diff = (s1**2 + s2**2) - s3**2

    if abs(diff) < tol:
        return "Rectángulo"
    elif diff > 0:
        return "Acutángulo"
    else:
        return "Obtusángulo"


def calcular_pendiente_segura(x1, y1, x2, y2):
    """Calcula la pendiente m entre dos puntos, manejando rectas verticales."""
    if x2 == x1:
        return None, "Vertical (indefinida)"
    m = (y2 - y1) / (x2 - x1)
    return m, f"{m:g}"


def generar_relleno(xc, yc, pixeles_ab):
    """
    Relleno del triángulo con el método del documento: C queda como punto fijo
    y, en un ciclo que se repite N veces (N = puntos de la tabla de AB), se
    traza con DDA la línea de C a cada píxel de AB. La misma función sirve con
    cualquier vértice fijo y los píxeles de su lado opuesto.
    Retorna una lista de líneas, cada una como lista de píxeles (x, y).
    """
    return [
        rasterizar_pixeles(generar_puntos_trayectoria(xc, yc, px, py))
        for px, py in pixeles_ab
    ]


def ajustar_al_contorno(relleno, pixeles_lados):
    """
    Mantiene el relleno dentro del triángulo. Cuando una línea de relleno es casi
    paralela a un lado, el redondeo del DDA puede dejar un píxel fuera del borde;
    en cada fila Y, ese píxel se recorre hasta el píxel del borde de esa fila.
    """
    limites = {}
    for pixeles in pixeles_lados:
        for x, y in pixeles:
            izq, der = limites.get(y, (x, x))
            limites[y] = (min(izq, x), max(der, x))

    ajustado = []
    for linea in relleno:
        nueva = []
        for x, y in linea:
            izq, der = limites.get(y, (x, x))
            nueva.append((min(max(x, izq), der), y))
        ajustado.append(nueva)
    return ajustado


def vertices_coinciden(x1, y1, x2, y2, x3, y3):
    """True si al menos dos vértices tienen exactamente las mismas coordenadas."""
    return (x1 == x2 and y1 == y2) or (x2 == x3 and y2 == y3) or (x3 == x1 and y3 == y1)


def analizar_triangulo(x1, y1, x2, y2, x3, y3):
    """
    Todos los datos del triángulo que muestra la página: métricas, clasificación,
    caso DDA, pasos y píxeles de cada lado y el relleno.
    Se asume que los vértices son distintos (ver vertices_coinciden).
    """
    # Cálculo de distancias (longitudes de lados)
    d_ab = distancia_euclidiana(x1, y1, x2, y2)
    d_bc = distancia_euclidiana(x2, y2, x3, y3)
    d_ca = distancia_euclidiana(x3, y3, x1, y1)

    perimetro = calcular_perimetro_triangulo(d_ab, d_bc, d_ca)
    area = calcular_area_triangulo(x1, y1, x2, y2, x3, y3)
    es_colineal = (area < 1e-6)

    # Clasificaciones
    if es_colineal:
        tipo_lados = "Colineal"
        tipo_angulos = "Plano (180°)"
        estado_texto = "Puntos Colineales (Degenerado)"
    else:
        tipo_lados = clasificar_por_lados(d_ab, d_bc, d_ca)
        tipo_angulos = clasificar_por_angulos(d_ab, d_bc, d_ca)
        estado_texto = "Triángulo Válido"

    # El DDA trabaja con píxeles: cada vértice se ubica primero en su píxel para
    # que los lados y el relleno partan exactamente de los mismos puntos
    pa = (redondear_pixel(x1), redondear_pixel(y1))
    pb = (redondear_pixel(x2), redondear_pixel(y2))
    pc = (redondear_pixel(x3), redondear_pixel(y3))

    # Pendientes de las líneas que se trazan
    m_ab, str_m_ab = calcular_pendiente_segura(*pa, *pb)
    m_bc, str_m_bc = calcular_pendiente_segura(*pb, *pc)
    m_ca, str_m_ca = calcular_pendiente_segura(*pc, *pa)

    # Las 3 líneas del triángulo con el programa de la línea (DDA): AB, BC y CA
    lados = {
        "AB": (*pa, *pb),
        "BC": (*pb, *pc),
        "CA": (*pc, *pa),
    }
    pasos = {lado: generar_puntos_trayectoria(*coords) for lado, coords in lados.items()}
    pixeles = {lado: rasterizar_pixeles(puntos) for lado, puntos in pasos.items()}
    casos = {
        lado: clasificar_recta(xb - xa, yb - ya)
        for lado, (xa, ya, xb, yb) in lados.items()
    }

    # Relleno: el método del documento (C fijo hacia cada píxel de AB) se repite
    # con A hacia BC y con B hacia CA; las líneas se cruzan y tapan los huecos
    relleno = ajustar_al_contorno(
        generar_relleno(*pc, pixeles["AB"])
        + generar_relleno(*pa, pixeles["BC"])
        + generar_relleno(*pb, pixeles["CA"]),
        pixeles.values(),
    )

    return {
        "x1": x1, "y1": y1,
        "x2": x2, "y2": y2,
        "x3": x3, "y3": y3,
        "d_ab": d_ab, "d_bc": d_bc, "d_ca": d_ca,
        "perimetro": perimetro,
        "semiperimetro": perimetro / 2.0,
        "area": area,
        "es_colineal": es_colineal,
        "tipo_lados": tipo_lados,
        "tipo_angulos": tipo_angulos,
        "estado_texto": estado_texto,
        "m_ab": m_ab, "m_bc": m_bc, "m_ca": m_ca,
        "str_m_ab": str_m_ab, "str_m_bc": str_m_bc, "str_m_ca": str_m_ca,
        "limit": calcular_limite((x1, y1, x2, y2, x3, y3), 0.2),
        # Tabla unificada con etiqueta de segmento
        "table_points": [
            (lado, paso, px, py)
            for lado in LADOS
            for paso, px, py in pasos[lado]
        ],
        "lados": lados,
        "pasos": pasos,
        "pixeles": pixeles,
        "casos": casos,
        "relleno": relleno,
    }
