import tkinter as tk

from components.Button import create_button
from pages.index import init_pages, show_page

root = tk.Tk()
root.title("Sample Window")
root.geometry("1200x800")

root.columnconfigure(1, weight=1)
root.rowconfigure(0, weight=1)

sidebar = tk.Frame(root, width=250, bg="#f0f0f0")
sidebar.grid(row=0, column=0, sticky="ns")

container = tk.Frame(root, bg="#ffffff")
container.grid(row=0, column=1, sticky="nsew")
container.rowconfigure(0, weight=1)
container.columnconfigure(0, weight=1)

COLOR_NORMAL = "#9a9a9a"
COLOR_HOVER = "#3d5afe"

init_pages(container)

create_button(sidebar, "Puntos colineales", lambda: show_page("puntos_colineales"))
create_button(sidebar, "Futuro programa", lambda: show_page("futuro"))

# plt.plot(x, y)
# plt.title("Sample Plot")
# plt.xlabel("X-axis")
# plt.ylabel("Y-axis")
# plt.show()

root.mainloop()