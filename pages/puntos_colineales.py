import math
import tkinter as tk
from tkinter import ttk, messagebox

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

results = {}

def get_pendiente(x1, y1, x2, y2):
    return (y2 - y1) / (x2 - x1)

def get_ordenada(x1, y1, pendiente):
    return y1 - pendiente * x1

def get_ecuacion_recta(x1, y1, pendiente):
    ordenada = get_ordenada(x1, y1, pendiente)
    signo = "+" if ordenada >= 0 else "-"
    return f"y = {pendiente:g}x {signo} {abs(ordenada):g}"

def get_direccion_x(dx):
    if dx > 0:
        return "De izquierda a derecha"
    elif dx < 0:
        return "De derecha a izquierda"
    return "Sin cambio horizontal"

def get_direccion_y(dy):
    if dy > 0:
        return "De abajo hacia arriba"
    elif dy < 0:
        return "De arriba hacia abajo"
    return "Sin cambio vertical (horizontal)"

def get_comportamiento_pendiente(m):
    if m > 0:
        return "Ascendente / Creciente (↗)"
    elif m < 0:
        return "Descendente / Decreciente (↘)"
    return "Horizontal (constante)"

def generar_puntos_trayectoria(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    pasos = int(max(abs(dx), abs(dy)))
    puntos = []

    if pasos == 0:
        return [(0, x1, y1)]

    step_x = dx / pasos
    step_y = dy / pasos

    for i in range(pasos + 1):
        px = x1 + i * step_x
        py = y1 + i * step_y
        # Formatear a entero si es exacto
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

def setup_ejes(ax, limit=10):
    ax.set_title("Grafica de la recta")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.grid(True, linestyle=":", linewidth=0.6)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    ax.set_aspect("equal", adjustable="box")

def plot_points(x1, x2, y1, pendiente, limit):
    ordenada = get_ordenada(x1, y1, pendiente)

    x_line = [-limit, limit]
    y_line = [pendiente * (-limit) + ordenada, pendiente * limit + ordenada]

    return {
        "X": x_line,
        "Y": y_line
    }

def draw_recta(ax, canvas, points, x1, y1, x2, y2, equation, limit, table_points=None):
    ax.clear()
    setup_ejes(ax, limit)

    # Trazar la recta continua
    ax.plot(points["X"], points["Y"], color="red", linewidth=2, label=f"Recta: {equation}")

    # Marcar los puntos generados de la trayectoria
    if table_points and len(table_points) > 2:
        t_x = [pt[1] for pt in table_points]
        t_y = [pt[2] for pt in table_points]
        ax.plot(t_x, t_y, marker="o", markersize=3, color="royalblue", linestyle="None", alpha=0.5, label="Puntos trayectoria")

    # Marcar los puntos A y B
    ax.plot([x1, x2], [y1, y2], marker="o", markersize=8, color="blue", linestyle="None", label="Puntos A y B")

    # Anotaciones con coordenadas
    ax.annotate(
        f"A ({x1:g}, {y1:g})",
        (x1, y1),
        textcoords="offset points",
        xytext=(0, 10),
        ha="center",
        fontsize=10,
        fontweight="bold",
        color="darkgreen"
    )
    ax.annotate(
        f"B ({x2:g}, {y2:g})",
        (x2, y2),
        textcoords="offset points",
        xytext=(0, 10),
        ha="center",
        fontsize=10,
        fontweight="bold",
        color="darkgreen"
    )

    ax.legend(loc="upper left", fontsize=8)
    canvas.draw()

def get_results(entryXA, entryYA, entryXB, entryYB, labelPendiente,
                labelDeltaX, labelDirX, labelDeltaY, labelDirY, tree, ax, canvas):
    try:
        x1 = float(entryXA.get())
        y1 = float(entryYA.get())
        x2 = float(entryXB.get())
        y2 = float(entryYB.get())
        if x1.is_integer(): x1 = int(x1)
        if y1.is_integer(): y1 = int(y1)
        if x2.is_integer(): x2 = int(x2)
        if y2.is_integer(): y2 = int(y2)
    except ValueError:
        messagebox.showerror("Error", "Todos los campos deben tener un número válido.")
        return

    if x2 == x1:
        messagebox.showerror("Error", "La pendiente es indefinida (recta vertical x1 = x2).")
        return

    delta_x = x2 - x1
    delta_y = y2 - y1
    dir_x = get_direccion_x(delta_x)
    dir_y = get_direccion_y(delta_y)

    pendiente = get_pendiente(x1, y1, x2, y2)
    comportamiento = get_comportamiento_pendiente(pendiente)
    angulo = math.degrees(math.atan(pendiente))
    equation = get_ecuacion_recta(x1, y1, pendiente)

    # El numero mas grande ingresado define la escala del plano
    max_val = max(abs(x1), abs(y1), abs(x2), abs(y2))
    if max_val == 0:
        max_val = 10
    margin = max(2, int(max_val * 0.1) + 1)
    limit = max_val + margin

    points = plot_points(x1, x2, y1, pendiente, limit)
    table_points = generar_puntos_trayectoria(x1, y1, x2, y2)

    results.update({
        "pendiente": pendiente,
        "equation": equation,
        "delta_x": delta_x,
        "delta_y": delta_y,
        "dir_x": dir_x,
        "dir_y": dir_y,
        "table_points": table_points,
        "limit": limit
    })

    # Actualizar etiquetas de resultados
    labelPendiente.config(text=f"Pendiente (m): {pendiente:g}  [{comportamiento}]  Ángulo: {angulo:.1f}°")
    labelDeltaX.config(text=f"Incremento X (dX): {delta_x:g}")
    labelDirX.config(text=f"Dirección X: {dir_x}")
    labelDeltaY.config(text=f"Incremento Y (dY): {delta_y:g}")
    labelDirY.config(text=f"Dirección Y: {dir_y}")

    # Llenar la tabla de valores X e Y
    for item in tree.get_children():
        tree.delete(item)

    for paso, px, py in table_points:
        tree.insert("", "end", values=(f"{px:g}", f"{py:g}"))

    # Dibujar la recta y los puntos
    draw_recta(ax, canvas, points, x1, y1, x2, y2, equation, limit, table_points)

def clear_all(entryXA, entryYA, entryXB, entryYB, labelPendiente,
              labelDeltaX, labelDirX, labelDeltaY, labelDirY, tree, ax, canvas):
    entryXA.delete(0, tk.END)
    entryYA.delete(0, tk.END)
    entryXB.delete(0, tk.END)
    entryYB.delete(0, tk.END)

    labelPendiente.config(text="Pendiente (m): ")
    labelDeltaX.config(text="Incremento X (dX): ")
    labelDirX.config(text="Dirección X: ")
    labelDeltaY.config(text="Incremento Y (dY): ")
    labelDirY.config(text="Dirección Y: ")

    for item in tree.get_children():
        tree.delete(item)

    results.clear()

    ax.clear()
    setup_ejes(ax, limit=10)
    canvas.draw()

    entryXA.focus_set()

def create_puntos_colineales_page(container):
    frame = tk.Frame(container)
    ttk.Label(frame, text="Puntos Colineales", font=("Arial", 22, "bold")).pack(pady=(15, 10))

    # Formulario de entradas
    groupEntry = tk.LabelFrame(frame, text="Variables (Coordenadas de los Puntos)", padx=10, pady=8)
    groupEntry.pack(fill="x", padx=10, pady=5)

    groupPointA = tk.LabelFrame(groupEntry, text="Punto A", padx=8, pady=5)
    groupPointA.pack(side="left", padx=5, pady=2)

    tk.Label(groupPointA, text="X:").pack(side="left", padx=3, pady=2)
    entryXA = tk.Entry(groupPointA, width=7)
    entryXA.pack(side="left", padx=3, pady=2)

    tk.Label(groupPointA, text="Y:").pack(side="left", padx=3, pady=2)
    entryYA = tk.Entry(groupPointA, width=7)
    entryYA.pack(side="left", padx=3, pady=2)

    groupPointB = tk.LabelFrame(groupEntry, text="Punto B", padx=8, pady=5)
    groupPointB.pack(side="left", padx=10, pady=2)

    tk.Label(groupPointB, text="X:").pack(side="left", padx=3, pady=2)
    entryXB = tk.Entry(groupPointB, width=7)
    entryXB.pack(side="left", padx=3, pady=2)

    tk.Label(groupPointB, text="Y:").pack(side="left", padx=3, pady=2)
    entryYB = tk.Entry(groupPointB, width=7)
    entryYB.pack(side="left", padx=3, pady=2)

    # Panel de Resultados y Análisis
    frameResults = tk.LabelFrame(frame, text="Análisis de la Recta", padx=10, pady=8)
    frameResults.pack(fill="x", padx=10, pady=5)

    labelPendiente = tk.Label(frameResults, text="Pendiente (m): ", font=("Arial", 9, "bold"), anchor="w")
    labelPendiente.grid(row=0, column=0, sticky="w", padx=8, pady=2)

    labelDeltaX = tk.Label(frameResults, text="Incremento X (dX): ", font=("Arial", 9), anchor="w")
    labelDeltaX.grid(row=0, column=1, sticky="w", padx=15, pady=2)

    labelDirX = tk.Label(frameResults, text="Dirección X: ", font=("Arial", 9), anchor="w")
    labelDirX.grid(row=1, column=1, sticky="w", padx=15, pady=2)

    labelDeltaY = tk.Label(frameResults, text="Incremento Y (dY): ", font=("Arial", 9), anchor="w")
    labelDeltaY.grid(row=0, column=2, sticky="w", padx=15, pady=2)

    labelDirY = tk.Label(frameResults, text="Dirección Y: ", font=("Arial", 9), anchor="w")
    labelDirY.grid(row=1, column=2, sticky="w", padx=15, pady=2)

    # Contenedor inferior: Tabla a la izquierda, Gráfica a la derecha
    mainContent = tk.Frame(frame)
    mainContent.pack(fill="both", expand=True, padx=10, pady=5)
    mainContent.columnconfigure(0, weight=1)
    mainContent.columnconfigure(1, weight=2)
    mainContent.rowconfigure(0, weight=1)

    # Tabla de puntos
    tableFrame = tk.LabelFrame(mainContent, text="Puntos de la Recta (Paso a Paso)", padx=5, pady=5)
    tableFrame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

    tree = ttk.Treeview(tableFrame, columns=("x", "y"), show="headings", height=10)
    tree.heading("x", text="X")
    tree.heading("y", text="Y")

    tree.column("x", width=90, anchor="center")
    tree.column("y", width=90, anchor="center")

    scrollbar = ttk.Scrollbar(tableFrame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Gráfica
    graphFrame = tk.LabelFrame(mainContent, text="Plano Cartesiano", padx=5, pady=5)
    graphFrame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

    figure = Figure(figsize=(5, 4), dpi=100)
    ax = figure.add_subplot(111)
    setup_ejes(ax, limit=10)

    canvas = FigureCanvasTkAgg(figure, master=graphFrame)
    canvas.get_tk_widget().pack(fill="both", expand=True)
    canvas.draw()

    # Botones en groupEntry
    buttonPendiente = tk.Button(
        groupEntry,
        text="Obtener resultados",
        bg="#2563eb",
        fg="white",
        font=("Arial", 9, "bold"),
        padx=8,
        pady=3,
        command=lambda: get_results(entryXA, entryYA, entryXB, entryYB,
                                    labelPendiente,
                                    labelDeltaX, labelDirX,
                                    labelDeltaY, labelDirY,
                                    tree, ax, canvas)
    )
    buttonPendiente.pack(side="left", padx=8, pady=5)

    buttonLimpiar = tk.Button(
        groupEntry,
        text="Limpiar",
        padx=8,
        pady=3,
        command=lambda: clear_all(entryXA, entryYA, entryXB, entryYB,
                                  labelPendiente,
                                  labelDeltaX, labelDirX,
                                  labelDeltaY, labelDirY,
                                  tree, ax, canvas)
    )
    buttonLimpiar.pack(side="left", padx=5, pady=5)

    return frame
