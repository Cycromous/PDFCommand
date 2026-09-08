"""Owns the ONE Tk window for the whole app and swaps pages in and out
instead of opening a new Toplevel window per tool."""

import ctypes
import os
import sys
import tkinter as tk
from tkinter import messagebox

from theme import BG_GRAY

# TCL / TK library setup for Windows / PyInstaller if needed
if not getattr(sys, "frozen", False):
    base_python = getattr(sys, "base_prefix", sys.prefix)
    tcl_path = os.path.join(base_python, "tcl", "tcl8.6")
    tk_path = os.path.join(base_python, "tcl", "tk8.6")
    if os.path.isdir(tcl_path):
        os.environ["TCL_LIBRARY"] = tcl_path
    if os.path.isdir(tk_path):
        os.environ["TK_LIBRARY"] = tk_path

try:
    from Home import HomeFrame
    from PDFEditor import EditorFrame
    from PDFMerger import MergerFrame
    from PDFSplitter import SplitterFrame
    from PDFConverter import ConverterFrame
    from PDFViewer import ViewerFrame
except ImportError as e:
    messagebox.showerror(
        "Error",
        f"Could not find a necessary module:\n\n{e}\n\n"
        "Please ensure Home.py, PDFEditor.py, PDFMerger.py, PDFSplitter.py, "
        "PDFConverter.py, and PDFViewer.py are in this folder."
    )
    sys.exit()


class PDFCommanderApp:
    FRAME_CLASSES = {
        "home": HomeFrame,
        "editor": EditorFrame,
        "merger": MergerFrame,
        "splitter": SplitterFrame,
        "converter": ConverterFrame,
        "viewer": ViewerFrame,
    }

    FRAME_TITLES = {
        "home": "PDF Commander",
        "editor": "PDF Editor",
        "merger": "PDF Merger",
        "splitter": "PDF Splitter",
        "converter": "PDF Converter",
        "viewer": "PDF Viewer",
    }

    def __init__(self, root, startup_pdf=None):
        self.root = root
        self.root.title("PDF Commander")

        try:
            self.root.state("zoomed")
        except Exception:
            self.root.geometry("1400x900")

        try:
            base_path = sys._MEIPASS if getattr(sys, "frozen", False) else os.path.abspath(".")
            self.root.iconbitmap(os.path.join(base_path, "Commander.ico"))
        except Exception:
            pass

        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass

        self.root.configure(bg=BG_GRAY)

        self.container = tk.Frame(self.root, bg=BG_GRAY)
        self.container.pack(fill=tk.BOTH, expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        self._build_frame("home")

        if startup_pdf:
            self.show_frame("viewer")
            self.frames["viewer"].load_specific_pdf(startup_pdf)
        else:
            self.show_frame("home")

    def _build_frame(self, name):
        if name not in self.frames:
            frame_cls = self.FRAME_CLASSES[name]
            frame = frame_cls(self.container, self)
            frame.grid(row=0, column=0, sticky="nsew")
            self.frames[name] = frame
        return self.frames[name]

    def show_frame(self, name):
        frame = self._build_frame(name)
        frame.tkraise()
        self.root.title(self.FRAME_TITLES.get(name, "PDF Commander"))
        if hasattr(frame, "on_show"):
            frame.on_show()


# Backward compatibility alias
PDFCommandApp = PDFCommanderApp

