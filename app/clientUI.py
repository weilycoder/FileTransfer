import tkinter as tk
from tkinter import ttk, messagebox

from .client import *


class UI(tk.Tk):
    def __init__(
        self, title: str = "File Transfer", width: int = 640, height: int = 480
    ):
        super().__init__()
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.client_socket = Client()
        self.initUI()

    def initUI(self):
        self.ytableScrollbar = ttk.Scrollbar(self, cursor="hand2")
        self.table = tk.Listbox(self, yscrollcommand=self.ytableScrollbar)
        self.ytableScrollbar.config(command=self.table.yview)

        self.updateB = ttk.Button(self, text="Update", cursor="hand2")
        self.pushB = ttk.Button(self, text="Push", cursor="hand2")
        self.deleteB = ttk.Button(self, text="Delete", cursor="hand2")
        self.installB = ttk.Button(self, text="Install", cursor="hand2")
        self.testB = ttk.Button(self, text="Test", cursor="hand2")

        self.host = tk.StringVar(self, value="localhost")
        self.post = tk.StringVar(self, value="8080")
        self.token = tk.StringVar(self, value="")

        self.hostE = ttk.Entry(self, textvariable=self.host)
        self.tokenE = ttk.Entry(self, textvariable=self.token)
        self.postE = ttk.Entry(self, textvariable=self.post)

        self.table.place(relx=0.0, rely=0.0, relwidth=0.98, relheight=0.75)
        self.ytableScrollbar.place(relx=0.98, rely=0.0, relwidth=0.02, relheight=0.75)

        self.updateB.place(relx=0.04, rely=0.80, relwidth=0.15, relheight=0.06)
        self.pushB.place(relx=0.21, rely=0.80, relwidth=0.15, relheight=0.06)
        self.deleteB.place(relx=0.04, rely=0.88, relwidth=0.15, relheight=0.06)
        self.installB.place(relx=0.21, rely=0.88, relwidth=0.15, relheight=0.06)
        self.testB.place(relx=0.78, rely=0.8, relwidth=0.08, relheight=0.06)

        ttk.Label(self, text="Host:").place(relx=0.405, rely=0.81)
        self.hostE.place(relx=0.47, rely=0.805, relwidth=0.16, relheight=0.05)
        ttk.Label(self, text="Post:").place(relx=0.635, rely=0.81)
        self.postE.place(relx=0.69, rely=0.805, relwidth=0.08, relheight=0.05)
        ttk.Label(self, text="Token:").place(relx=0.39, rely=0.89)
        self.tokenE.place(relx=0.47, rely=0.885, relwidth=0.4, relheight=0.05)

        self.mainloop()


if __name__ == "__main__":
    app = UI()
