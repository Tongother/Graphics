"""
Recta entre dos puntos: pendiente, ecuación, clasificación de los 11 casos de
trazo del documento y rasterización con DDA.
"""
import math
from fractions import Fraction


def get_pendiente(x1, y1, x2, y2):
    pendiente = (y2 - y1) / (x2 - x1)
    # Evita el "-0" que resulta de dividir 0 entre un número negativo
    return 0.0 if pendiente == 0 else pendiente


def get_ordenada(x1, y1, pendiente):
    return y1 - pendiente * x1


def get_ecuacion_recta(x1, y1, pendiente):
    ordenada = get_ordenada(x1, y1, pendiente)
    if pendiente == 0:
        return f"y = {ordenada:g}"

    if pendiente == 1:
        termino_x = "x"
    elif pendiente == -1:
        termino_x = "-x"
    else:
        termino_x = f"{pendiente:g}x"

    if ordenada == 0:
        return f"y = {termino_x}"
    signo = "+" if ordenada > 0 else "-"
    return f"y = {termino_x} {signo} {abs(ordenada):g}"


def formatear_pendiente(dx, dy):
    """Pendiente como fracción reducida (2/5) cuando es exacta; si no, en decimal."""
    m = dy / dx
    fraccion = (Fraction(str(dy)) / Fraction(str(dx))).limit_denominator(1000)
    texto = str(fraccion) if abs(float(fraccion) - m) < 1e-9 else f"{m:.4g}"
    return texto.replace("-", "−")


def clasificar_recta(dx, dy):
    """
    Identifica el caso de trazo según los incrementos ΔX y ΔY, con la agrupación
    del documento: 4 positivos, 4 negativos y 3 especiales (45°, horizontal y
    vertical). Cada inclinación se dibuja en los dos sentidos y cada sentido es
    un caso distinto.
    Retorna una tupla (caso, detalle, notacion).
    """
    if dx == 0 and dy == 0:
        # No es un caso del documento: solo protege contra A = B
        return "Un solo punto", "A y B son iguales: no hay recorrido", "Sin recorrido: ΔX = 0 y ΔY = 0"

    sx = "+" if dx > 0 else "−"
    sy = "+" if dy > 0 else "−"
    sentido_x = "izquierda → derecha" if dx > 0 else "derecha → izquierda"

    if dy == 0:
        return "Especial: horizontal", sentido_x, f"m = 0 · Xₖ₊₁ = Xₖ {sx} 1 · Y no cambia"

    if dx == 0:
        sentido_y = "abajo → arriba" if dy > 0 else "arriba → abajo"
        return "Especial: vertical", sentido_y, f"m = Error (indefinida) · Yₖ₊₁ = Yₖ {sy} 1 · X no cambia"

    if abs(abs(dx) - abs(dy)) < 1e-9:
        inciso, flecha = {
            ("+", "+"): ("a", "↗"),
            ("+", "−"): ("b", "↘"),
            ("−", "−"): ("c", "↙"),
            ("−", "+"): ("d", "↖"),
        }[(sx, sy)]
        m = "1" if sx == sy else "−1"
        sentido_y = "subiendo" if dy > 0 else "bajando"
        return (
            f"Especial 45° {inciso}) {flecha}",
            f"Diagonal, {sentido_x}, {sentido_y}",
            f"m = {m} · Xₖ₊₁ = Xₖ {sx} 1 · Yₖ₊₁ = Yₖ {sy} 1"
        )

    acostada = abs(dy) < abs(dx)
    if (dx > 0) == (dy > 0):
        # Positivo 1 y 3 van de izquierda a derecha; 2 y 4 de derecha a izquierda
        numero = (1 if acostada else 3) + (0 if dx > 0 else 1)
        grupo, trazo, clase = "Positivo", "/", "+m<1" if acostada else "+m>1"
        paso_m, paso_inv = "m", "1/m"
    else:
        # Negativo 1 y 3 van de derecha a izquierda; 2 y 4 de izquierda a derecha
        numero = (1 if acostada else 3) + (0 if dx < 0 else 1)
        grupo, trazo, clase = "Negativo", "\\", "|−m|<1" if acostada else "|−m|>1"
        paso_m, paso_inv = "|m|", "1/|m|"

    if acostada:
        formula = f"Xₖ₊₁ = Xₖ {sx} 1 · Yₖ₊₁ = Yₖ {sy} {paso_m}"
    else:
        formula = f"Yₖ₊₁ = Yₖ {sy} 1 · Xₖ₊₁ = Xₖ {sx} {paso_inv}"

    inclinacion = "Acostada" if acostada else "Parada"
    return (
        f"{grupo} {numero}",
        f"{inclinacion} {trazo}, {sentido_x}",
        f"{clase}, m = {formatear_pendiente(dx, dy)} · {formula}"
    )


def redondear_pixel(valor):
    """
    Posición del píxel: el entero más cercano, con las mitades hacia arriba.
    No se usa round() porque redondea 0.5 al par (round(2.5) == 2).
    """
    return math.floor(valor + 0.5)


def get_direccion_x(dx):
    if dx > 0:
        return "Izquierda a Derecha"
    elif dx < 0:
        return "Derecha a Izquierda"
    return "Sin cambio horizontal"


def get_direccion_y(dy):
    if dy > 0:
        return "Abajo a Arriba"
    elif dy < 0:
        return "Arriba a Abajo"
    return "Sin cambio vertical"


def get_comportamiento_pendiente(m):
    if m > 0:
        return "Ascendente"
    elif m < 0:
        return "Descendente"
    return "Horizontal"


def generar_puntos_trayectoria(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    pasos = int(max(abs(dx), abs(dy)))
    puntos = []

    if dx == 0 and dy == 0:
        return [(0, x1, y1)]
    if pasos == 0:
        # Puntos distintos a menos de una unidad: un solo paso de A a B
        pasos = 1

    # Un eje avanza ±1 por paso y el otro ±|m| (o ±1/|m|). Se calcula A + i·paso
    # en lugar de sumar el paso en cada vuelta para no acumular error de redondeo.
    step_x = dx / pasos
    step_y = dy / pasos

    for i in range(pasos + 1):
        px = x1 + i * step_x
        py = y1 + i * step_y
        if abs(px - round(px)) < 1e-7:
            px = int(round(px))
        else:
            px = round(px, 4)
        if abs(py - round(py)) < 1e-7:
            py = int(round(py))
        else:
            py = round(py, 4)
        puntos.append((i, px, py))

    return puntos


def rasterizar_pixeles(puntos):
    """Píxeles que enciende el DDA: cada punto (paso, X, Y) redondeado a enteros."""
    return [(redondear_pixel(px), redondear_pixel(py)) for _, px, py in puntos]


def calcular_limite(valores, proporcion):
    """Medio ancho del plano para que quepan todos los valores, con un margen proporcional."""
    max_val = max(abs(v) for v in valores)
    if max_val == 0:
        max_val = 10
    return max_val + max(2, int(max_val * proporcion) + 1)


def analizar_recta(x1, y1, x2, y2):
    """Todos los datos de la recta AB que muestra la página (métricas, caso y tabla)."""
    delta_x = x2 - x1
    delta_y = y2 - y1
    caso, caso_detalle, notacion = clasificar_recta(delta_x, delta_y)

    if delta_x == 0 and delta_y == 0:
        # Un solo punto: no hay recta, pendiente ni ángulo
        pendiente = ordenada = angulo = None
        comportamiento = "Sin dirección (un solo punto)"
        equation = f"Punto ({x1:g}, {y1:g})"
    elif delta_x == 0:
        # Recta vertical: la pendiente es indefinida (división entre cero)
        pendiente = ordenada = None
        comportamiento = "Vertical"
        angulo = 90.0
        equation = f"x = {x1:g}"
    else:
        pendiente = get_pendiente(x1, y1, x2, y2)
        ordenada = get_ordenada(x1, y1, pendiente)
        comportamiento = get_comportamiento_pendiente(pendiente)
        angulo = math.degrees(math.atan(pendiente))
        equation = get_ecuacion_recta(x1, y1, pendiente)

    return {
        "x1": x1,
        "y1": y1,
        "x2": x2,
        "y2": y2,
        "pendiente": pendiente,
        "ordenada": ordenada,
        "comportamiento": comportamiento,
        "angulo": angulo,
        "equation": equation,
        "caso": caso,
        "caso_detalle": caso_detalle,
        "notacion": notacion,
        "delta_x": delta_x,
        "delta_y": delta_y,
        "dir_x": get_direccion_x(delta_x),
        "dir_y": get_direccion_y(delta_y),
        "limit": calcular_limite((x1, y1, x2, y2), 0.15),
        "table_points": generar_puntos_trayectoria(x1, y1, x2, y2),
    }
