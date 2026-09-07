import tkinter as tk
from tkinter import ttk

def future_page(container):
    frame = tk.Frame(container)
    ttk.Label(frame, text="Futura pestaña", font=("Arial", 24)).pack(pady=20)
    return frame