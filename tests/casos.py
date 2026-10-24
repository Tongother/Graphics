"""Datos compartidos entre las pruebas de lógica y las de interfaz."""

# (A, B, caso, notación): 4 positivos, 4 negativos y 3 especiales del documento
CASOS_RECTA = [
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
