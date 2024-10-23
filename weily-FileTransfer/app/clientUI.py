import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from .client import *


class ProgressbarToplevel(tk.Toplevel):
    def __init__(
        self,
        master: Union[tk.Misc, None] = None,
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

    @ignoreExceptions(tk.TclError, True)
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

    @ignoreExceptions(tk.TclError, True)
    def letTop(self):
        self.attributes("-topmost", True)
        self.update()
        self.attributes("-topmost", False)
        self.update()


class UI(tk.Tk):
    toplever_table: Set[ProgressbarToplevel]

    def __init__(
        self,
        title: str = "File Transfer",
        width: int = 640,
        height: int = 480,
        *,
        host: str = "localhost",
        post: int = 8080,
        client_timeout: Union[float, None] = None,
        bufsize: Union[int, None] = None,
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
        self.post = tk.StringVar(self, str(post))
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
        self.initListboxWithBar().place(
            relx=0.0, rely=0.0, relwidth=1.0, relheight=0.75
        )
        self.initButtons().place(relx=0.04, rely=0.8, relwidth=0.32, relheight=0.15)
        self.initLinkCon().place(relx=0.38, rely=0.8, relwidth=0.5, relheight=0.15)
        self.mainloop()

    def initListboxWithBar(self):
        BARWID = 0.02
        BOXWID = 1 - BARWID
        root = ttk.Frame(self)
        ytableScrollbar = ttk.Scrollbar(root, cursor="hand2")
        self.table = tk.Listbox(
            root, yscrollcommand=ytableScrollbar, listvariable=self.data # type: ignore
        )
        ytableScrollbar.config(command=self.table.yview)
        self.table.place(relx=0.0, rely=0.0, relwidth=BOXWID, relheight=1.0)
        ytableScrollbar.place(relx=BOXWID, rely=0.0, relwidth=BARWID, relheight=1.0)
        return root

    def initButtons(self):
        DX, DY = 0.02, 0.05
        BWID, BHEI = 0.5 - DX, 0.5 - DY
        BX, BY = 1 - BWID - DX, 1 - BHEI - DY
        root = ttk.Frame(self, relief="groove")
        ttk.Button(root, text="Update", cursor="hand2", command=self.updateList).place(
            relx=DX, rely=DY, relwidth=BWID, relheight=BHEI
        )
        ttk.Button(root, text="Upload", cursor="hand2", command=self.pushFiles).place(
            relx=BX, rely=DY, relwidth=BWID, relheight=BHEI
        )
        ttk.Button(root, text="Delete", cursor="hand2", command=self.eraseFile).place(
            relx=DX, rely=BY, relwidth=BWID, relheight=BHEI
        )
        ttk.Button(root, text="Download", cursor="hand2", command=self.download).place(
            relx=BX, rely=BY, relwidth=BWID, relheight=BHEI
        )
        return root

    def initLinkCon(self):
        root = ttk.Frame(self, relief="groove")
        ttk.Label(root, text="Host:", anchor="e").place(
            relx=0.17, rely=0.1, relwidth=0.108, relheight=0.33, anchor="ne"
        )
        ttk.Label(root, text="Post:", anchor="e").place(
            relx=0.61, rely=0.1, relwidth=0.108, relheight=0.33, anchor="ne"
        )
        ttk.Label(root, text="Token:", anchor="e").place(
            relx=0.17, rely=0.6, relwidth=0.14, relheight=0.33, anchor="ne"
        )
        ttk.Button(root, text="Link", cursor="hand2", command=self.testCon).place(
            relx=0.8, rely=0.067, relwidth=0.16, relheight=0.37
        )
        ttk.Entry(root, textvariable=self.host).place(
            relx=0.18, rely=0.067, relwidth=0.32, relheight=0.33
        )
        ttk.Entry(root, textvariable=self.post).place(
            relx=0.62, rely=0.067, relwidth=0.16, relheight=0.33
        )
        ttk.Entry(root, textvariable=self.token).place(
            relx=0.18, rely=0.57, relwidth=0.8, relheight=0.33
        )
        return root

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
        except (OSError, AssertionError) as err:
            self.showwarning(str(err))

    def updateList(self):
        try:
            self.update()
            self.data.set(str(self.client_socket.list()))
            self.table.selection_clear(0, self.table.size() - 1)
            self.update_toplever()
        except (OSError, AssertionError) as err:
            self.showwarning(str(err))

    def eraseFile(self):
        try:
            passwd = self.token.get()
            item = self.getSelFile()
            self.showinfo(self.client_socket.erase(item, passwd))
            self.updateList()
        except (OSError, AssertionError) as err:
            self.showwarning(str(err))

    def pushFiles(self):
        try:
            self.client_socket.test()
            passwd = self.token.get()
            for filename in filedialog.askopenfilenames(title=self.title()):
                self.pushFile(filename, passwd)
        except (OSError, AssertionError) as err:
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
        except (OSError, AssertionError) as err:
            self.showwarning(str(err))
        else:
            self.updateList()
        finally:
            pushCallBack(0, 0)

    @withThread
    def download(self):
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
        except (OSError, AssertionError) as err:
            self.showwarning(str(err))
        finally:
            self.close_toplever(toplevel)

    def start_toplever(self, title: Union[str, None] = None):
        tl = ProgressbarToplevel(self, self.title() if title is None else title)
        self.toplever_table.add(tl)
        return tl

    @ignoreExceptions((OSError, AssertionError))
    def close_toplever(self, toplevel: ProgressbarToplevel):
        if toplevel is not None:
            toplevel.destroy()
            self.toplever_table.remove(toplevel)

    def update_toplever(self):
        for tp in self.toplever_table.copy():
            if tp.letTop():
                self.toplever_table.remove(tp)

    def showinfo(self, msg: str):
        messagebox.showinfo(self.title(), msg)

    def showwarning(self, msg: str):
        messagebox.showwarning(self.title(), msg)


if __name__ == "__main__":
    app = UI()
