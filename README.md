# Proyecto de Computación Gráfica

Aplicación de escritorio moderna desarrollada en Python con **CustomTkinter** y **Matplotlib**. Permite calcular, analizar y graficar la trayectoria y ecuación de la recta que pasa por dos puntos, con un diseño profesional, soporte nativo para **Modo Oscuro** y **Modo Claro** en tiempo real, esquinas redondeadas y plano cartesiano expandido.

## Requisitos

- Python 3.10 o superior
- Tkinter (en Linux: `sudo pacman -S tk` o `sudo apt install python3-tk`)
- CustomTkinter (`pip install customtkinter`)
- CTkTable (`pip install CTkTable`)
- Matplotlib

---

## Activación del Entorno Virtual y Ejecución

### En Linux / Arch Linux / macOS

1. Abrir una terminal en la carpeta del proyecto (`Graphics`).
2. Activar el entorno virtual:

```bash
source .venv/bin/activate
```

3. Ejecutar la aplicación:

```bash
python main.py
```

4. Para salir del entorno virtual al finalizar:

```bash
deactivate
```

---

### En Windows (PowerShell)

1. Abrir PowerShell en la raíz del proyecto.
2. Activar el entorno virtual:

```powershell
.\.venv\Scripts\Activate.ps1
```

3. Ejecutar la aplicación:

```powershell
python main.py
```

---

## Características Principales

- **Módulo de Puntos Colineales:** Cálculo analítico de pendientes, vector director, ecuación explícita y rasterización discreta de rectas.
- **Módulo de Trazado de Triángulo:** Entrada de 3 coordenadas ($A, B, C$), cálculo de área mediante fórmula de Gauss/Shoelace, perímetro, longitudes euclidianas, pendientes de cada lado, clasificación (por lados: Equilátero/Isósceles/Escaleno; por ángulos: Acutángulo/Rectángulo/Obtusángulo; detección de colineales), relleno de polígono translúcido y tabla discreta segmento por segmento con `CTkTable`.
- **Módulo de Circunferencia y Círculo Relleno:** Implementación completa del **Algoritmo de Punto Medio de Bresenham** con simetría de 8 octantes, **traslación bidimensional del centro** $(X_c, Y_c)$, algoritmo de **círculo relleno por líneas de barrido (scanlines)**, controles de traslación rápida en tiempo real, ecuaciones ordinaria y general, métricas geométricas (área, perímetro, diámetro) y tabla detallada de iteraciones con los 8 puntos trasladados por cada paso.
- **Diseño Moderno con CustomTkinter:** Interfaz elegante con bordes y esquinas redondeadas, transiciones suaves y estética contemporánea.
- **Iconos SVG (`CTkImage`):** Iconos de [Tabler Icons](https://tabler.io/icons) guardados en `public/`, rasterizados con `resvg-py` a 4x y recoloreados según el tema, integrados en botones y títulos.
- **Sistema de Temas Nativo (Dark / Light):** Interruptor `CTkSwitch` en la barra lateral para alternar instantáneamente entre Modo Oscuro y Modo Claro.
- **Plano Cartesiano Predominante:** Ocupa más del 80% de la ventana con escala adaptativa 1:1, fondo coordinado con el tema y alta definición.
- **Zoom y Desplazamiento:** La rueda del mouse acerca o aleja (centrado en el cursor) y arrastrar con clic izquierdo mueve el plano, sin cambiar el tamaño de la gráfica. El botón "Centrar vista" regresa a la vista original.
- **Tabla Moderna con CTkTable:** Visualización paso a paso de los puntos discretos con estilo redondeado, cabecera azul y filas alternadas.
- **Casos de Trazo del Documento:** Clasifica la recta en 4 casos positivos, 4 negativos y 3 especiales (45° en sus 4 direcciones, horizontal y vertical), contando cada sentido de dibujo como un caso distinto, y muestra su notación (p. ej. `+m<1, m = 2/5 · Xₖ₊₁ = Xₖ + 1 · Yₖ₊₁ = Yₖ + m`).
- **Decimales y Píxeles:** La tabla muestra los valores con dos decimales y el píxel redondeado al entero más cercano.
- **Datos Analíticos Separados y Claros:** Tarjetas con métricas organizadas en jerarquía estructurada en 4 columnas.
- **Arquitectura en Capas:** La lógica de los algoritmos (`core/`) está separada de la interfaz (`pages/`) y de las piezas visuales compartidas (`ui/`), así cada parte se modifica y prueba por separado.

---

## Pruebas

```bash
python -m unittest discover -s tests -p "test_core_*.py"   # lógica de los algoritmos (< 1 s)
python -m unittest discover -s tests                       # todas, incluye ventanas (~25 s)
```

---

## Estructura del Proyecto

```text
.
├── main.py              # Ventana, menú lateral (desde pages/index.py) y switch de tema
├── AGENTS.md            # Guía del proyecto para agentes de IA (Antigravity, Claude Code, …)
├── CLAUDE.md            # Solo importa AGENTS.md para Claude Code
├── requirements.txt
├── core/                # Lógica pura de los algoritmos (sin interfaz)
│   ├── recta.py         #   DDA, pendiente, 11 casos de trazo
│   ├── triangulo.py     #   métricas, clasificación, lados y relleno DDA
│   └── circulo.py       #   punto medio de Bresenham, octantes, rellenos, ecuaciones
├── ui/                  # Piezas de interfaz compartidas
│   ├── plano.py         #   plano cartesiano, zoom y arrastre
│   ├── widgets.py       #   tarjetas, entradas, botones, tablas
│   ├── tema.py          #   modo oscuro / claro
│   └── icons.py         #   iconos SVG -> CTkImage
├── pages/               # Una página por módulo (solo interfaz)
│   ├── index.py         #   registro PAGINAS y navegación
│   ├── puntos_colineales.py
│   ├── triangulo.py
│   └── circulo.py
├── tests/               # test_core_* (rápidas), test_graficas, test_interfaz
├── public/              # Iconos SVG (se cargan por nombre de archivo)
├── docs/                # PDF de la guía, diagramas de flujo, Gantt y tablas de casos
└── .claude/skills/      # Instrucciones para agregar módulos nuevos con IA
```
