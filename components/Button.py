from tkinter import ttk


def create_button(container, texto, function):
    boton = ttk.Button(
        container,
        text=texto,
        padding=10,
        command=lambda: function()
    )
    boton.pack(fill="x")
    return boton