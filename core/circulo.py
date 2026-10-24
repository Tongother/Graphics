"""
Circunferencia y círculo relleno.
1. Ecuaciones analíticas: Teorema de Pitágoras (X - Xc)² + (Y - Yc)² = r², ecuación explícita
   Y = Yc ± √(r² - (Xc - X)²) y ecuación general X² + Y² + DX + EY + F = 0.
2. Algoritmo de Punto Medio de Bresenham para circunferencia con parámetro inicial
   P0 = 1 - r (o 5/4 - r) y prueba en cada Xk:
     - Si Pk < 0: Pk+1 = Pk + 2*Xk+1 + 1, con (Xk+1, Yk)
     - Si Pk >= 0: Pk+1 = Pk + 2*Xk+1 + 1 - 2*Yk+1, con (Xk+1, Yk-1)
     - Ciclo hasta X >= Y.
3. Simetría de 8 Octantes con traslación bidimensional C(Xc, Yc).
4. Relleno del círculo:
   - DDA Radial: Centro fijo A(Xc, Yc) hacia cada píxel B de los 8 octantes trazado con DDA (11 casos).
   - Cuerdas (Scanlines horizontales) y Círculos concéntricos.
"""
import math

from core.recta import clasificar_recta, generar_puntos_trayectoria, rasterizar_pixeles, redondear_pixel

# Opciones del menú "Método de Relleno"; el código las distingue por subcadena
METODO_DDA = "DDA Radial (Centro a Octantes)"
METODO_CUERDAS = "Cuerdas (Líneas Horizontales / Scanline)"
METODO_CONCENTRICO = "Círculos Concéntricos"
METODOS_RELLENO = (METODO_DDA, METODO_CUERDAS, METODO_CONCENTRICO)

# Octante n -> (intercambia X/Y, signo de la 1a coordenada, signo de la 2a),
# en el mismo orden que los puntos de simetría de algoritmo_punto_medio_circunferencia
OCTANTES = (
    (False, 1, 1),    # Oct 1: (+x, +y)
    (True, 1, 1),     # Oct 2: (+y, +x)
    (True, -1, 1),    # Oct 3: (-y, +x)
    (False, -1, 1),   # Oct 4: (-x, +y)
    (False, -1, -1),  # Oct 5: (-x, -y)
    (True, -1, -1),   # Oct 6: (-y, -x)
    (True, 1, -1),    # Oct 7: (+y, -x)
    (False, 1, -1),   # Oct 8: (+x, -y)
)


def _signo(s):
    return "+" if s > 0 else "-"


def nombre_octante(num_oct):
    """'Octante 3: (-Y, +X)'"""
    swap, sx, sy = OCTANTES[num_oct - 1]
    a, b = ("Y", "X") if swap else ("X", "Y")
    return f"Octante {num_oct}: ({_signo(sx)}{a}, {_signo(sy)}{b})"


def formula_octante(num_oct):
    """'(Xc - Y, Yc + X)'"""
    swap, sx, sy = OCTANTES[num_oct - 1]
    a, b = ("Y", "X") if swap else ("X", "Y")
    return f"(Xc {_signo(sx)} {a}, Yc {_signo(sy)} {b})"


def fila_octante(paso, num_oct, xc, yc):
    """Fila de la tabla de un octante: [paso, X relativo, Y relativo, fórmula, píxel]."""
    swap, sx, sy = OCTANTES[num_oct - 1]
    xs, ys = paso["x_sig"], paso["y_sig"]
    a, b = (ys, xs) if swap else (xs, ys)
    pt = paso["pts"][num_oct - 1]
    calc_str = f"({xc} {_signo(sx)} {a}, {yc} {_signo(sy)} {b})"
    return [str(paso["k"]), str(sx * a), str(sy * b), calc_str, f"({pt[0]}, {pt[1]})"]


def algoritmo_punto_medio_circunferencia(xc, yc, r, usar_fraccion=False):
    """
    Algoritmo de Punto Medio de Bresenham para la Circunferencia.
    Punto inicial: (X0, Y0) = (0, r).
    P0 = 5/4 - r o P0 = 1 - r.
    Repite hasta que X >= Y.
    """
    r = redondear_pixel(r)
    xc = redondear_pixel(xc)
    yc = redondear_pixel(yc)

    x = 0
    y = r
    p0 = (1.25 - r) if usar_fraccion else (1 - r)
    p = p0

    pasos = []
    pixeles_contorno = set()
    octantes_dict = {i: [] for i in range(1, 9)}

    # Puntos cardinales del punto inicial (0, r)
    puntos_iniciales = [
        (xc + 0, yc + r),
        (xc + 0, yc - r),
        (xc + r, yc + 0),
        (xc - r, yc + 0),
    ]
    for pt in puntos_iniciales:
        pixeles_contorno.add(pt)

    k = 0
    while x < y:
        x_sig = x + 1
        p_actual = p

        if p < 0:
            y_sig = y
            delta = 2 * x_sig + 1
            p_sig = p + delta
            formula_txt = f"{p_actual:g} + 2({x_sig}) + 1 = {p_sig:g}"
            decision_txt = f"Pₖ < 0 → (Xₖ₊₁, Yₖ) = ({x_sig}, {y_sig})"
        else:
            y_sig = y - 1
            delta = 2 * x_sig + 1 - 2 * y_sig
            p_sig = p + delta
            formula_txt = f"{p_actual:g} + 2({x_sig}) + 1 - 2({y_sig}) = {p_sig:g}"
            decision_txt = f"Pₖ ≥ 0 → (Xₖ₊₁, Yₖ₋₁) = ({x_sig}, {y_sig})"

        # Simetría en los 8 Octantes con traslación del centro (Xc, Yc)
        pts_simetria = [
            (xc + x_sig, yc + y_sig),  # Oct 1: (+x, +y)
            (xc + y_sig, yc + x_sig),  # Oct 2: (+y, +x)
            (xc - y_sig, yc + x_sig),  # Oct 3: (-y, +x)
            (xc - x_sig, yc + y_sig),  # Oct 4: (-x, +y)
            (xc - x_sig, yc - y_sig),  # Oct 5: (-x, -y)
            (xc - y_sig, yc - x_sig),  # Oct 6: (-y, -x)
            (xc + y_sig, yc - x_sig),  # Oct 7: (+y, -x)
            (xc + x_sig, yc - y_sig),  # Oct 8: (+x, -y)
        ]

        for idx, pt in enumerate(pts_simetria, start=1):
            octantes_dict[idx].append(pt)
            pixeles_contorno.add(pt)

        pasos.append({
            "k": k,
            "pk": p_actual,
            "x_sig": x_sig,
            "y_sig": y_sig,
            "formula": formula_txt,
            "decision": decision_txt,
            "base_trans": (xc + x_sig, yc + y_sig),
            "pts": pts_simetria
        })

        x = x_sig
        y = y_sig
        p = p_sig
        k += 1

        if x >= y:
            break

    puntos_ordenados = sorted(
        pixeles_contorno,
        key=lambda pt: math.atan2(pt[1] - yc, pt[0] - xc)
    )

    return pasos, pixeles_contorno, puntos_ordenados, octantes_dict


def generar_relleno_dda_radial(xc, yc, puntos_borde):
    """
    Relleno del Círculo con el método del documento: el centro A(Xc, Yc) queda
    fijo y, en un ciclo sobre el arreglo con los píxeles B de los 8 octantes, se
    corre el programa de la línea DDA (11 casos) de A a cada B.
    El método puro deja huecos entre líneas vecinas en la mitad exterior.
    Retorna (líneas como listas de píxeles, píxeles encendidos, info de cada línea).
    """
    lineas_segmentos = []
    lineas_info = []
    pixeles_relleno = set()

    for idx, (bx, by) in enumerate(puntos_borde, start=1):
        dx = bx - xc
        dy = by - yc
        pixeles_linea = rasterizar_pixeles(generar_puntos_trayectoria(xc, yc, bx, by))
        pixeles_relleno.update(pixeles_linea)

        lineas_segmentos.append(pixeles_linea)
        caso, _, notacion = clasificar_recta(dx, dy)

        lineas_info.append({
            "num": idx,
            "a": (xc, yc),
            "b": (bx, by),
            "dist": math.hypot(dx, dy),
            "caso": caso,
            "notacion": notacion,
            "num_px": len(pixeles_linea)
        })

    return lineas_segmentos, pixeles_relleno, lineas_info


def generar_relleno_cuerdas_scanlines(xc, yc, r, pixeles_contorno):
    """
    Método de Cuerdas (Scanlines): Conecta de extremo a extremo cada fila horizontal.
    """
    filas = {}
    for px, py in pixeles_contorno:
        if py not in filas:
            filas[py] = [px, px]
        else:
            if px < filas[py][0]:
                filas[py][0] = px
            if px > filas[py][1]:
                filas[py][1] = px

    segmentos = []
    pixeles_relleno = set()

    for py in sorted(filas.keys()):
        xmin, xmax = filas[py]
        segmentos.append(((xmin, py), (xmax, py)))
        for x in range(xmin, xmax + 1):
            pixeles_relleno.add((x, py))

    return segmentos, pixeles_relleno


def generar_relleno_concentrico(xc, yc, r):
    """
    Método de Círculos Concéntricos: Dibuja circunferencias con radios enteros de 1 a r.
    Retorna (cada anillo como línea cerrada de píxeles ordenados por ángulo, píxeles encendidos).
    """
    segmentos = []
    pixeles_relleno = set()
    r_int = redondear_pixel(r)

    for rad in range(1, r_int + 1):
        anillo = set()
        x = 0
        y = rad
        p = 1 - rad
        while x <= y:
            anillo.add((xc + x, yc + y))
            anillo.add((xc + y, yc + x))
            anillo.add((xc - y, yc + x))
            anillo.add((xc - x, yc + y))
            anillo.add((xc - x, yc - y))
            anillo.add((xc - y, yc - x))
            anillo.add((xc + y, yc - x))
            anillo.add((xc + x, yc - y))
            x += 1
            if p < 0:
                p += 2 * x + 1
            else:
                y -= 1
                p += 2 * (x - y) + 1

        pixeles_relleno |= anillo
        ordenado = sorted(anillo, key=lambda pt: math.atan2(pt[1] - yc, pt[0] - xc))
        segmentos.append(ordenado + ordenado[:1])

    return segmentos, pixeles_relleno


def get_ecuaciones_circunferencia(xc, yc, r):
    """
    Genera las ecuaciones de la circunferencia:
    - Ordinaria: (X - Xc)² + (Y - Yc)² = r²
    - Explícita: Y = Yc ± √(r² - (Xc - X)²)
    - General:   X² + Y² + DX + EY + F = 0
    """
    r_sq = r ** 2

    if xc == 0:
        term_x = "X²"
    elif xc > 0:
        term_x = f"(X - {xc:g})²"
    else:
        term_x = f"(X + {abs(xc):g})²"

    if yc == 0:
        term_y = "Y²"
    elif yc > 0:
        term_y = f"(Y - {yc:g})²"
    else:
        term_y = f"(Y + {abs(yc):g})²"

    ordinaria = f"{term_x} + {term_y} = {r_sq:g}"

    base_x = "X" if xc == 0 else f"({xc:g} - X)"
    if yc == 0:
        explicita = f"Y = ± √({r_sq:g} - {base_x}²)"
    else:
        explicita = f"Y = {yc:g} ± √({r_sq:g} - {base_x}²)"

    D = -2 * xc
    E = -2 * yc
    F = xc ** 2 + yc ** 2 - r_sq

    partes_gen = ["X² + Y²"]
    if D != 0:
        signo_d = "+ " if D > 0 else "- "
        val_d = abs(D)
        partes_gen.append(f"{signo_d}{val_d:g}X" if val_d != 1 else f"{signo_d}X")
    if E != 0:
        signo_e = "+ " if E > 0 else "- "
        val_e = abs(E)
        partes_gen.append(f"{signo_e}{val_e:g}Y" if val_e != 1 else f"{signo_e}Y")
    if F != 0:
        signo_f = "+ " if F > 0 else "- "
        partes_gen.append(f"{signo_f}{abs(F):g}")

    partes_gen.append("= 0")
    general = " ".join(partes_gen)

    return ordinaria, explicita, general


def analizar_circulo(xc, yc, r, metodo=METODO_DDA):
    """
    Todos los datos del círculo que muestra la página: pasos de Bresenham,
    contorno, relleno según el método elegido, ecuaciones y métricas.
    Se asume r > 0.
    """
    # 1. Algoritmo de punto medio de Bresenham
    pasos, pixeles_contorno, puntos_ordenados, octantes_dict = algoritmo_punto_medio_circunferencia(xc, yc, r)

    # 2. Relleno según el método seleccionado, desde el centro en su píxel
    #    (el mismo que usa el contorno)
    pxc, pyc = redondear_pixel(xc), redondear_pixel(yc)
    lineas_info = []
    if "DDA Radial" in metodo:
        segmentos_relleno, pixeles_relleno, lineas_info = generar_relleno_dda_radial(pxc, pyc, puntos_ordenados)
    elif "Cuerdas" in metodo:
        segmentos_relleno, pixeles_relleno = generar_relleno_cuerdas_scanlines(pxc, pyc, r, pixeles_contorno)
    else:  # Concéntrico
        segmentos_relleno, pixeles_relleno = generar_relleno_concentrico(pxc, pyc, r)

    # Huecos: píxeles dentro del contorno (fila por fila) que el método no encendió
    _, interior = generar_relleno_cuerdas_scanlines(pxc, pyc, r, pixeles_contorno)
    pixeles_huecos = interior - pixeles_relleno

    # 3. Métricas analíticas
    ordinaria, explicita, general = get_ecuaciones_circunferencia(xc, yc, r)

    return {
        "xc": xc,
        "yc": yc,
        "r": r,
        "p0": 1 - r,
        "metodo_relleno": metodo,
        "pasos": pasos,
        "pixeles_contorno": pixeles_contorno,
        "puntos_ordenados": puntos_ordenados,
        "octantes_dict": octantes_dict,
        "segmentos_relleno": segmentos_relleno,
        "pixeles_relleno": pixeles_relleno,
        "pixeles_huecos": pixeles_huecos,
        "lineas_info": lineas_info,
        "ordinaria": ordinaria,
        "explicita": explicita,
        "general": general,
        "perimetro": 2.0 * math.pi * r,
        "area": math.pi * (r ** 2),
        "diametro": 2.0 * r,
    }
