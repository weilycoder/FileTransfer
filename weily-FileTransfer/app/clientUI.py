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

    @ignoreExceptions((tk.TclError, AssertionError), True)
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
    button_list: List[ttk.Button]
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
        self.button_list = []
        self.toplever_table = set()
        self.data = tk.StringVar(self)
        self.token = tk.StringVar(self)
        self.host = tk.StringVar(self, host)
        self.post = tk.StringVar(self, str(post))
        self.ignoreInfo = tk.IntVar(self, 0)
        self.ignoreWarn = tk.IntVar(self, 0)
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
        self.initButtons().place(relx=0.02, rely=0.8, relwidth=0.28, relheight=0.15)
        self.initLinkCon().place(relx=0.32, rely=0.8, relwidth=0.48, relheight=0.15)
        self.initCheckBut().place(relx=0.82, rely=0.8, relwidth=0.16, relheight=0.15)

    def initListboxWithBar(self):
        BARWID = 0.02
        BOXWID = 1 - BARWID
        root = ttk.Frame(self)
        ytableScrollbar = ttk.Scrollbar(root)
        self.table = tk.Listbox(
            root, yscrollcommand=ytableScrollbar.set, listvariable=self.data  # type: ignore
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
        self.updateBtn = self.new_button(root, "Update", self.updateList)
        self.uploadBtn = self.new_button(root, "Upload", self.pushFiles)
        self.delBtn = self.new_button(root, "Delete", self.eraseFile)
        self.downloadBtn = self.new_button(root, "Download", self.download)
        self.updateBtn.place(relx=DX, rely=DY, relwidth=BWID, relheight=BHEI)
        self.uploadBtn.place(relx=BX, rely=DY, relwidth=BWID, relheight=BHEI)
        self.delBtn.place(relx=DX, rely=BY, relwidth=BWID, relheight=BHEI)
        self.downloadBtn.place(relx=BX, rely=BY, relwidth=BWID, relheight=BHEI)
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
        self.new_button(root, "Link", self.testCon).place(
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

    def initCheckBut(self):
        root = ttk.Frame(self, relief="groove")
        ttk.Checkbutton(root, text="ignore info", variable=self.ignoreInfo).place(
            relx=0.05, rely=0.2, relwidth=0.9, relheight=0.3
        )
        ttk.Checkbutton(root, text="ignore warn", variable=self.ignoreWarn).place(
            relx=0.05, rely=0.5, relwidth=0.9, relheight=0.3
        )
        return root

    def getSelFile(self):
        sel = self.table.curselection()
        assert sel, "No item selected."
        assert len(sel) == 1, "Too many items selected."
        return str(self.table.get((sel[0])))

    @withThread
    @logException(stdloggers.err_logger)
    def testCon(self):
        try:
            self.block_button(UI_BLOCK)
            self.client_socket = self.newClient()
            self.client_socket.test()
            self.updateList(False).join()
            self.showinfo("Link Ok.")
        except (OSError, AssertionError) as err:
            self.showwarning(str(err))

    @withThread
    @logException(stdloggers.err_logger)
    def updateList(self, is_button: bool = True):
        try:
            if is_button:
                self.block_button(UI_BLOCK)
            self.data.set(self.client_socket.list())  # type: ignore
            self.table.selection_clear(0, self.table.size() - 1)
            self.update_toplever()
        except (OSError, AssertionError) as err:
            self.showwarning(str(err))

    @withThread
    @logException(stdloggers.err_logger)
    def eraseFile(self):
        try:
            self.block_button(UI_BLOCK)
            passwd = self.token.get()
            item = self.getSelFile()
            self.updateList(False).join()
            self.showinfo_fromServer(self.client_socket.erase(item, passwd))
        except (OSError, AssertionError) as err:
            self.showwarning(str(err))

    @logException(stdloggers.err_logger)
    def pushFiles(self):
        try:
            self.block_button(UI_BLOCK)
            self.client_socket.test()
            passwd = self.token.get()
            for filename in filedialog.askopenfilenames(title=self.title()):
                self.pushFile(filename, passwd)
        except (OSError, AssertionError) as err:
            self.showwarning(str(err))

    @withThread
    @logException(stdloggers.err_logger)
    def pushFile(self, fn: str, passwd: str):
        @ignoreExceptions(tk.TclError, True)
        def pushCallBack(sent: int, size: int):
            if not size or not pro.winfo_exists():
                self.close_toplever(pro)
                return True
            pro.run(sent, size)
            self.update()
            return False

        try:
            pro = self.start_toplever(f"Uploading - {getFilename(fn)}")
            self.showinfo_fromServer(
                self.client_socket.insert(fn, passwd, callback=pushCallBack)
            )
        except (OSError, AssertionError) as err:
            self.showwarning(str(err))
        else:
            self.updateList(False).join()
        finally:
            pushCallBack(0, 0)

    @withThread
    def download(self):
        toplevel = None
        try:
            self.block_button(UI_BLOCK)
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
                self.showinfo_fromServer(ret.decode())
        except (OSError, AssertionError) as err:
            self.showwarning(str(err))
        finally:
            self.close_toplever(toplevel)

    def start_toplever(self, title: Union[str, None] = None):
        tl = ProgressbarToplevel(self, self.title() if title is None else title)
        self.toplever_table.add(tl)
        return tl

    @ignoreExceptions((OSError, AssertionError, AttributeError, KeyError))
    def close_toplever(self, toplevel: ProgressbarToplevel):
        toplevel.destroy()
        self.toplever_table.remove(toplevel)

    @ignoreExceptions((AttributeError, KeyError))
    def update_toplever(self):
        for tp in self.toplever_table.copy():
            if tp.letTop():
                self.toplever_table.remove(tp)

    def new_button(self, master: tk.Misc, text: str, command: Callable[[], Any]):
        btn = ttk.Button(master, cursor="hand2", text=text, command=command)
        self.button_list.append(btn)
        return btn

    def enable_button(self):
        for btn in self.button_list:
            btn.config(state="normal")
        self.update()

    def disable_button(self):
        for btn in self.button_list:
            btn.config(state="disabled")
        self.update()

    def block_button(self, ms: int):
        self.disable_button()
        self.after(ms, func=self.enable_button)

    def showinfo_fromServer(self, msg: str):
        self.showinfo(msg) if msg.encode() == OK else self.showwarning(msg)

    def showinfo(self, msg: str):
        if not self.ignoreInfo.get():
            messagebox.showinfo(self.title(), msg)
        else:
            stdloggers.log_logger(msg, before=INFO)

    def showwarning(self, msg: str):
        if not self.ignoreWarn.get():
            messagebox.showwarning(self.title(), msg)
        else:
            stdloggers.log_logger(msg, before=WARN)


if __name__ == "__main__":
    app = UI()
