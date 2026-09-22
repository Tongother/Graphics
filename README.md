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

- **Diseño Moderno con CustomTkinter:** Interfaz elegante con bordes y esquinas redondeadas, transiciones suaves y estética contemporánea.
- **Iconos Vectoriales Nativos (`CTkImage`):** Iconos de alta fidelidad renderizados con supersampling 4x integrados en botones y títulos.
- **Sistema de Temas Nativo (Dark / Light):** Interruptor `CTkSwitch` en la barra lateral para alternar instantáneamente entre Modo Oscuro y Modo Claro.
- **Plano Cartesiano Predominante:** Ocupa más del 80% de la ventana con escala adaptativa 1:1, fondo coordinado con el tema y alta definición.
- **Tabla Moderna con CTkTable:** Visualización paso a paso de los puntos discretos con estilo redondeado, cabecera azul y filas alternadas.
- **Datos Analíticos Separados y Claros:** Tarjetas con métricas organizadas en jerarquía: Pendiente ($m$, comportamiento, ángulo), Ecuación ($y = mx + b$, ordenada al origen) e Incrementos ($\Delta X, \Delta Y$, sentido y magnitud).
- **Arquitectura Directa sin Componentes Innecesarios:** El código está organizado limpiamente dentro de `pages/` y `main.py`.

---

## Estructura del Proyecto

```text
.
├── main.py
├── test_app.py
├── requirements.txt
├── README.md
└── pages/
    ├── Futuro.py
    ├── icons.py
    ├── index.py
    └── puntos_colineales.py
```
