import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from .client import *


class ProgressbarToplevel(tk.Toplevel):
    def __init__(
        self,
        master: tk.Misc = None,
        title: str = "",
        width=360,
        height=50,
    ):
        super().__init__(master)
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.attributes("-toolwindow", True)
        self.resizable(False, False)
        self.initUI()

    def initUI(self):
        self.progress_bar = ttk.Progressbar(
            self, orient="horizontal", mode="determinate"
        )
        self.progress_bar.place(relx=0.05, rely=0.25, relwidth=0.9, relheight=0.5)
        self.letTop()

    @ignoreExceptions(Exception, True)
    def run(self, value: int, maximum: int):
        assert self.winfo_exists()
        self.progress_bar.config(mode="determinate")
        self.progress_bar["value"] = value
        self.progress_bar["maximum"] = maximum
        self.update()

    def start(self):
        self.progress_bar.config(mode="indeterminate")
        self.progress_bar.start()
        self.update()

    def letTop(self):
        self.attributes("-topmost", True)
        self.update()
        self.attributes("-topmost", False)
        self.update()


class UI(tk.Tk):
    toplever_table: typing.Set[ProgressbarToplevel]

    def __init__(
        self,
        title: str = "File Transfer",
        width: int = 640,
        height: int = 480,
        *,
        host: str = "localhost",
        post: int = 8080,
        client_timeout: int = None,
        bufsize: int = None,
    ):
        super().__init__()
        self.timeout = client_timeout
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.bufsize = bufsize
        self.toplever_table = set()
        self.data = tk.StringVar(self)
        self.token = tk.StringVar(self)
        self.host = tk.StringVar(self, host)
        self.post = tk.StringVar(self, post)
        self.client_socket = self.newClient()
        self.initUI()

    def newClient(self):
        return Client(
            self.host.get(),
            int(self.post.get()),
            client_timeout=self.timeout,
            bufsize=self.bufsize,
        )

    def initUI(self):
        self.ytableScrollbar = ttk.Scrollbar(self, cursor="hand2")
        self.table = tk.Listbox(
            self, yscrollcommand=self.ytableScrollbar, listvariable=self.data
        )
        self.ytableScrollbar.config(command=self.table.yview)

        self.updateB = ttk.Button(
            self, text="Update", cursor="hand2", command=self.updateList
        )
        self.pushB = ttk.Button(
            self, text="Upload", cursor="hand2", command=self.pushFiles
        )
        self.deleteB = ttk.Button(
            self, text="Delete", cursor="hand2", command=self.eraseFile
        )
        self.installB = ttk.Button(
            self, text="Download", cursor="hand2", command=self.installFile
        )
        self.testB = ttk.Button(self, text="Link", cursor="hand2", command=self.testCon)

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

        ttk.Label(self, text="Host:", anchor="e").place(
            relx=0.465, rely=0.81, relwidth=0.054, relheight=0.05, anchor="ne"
        )
        self.hostE.place(relx=0.47, rely=0.805, relwidth=0.16, relheight=0.05)
        ttk.Label(self, text="Post:", anchor="e").place(
            relx=0.685, rely=0.81, relwidth=0.054, relheight=0.05, anchor="ne"
        )
        self.postE.place(relx=0.69, rely=0.805, relwidth=0.08, relheight=0.05)
        ttk.Label(self, text="Token:", anchor="e").place(
            relx=0.465, rely=0.89, relwidth=0.075, relheight=0.05, anchor="ne"
        )
        self.tokenE.place(relx=0.47, rely=0.885, relwidth=0.4, relheight=0.05)

        self.mainloop()

    def getSelFile(self):
        sel = self.table.curselection()
        assert sel, "No item selected."
        assert len(sel) == 1, "Too many items selected."
        return str(self.table.get((sel[0])))

    @withThread
    def testCon(self):
        try:
            self.client_socket = self.newClient()
            self.client_socket.test()
            self.showinfo("Link Ok.")
            self.updateList()
        except Exception as err:
            self.showwarning(str(err))

    def updateList(self):
        try:
            self.update()
            self.data.set(self.client_socket.list())
            self.table.selection_clear(0, self.table.size() - 1)
            self.update_toplever()
        except Exception as err:
            self.showwarning(str(err))

    def eraseFile(self):
        try:
            passwd = self.token.get()
            item = self.getSelFile()
            self.showinfo(self.client_socket.erase(item, passwd))
            self.updateList()
        except Exception as err:
            self.showwarning(str(err))

    def pushFiles(self):
        try:
            self.client_socket.test()
            passwd = self.token.get()
            for filename in filedialog.askopenfilenames(title=self.title()):
                self.pushFile(filename, passwd)
        except Exception as err:
            self.showwarning(str(err))

    @withThread
    def pushFile(self, fn: str, passwd: str):
        @ignoreExceptions(Exception, True)
        def pushCallBack(sent: int, size: int):
            if not size or not pro.winfo_exists():
                self.close_toplever(pro)
                return True
            pro.run(sent, size)
            self.update()
            return False

        try:
            pro = self.start_toplever(f"Uploading - {getFilename(fn)}")
            self.showinfo(self.client_socket.insert(fn, passwd, callback=pushCallBack))
        except Exception as err:
            self.showwarning(str(err))
        else:
            self.updateList()
        finally:
            pushCallBack(0, 0)

    @withThread
    def installFile(self):
        toplevel = None
        try:
            passwd = self.token.get()
            item = self.getSelFile()
            toplevel = self.start_toplever(f"Download - {item}")
            toplevel.start()
            ret = self.client_socket.get(item, passwd)
            if not toplevel.winfo_exists():
                self.showinfo("Abort.")
            elif not ret[-1]:
                ret.pop()
                fn = filedialog.asksaveasfilename(title=self.title(), initialfile=item)
                if not fn:
                    return
                with open(fn, "wb") as f:
                    f.write(ret)
                self.showinfo("Install Ok.")
            else:
                self.showinfo(ret.decode())
        except Exception as err:
            self.showwarning(str(err))
        finally:
            self.close_toplever(toplevel)

    def start_toplever(self, title: str = None):
        tl = ProgressbarToplevel(self, self.title() if title is None else title)
        self.toplever_table.add(tl)
        return tl

    @ignoreExceptions(Exception)
    def close_toplever(self, toplevel: ProgressbarToplevel):
        if toplevel is not None:
            toplevel.destroy()
            self.toplever_table.remove(toplevel)

    def update_toplever(self):
        for tp in self.toplever_table.copy():
            if tp.winfo_exists():
                tp.letTop()
            else:
                self.toplever_table.remove(tp)

    def showinfo(self, msg: str):
        messagebox.showinfo(self.title(), msg)

    def showwarning(self, msg: str):
        messagebox.showwarning(self.title(), msg)


if __name__ == "__main__":
    app = UI()
