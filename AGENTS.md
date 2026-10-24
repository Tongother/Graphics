# Graficación — Laboratorio de Algoritmos

App de escritorio (Python 3.12, CustomTkinter + Matplotlib) para un curso de Computación
Gráfica: recta DDA, triángulo (DDA + relleno) y circunferencia (punto medio de Bresenham).
Todo el código, nombres y comentarios están en **español**.

> Este archivo es la guía para todos los agentes de IA del equipo (Antigravity, Claude Code, …).
> `CLAUDE.md` solo lo importa: edita las reglas **aquí**.

## Comandos (Windows, desde la raíz; en Linux/macOS usar `.venv/bin/python`)

```bash
.venv/Scripts/python.exe main.py                                            # ejecutar la app
.venv/Scripts/python.exe -m unittest discover -s tests -p "test_core_*.py"  # lógica: <1 s, correr siempre
.venv/Scripts/python.exe -m unittest discover -s tests                      # todo: ~25 s (abre ventanas Tk)
```

Las líneas `invalid command name ..._windows_set_titlebar_icon` / `bgerror` en las pruebas
de interfaz son ruido de CustomTkinter al destruir ventanas, no fallos. Mira solo el `OK`/`FAILED` final.

## Dónde está cada cosa

| Quiero cambiar…                                  | Archivo                                   |
|--------------------------------------------------|-------------------------------------------|
| Un algoritmo, fórmula, texto de caso o ecuación  | `core/recta.py`, `core/triangulo.py`, `core/circulo.py` |
| Qué se muestra en una página / su layout         | `pages/<modulo>.py`                       |
| Dibujo en el plano de una página                 | `render_*_plot()` en `pages/<modulo>.py`  |
| Ejes, zoom, arrastre, leyenda, etiquetas         | `ui/plano.py`                             |
| Estilo de tarjetas, botones, tablas, entradas    | `ui/widgets.py`                           |
| Cambio de tema claro/oscuro                      | `ui/tema.py`                              |
| Menú lateral / agregar o quitar una página       | `PAGINAS` en `pages/index.py` (main.py lo lee) |
| Iconos                                           | `public/<nombre>.svg` (Tabler Icons) + `get_icon("<nombre>")` |

## Arquitectura (reglas)

- `core/` es lógica pura: **no importa** `customtkinter`, `tkinter` ni `matplotlib`. Cada módulo
  expone `analizar_<figura>(...) -> dict` con todo lo que la página muestra.
- `pages/` solo interfaz: lee entradas (`leer_numeros`), valida con `messagebox`, llama a
  `analizar_*()`, guarda el dict en su estado de módulo (`current_data`, `current_triangle_data`,
  `current_circle_data`, con `has_data=True`) y actualiza widgets + plano.
- `ui/` es compartido por todas las páginas; las páginas no se importan entre sí.
- Flujo: `main.py` → `pages/index.py` (`PAGINAS`) → `pages/*.py` → `core/*.py` y `ui/*.py`.

## Convenciones

- Píxeles: usar `redondear_pixel()` (mitades hacia arriba), **nunca** `round()`.
- Colores: tuplas `(claro, oscuro)` en widgets; en Matplotlib `"#oscuro" if is_dark else "#claro"`.
- Cada plano registra su redibujado con `register_plot_updater()` y conserva el zoom con `view=`.
- Los textos de casos DDA y notación están fijados por las pruebas (`tests/casos.py`); si cambian,
  actualizar las pruebas en el mismo cambio.
- Valores por defecto de las entradas (recta 1,2→5,8; triángulo (1,1),(7,2),(3,7); círculo
  C(150,100) R=10) los usan las pruebas de interfaz.
- Pruebas: lógica nueva → `tests/test_core_<modulo>.py`; dibujo → `tests/test_graficas.py`
  (backend Agg); botones/ventanas → `tests/test_interfaz.py`.

## Ahorro de contexto

- No leer `.venv/` ni `docs/` (PDF, xlsx y drawio del curso: binarios grandes) salvo que se pida.
- Para cambiar un algoritmo basta con `core/<modulo>.py` y su prueba; no hace falta abrir la página.
- Para agregar un módulo nuevo (elipse, transformaciones, …) seguir los pasos de
  `.claude/skills/nuevo-modulo/SKILL.md` (en Claude Code se carga solo como skill).
