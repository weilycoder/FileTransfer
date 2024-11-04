import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from .client import *


class ProgressbarToplevel(tk.Toplevel):
    def __init__(
        self,
        master: Optional[tk.Misc] = None,
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
    data: List[Tuple[str, int]]
    button_list: List[ttk.Button]
    toplever_table: Set[ProgressbarToplevel]
    sort_methed: Union[None, Tuple[int, bool]]

    def __init__(
        self,
        title: str = "File Transfer",
        width: int = 640,
        height: int = 480,
        *,
        host: str = "localhost",
        post: int = 8080,
        client_timeout: Optional[float] = None,
        bufsize: Optional[int] = None,
    ):
        super().__init__()
        self.timeout = client_timeout
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.bufsize = bufsize
        self.data = []
        self.button_list = []
        self.sort_methed = None
        self.toplever_table = set()
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
        self.initBindKey()

    def initListboxWithBar(self):
        BARWID = 0.02
        BOXWID = 1 - BARWID
        root = ttk.Frame(self)
        ytableScrollbar = ttk.Scrollbar(root)
        self.tree_lock = threading.Lock()
        self.tree = ttk.Treeview(root, yscrollcommand=ytableScrollbar.set)
        self.tree["columns"] = ("#1", "#2")
        self.tree.column("#0", width=0, stretch=tk.NO)
        self.tree.heading(
            "#1", text="File", anchor=tk.W, command=lambda: self.sel_head(0)
        )
        self.tree.heading(
            "#2", text="Size", anchor=tk.W, command=lambda: self.sel_head(1)
        )
        ytableScrollbar.config(command=self.tree.yview)
        self.tree.place(relx=0.0, rely=0.0, relwidth=BOXWID, relheight=1.0)
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

    def initBindKey(self):
        self.bind("<Return>", self.testCon)
        self.bind("<Delete>", self.eraseFile)

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

    def sel_head(self, col: int):
        if self.sort_methed is None or self.sort_methed[0] != col:
            self.sort_methed = (col, False)
        else:
            self.sort_methed = (col, not self.sort_methed[1])
        self.set_data(self.get_list(False), True)

    def get_list(self, force: bool = True):
        if force:
            self.data = self.client_socket.list()
        if self.sort_methed is not None:
            i, r = self.sort_methed
            self.data.sort(key=lambda tp: tp[i], reverse=r)
        return self.data

    def getSelFile(self):
        sel = self.tree.selection()
        return [str(self.tree.item(it, "values")[0]) for it in sel]

    def set_data(self, table: List[Tuple[str, int]], force: bool = False):
        with self.tree_lock:
            if force:
                for item in self.tree.get_children():
                    self.tree.delete(item)
                for file, size in table:
                    self.tree.insert("", tk.END, values=(file, format_size(size)))
            else:
                new_data = map(lambda tp: (tp[0], format_size(tp[1])), table)
                current_items = list(self.tree.get_children())
                current_data = {
                    tuple(self.tree.item(it)["values"]): it for it in current_items
                }
                for new_it in new_data:
                    if new_it in current_data:
                        item_id = current_data[new_it]
                        current_items.remove(item_id)
                    else:
                        self.tree.insert("", tk.END, values=new_it)
                for it in current_items:
                    self.tree.delete(it)

    def _updateList(self):
        self.set_data(self.get_list())

    @withThread
    @logException(stdloggers.err_logger)
    def testCon(self, event=None):
        try:
            self.block_button(UI_BLOCK)
            self.client_socket = self.newClient()
            self.client_socket.test()
            self._updateList()
            self.showinfo("Link Ok.")
        except (OSError, AssertionError) as err:
            self.showwarning(str(err))

    @withThread
    @logException(stdloggers.err_logger)
    def updateList(self):
        try:
            self.block_button(UI_BLOCK)
            self._updateList()
            self.update_toplever()
        except (OSError, AssertionError) as err:
            self.showwarning(str(err))

    @withThread
    @logException(stdloggers.err_logger)
    def eraseFile(self, event=None):
        self.block_button(UI_BLOCK)
        passwd = self.token.get()
        item = self.getSelFile()
        if len(item) == 0:
            self.showwarning(NO_ITEM)
        else:
            for fn in item:
                try:
                    self.showinfo_fromServer(self.client_socket.erase(fn, passwd), fn)
                except OSError as err:
                    self.showwarning(str(err), fn)
                else:
                    self._updateList()

    @withThread
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
                self.client_socket.insert(fn, passwd, callback=pushCallBack),
                getFilename(fn),
            )
            self._updateList()
        except (OSError, AssertionError) as err:
            self.showwarning(str(err), getFilename(fn))
        except UnicodeError:
            self.showwarning(FAIL_SEND, getFilename(fn))
        finally:
            pushCallBack(0, 0)

    @withThread
    def download(self):
        toplevel = None
        self.block_button(UI_BLOCK)
        passwd = self.token.get()
        item = self.getSelFile()
        if len(item) == 0:
            self.showwarning(NO_ITEM)
        elif len(item) > 1:
            self.showwarning(TOO_MANY_ITEM)
        else:
            try:
                # item = self.getSelFile()[0]
                toplevel = self.start_toplever(f"Download - {item[0]}")
                toplevel.start()
                ret = self.client_socket.get(item[0], passwd)
                if not toplevel.winfo_exists():
                    self.showinfo("Abort.", item[0])
                elif not ret[-1]:
                    ret.pop()
                    fn = filedialog.asksaveasfilename(
                        title=self.title(), initialfile=item[0]
                    )
                    if not fn:
                        return
                    with open(fn, "wb") as f:
                        f.write(ret)
                    self.showinfo("Install Ok.", item[0])
                else:
                    self.showinfo_fromServer(ret.decode(), item[0])
            except OSError as err:
                self.showwarning(str(err), item[0])
            except AssertionError as err:
                self.showwarning(str(err))
            finally:
                self.close_toplever(toplevel)

    def start_toplever(self, title: Optional[str] = None):
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

    def check_server(self, msg: str):
        return msg == OK.decode()

    def showinfo_fromServer(self, msg: str, source: Optional[str] = None):
        (self.showinfo if self.check_server(msg) else self.showwarning)(msg, source)

    def showinfo(self, msg: str, source: Optional[str] = None):
        if source is not None:
            msg = f"{source}: {msg}"
        if not self.ignoreInfo.get():
            messagebox.showinfo(self.title(), msg)
        else:
            stdloggers.log_logger(msg, before=INFO)

    def showwarning(self, msg: str, source: Optional[str] = None):
        if source is not None:
            msg = f"{source}: {msg}"
        if not self.ignoreWarn.get():
            messagebox.showwarning(self.title(), msg)
        else:
            stdloggers.warn_logger(msg, before=WARN)


if __name__ == "__main__":
    app = UI()
