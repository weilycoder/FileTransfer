from base64 import b64decode, b64encode
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from .client import *


class UI(tk.Tk):
    def __init__(
        self,
        title: str = "File Transfer",
        width: int = 640,
        height: int = 480,
        *,
        host: str = "localhost",
        post: int = 8080,
        client_timeout: int = None,
        bufsize: int = None
    ):
        super().__init__()
        self.timeout = client_timeout
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.bufsize = bufsize
        self.client_socket = Client(host, post, client_timeout=self.timeout, bufsize=self.bufsize)
        self.initUI()

    def initUI(self):
        self.data = tk.StringVar(self)

        self.ytableScrollbar = ttk.Scrollbar(self, cursor="hand2")
        self.table = tk.Listbox(
            self, yscrollcommand=self.ytableScrollbar, listvariable=self.data
        )
        self.ytableScrollbar.config(command=self.table.yview)

        self.updateB = ttk.Button(
            self, text="Update", cursor="hand2", command=self.updateList
        )
        self.pushB = ttk.Button(
            self, text="Push", cursor="hand2", command=self.pushFile
        )
        self.deleteB = ttk.Button(
            self, text="Delete", cursor="hand2", command=self.eraseFile
        )
        self.installB = ttk.Button(
            self, text="Install", cursor="hand2", command=self.installFile
        )
        self.testB = ttk.Button(self, text="Test", cursor="hand2", command=self.test)

        self.host = tk.StringVar(self, value=self.client_socket.address[0])
        self.post = tk.StringVar(self, value=self.client_socket.address[1])
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

    def getSelFile(self):
        sel = self.table.curselection()
        assert sel, "No item selected."
        assert len(sel) == 1, "Too many items selected."
        return str(self.table.get((sel[0])))

    def test(self):
        try:
            host = self.host.get()
            post = int(self.post.get())
            self.client_socket = Client(host, post, client_timeout=self.timeout, bufsize=self.bufsize)
            self.client_socket.test()
            messagebox.showinfo(self.title(), "Test Ok.")
            self.updateList()
        except Exception as err:
            messagebox.showwarning(self.title(), str(err))

    def updateList(self):
        try:
            self.update()
            self.data.set(self.client_socket.list())
            self.table.selection_clear(0, self.table.size() - 1)
        except Exception as err:
            messagebox.showwarning(self.title(), str(err))

    def pushFile(self):
        try:
            passwd = self.token.get()
            fn = filedialog.askopenfilename(title=self.title())
            if not fn:
                return
            messagebox.showinfo(
                self.title(),
                self.client_socket.insert(fn, passwd, callback=self.pushCallBack),
            )
        except Exception as err:
            messagebox.showwarning(self.title(), str(err))
        else:
            self.updateList()

    def eraseFile(self):
        try:
            passwd = self.token.get()
            item = self.getSelFile()
            messagebox.showinfo(self.title(), self.client_socket.erase(item, passwd))
            self.updateList()
        except Exception as err:
            messagebox.showwarning(self.title(), str(err))

    def installFile(self):
        try:
            passwd = self.token.get()
            item = self.getSelFile()
            ret = self.client_socket.get(item, passwd)
            if not ret[-1]:
                ret.pop()
                fn = filedialog.asksaveasfilename(title=self.title(), initialfile=item)
                if not fn:
                    return
                with open(fn, "wb") as f:
                    f.write(ret)
                messagebox.showinfo(self.title(), "Install Ok.")
            else:
                print(ret)
                messagebox.showinfo(self.title(), ret.decode())
        except Exception as err:
            messagebox.showwarning(self.title(), str(err))

    def pushCallBack(self, sent: int, size: int):
        print(sent, size)
        self.update()


if __name__ == "__main__":
    app = UI()
