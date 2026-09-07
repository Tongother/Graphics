import tkinter as tk
from tkinter import ttk, messagebox

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

results = {}
xMenor = 0

def get_pendiente(x1, y1, x2, y2):
    pendiente = (y2 - y1) / (x2 - x1)
    return pendiente

def get_ordenada(x1, y1, pendiente):
    return y1 - pendiente * x1

def get_ecuacion_recta(x1, y1, pendiente):
    ordenada = get_ordenada(x1, y1, pendiente)
    signo = "+" if ordenada >= 0 else "-"
    return f"y = {pendiente:g}x {signo} {abs(ordenada):g}"

def plot_points(x1, x2, y1, pendiente):
    ordenada = get_ordenada(x1, y1, pendiente)

    arrayMin = []
    arrayMax = []
    x = []
    y = []

    xMenor, xMayor = min(x1, x2), max(x1, x2)

    for i in range(0, 3):
        arrayMin.append(xMenor - (2 - i)) # Esto me sirve para que empiece a graficar desde 3 unidades antes del punto menor
        arrayMax.append(xMayor + i)

    x = arrayMin + arrayMax

    for i in x:
        y.append(pendiente * i + ordenada)

    points = {
        "X": x,
        "Y": y
    }

    return points

def setup_ejes(ax):
    ax.set_title("Grafica de la recta")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.grid(True, linestyle=":", linewidth=0.6)

def draw_recta(ax, canvas, points, x1, y1, x2, y2):
    ax.clear()
    setup_ejes(ax)

    ax.plot(points["X"], points["Y"], marker="o", color="blue")

    ax.annotate("A", (x1, y1), textcoords="offset points", xytext=(0,10), ha='center', fontsize=12, color="green")
    ax.annotate("B", (x2, y2), textcoords="offset points", xytext=(0,10), ha='center', fontsize=12, color="green")

    ax.plot(points["X"], points["Y"], color="red", linewidth=2, label="Recta que pasa por A y B")
    ax.legend()
    canvas.draw()

def get_results(entryXA, entryYA, entryXB, entryYB, labelPendiente, labelEquation, ax, canvas):
    try:
        x1 = int(entryXA.get())
        y1 = int(entryYA.get())
        x2 = int(entryXB.get())
        y2 = int(entryYB.get())
    except ValueError:
        messagebox.showerror("Error", "Todos los campos deben tener un numero entero.")
        return

    if x2 == x1:
        messagebox.showerror("Error", "La pendiente es indefinida (recta vertical).")
        return

    pendiente = get_pendiente(x1, y1, x2, y2)
    equation = get_ecuacion_recta(x1, y1, pendiente)
    points = plot_points(x1, x2, y1, pendiente)

    results.update({
        "pendiente": pendiente,
        "equation": equation,
        "points": points
    })

    labelPendiente.config(text=f"Pendiente: {pendiente:g}")
    labelEquation.config(text=f"Ecuacion: {equation}")

    draw_recta(ax, canvas, points, x1, y1, x2, y2)

def create_puntos_colineales_page(container):
    frame = tk.Frame(container)
    ttk.Label(frame, text="Puntos Colineales", font=("Arial", 24)).pack(pady=20)

    groupEntry = tk.LabelFrame(frame, text="Variables", padx=10, pady=10)
    groupEntry.pack(fill="x", padx=10, pady=10)

    groupPointA = tk.LabelFrame(groupEntry, text="Punto A", padx=10, pady=10)
    groupPointA.pack(fill="x", padx=10, pady=10)

    labelXA = tk.Label(groupPointA, text="X:")
    labelXA.pack(side="left", padx=5, pady=5)

    entryXA = tk.Entry(groupPointA)
    entryXA.pack(side="left", padx=5, pady=5)

    labelYA = tk.Label(groupPointA, text="Y:")
    labelYA.pack(side="left", padx=5, pady=5)

    entryYA = tk.Entry(groupPointA)
    entryYA.pack(side="left", padx=5, pady=5)

    groupPointB = tk.LabelFrame(groupEntry, text="Punto B", padx=10, pady=10)
    groupPointB.pack(fill="x", padx=10, pady=10)

    labelXB = tk.Label(groupPointB, text="X:")
    labelXB.pack(side="left", padx=5, pady=5)

    entryXB = tk.Entry(groupPointB)
    entryXB.pack(side="left", padx=5, pady=5)

    labelYB = tk.Label(groupPointB, text="Y:")
    labelYB.pack(side="left", padx=5, pady=5)

    entryYB = tk.Entry(groupPointB)
    entryYB.pack(side="left", padx=5, pady=5)

    frameResults = tk.LabelFrame(frame, text="Resultados", padx=10, pady=10)
    frameResults.pack(fill="x", padx=10, pady=10)

    labelPendiente = tk.Label(frameResults, text="Pendiente: ")
    labelPendiente.pack(side="left", padx=5, pady=5)

    labelEquation = tk.Label(frameResults, text="Ecuacion: ")
    labelEquation.pack(side="left", padx=5, pady=5)

    figure = Figure(figsize=(5, 4), dpi=100)
    ax = figure.add_subplot(111)
    setup_ejes(ax)

    canvas = FigureCanvasTkAgg(figure, master=frame)
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
    canvas.draw()

    buttonPendiente = tk.Button(
        groupEntry,
        text="Obtener resultados",
        command=lambda: get_results(entryXA, entryYA, entryXB, entryYB, labelPendiente, labelEquation, ax, canvas)
    )
    buttonPendiente.pack(side="left", padx=5, pady=5)

    return frame
