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

        # DPI Awareness for crisp UI and accurate screen metrics
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass

        # Center the window on whatever screen it opens on
        self.root.update_idletasks()
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        win_w = min(1400, int(screen_w * 0.9))
        win_h = min(900, int(screen_h * 0.9))
        pos_x = max(0, (screen_w - win_w) // 2)
        pos_y = max(0, (screen_h - win_h) // 2)
        self.root.geometry(f"{win_w}x{win_h}+{pos_x}+{pos_y}")

        try:
            base_path = sys._MEIPASS if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(base_path, "Commander.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
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

        self.frames = {}
        self.current_frame = None
        self.current_frame_name = None
        self._animating = False
        self._anim_timer = None
        self._anim_old = None
        self._anim_new = None

        self._build_frame("home")

        if startup_pdf:
            self.show_frame("viewer", animate=False)
            self.frames["viewer"].load_specific_pdf(startup_pdf)
        else:
            self.show_frame("home", animate=False)

    def _build_frame(self, name):
        if name not in self.frames:
            frame_cls = self.FRAME_CLASSES[name]
            frame = frame_cls(self.container, self)
            frame.place(relx=0, rely=0, relwidth=1.0, relheight=1.0)
            frame.lower()
            self.frames[name] = frame
        return self.frames[name]

    def _settle_animation(self):
        """Immediately settles any in-flight animation before starting another."""
        if self._anim_timer is not None:
            try:
                self.root.after_cancel(self._anim_timer)
            except Exception:
                pass
            self._anim_timer = None
        if self._animating:
            if self._anim_old and self._anim_old != self._anim_new:
                self._anim_old.place_forget()
            if self._anim_new:
                self._anim_new.place(relx=0, rely=0, relwidth=1.0, relheight=1.0)
                self._anim_new.tkraise()
            self._animating = False
            self._anim_old = None
            self._anim_new = None

    def show_frame(self, name, animate=True):
        if name == self.current_frame_name and not self._animating:
            return

        self._settle_animation()

        new_frame = self._build_frame(name)
        old_frame = self.current_frame

        self.root.title(self.FRAME_TITLES.get(name, "PDF Commander"))
        if hasattr(new_frame, "on_show"):
            new_frame.on_show()

        if not animate or old_frame is None or old_frame == new_frame:
            if old_frame and old_frame != new_frame:
                old_frame.place_forget()
            new_frame.place(relx=0, rely=0, relwidth=1.0, relheight=1.0)
            new_frame.tkraise()
            self.current_frame = new_frame
            self.current_frame_name = name
            return

        is_back = (name == "home")
        self._animating = True
        self._anim_old = old_frame
        self._anim_new = new_frame
        self.current_frame = new_frame
        self.current_frame_name = name

        total_steps = 15
        step_ms = 12

        if is_back:
            # Return Home: reveal Home underneath while current tool slides away to the right
            new_frame.place(relx=0, rely=0, relwidth=1.0, relheight=1.0)
            new_frame.lower()
            old_frame.place(relx=0, rely=0, relwidth=1.0, relheight=1.0)
            old_frame.tkraise()
        else:
            # Open Tool: new tool slides in from the right over current view
            old_frame.place(relx=0, rely=0, relwidth=1.0, relheight=1.0)
            new_frame.place(relx=1.0, rely=0, relwidth=1.0, relheight=1.0)
            new_frame.tkraise()

        def do_step(step_idx=0):
            if not self._animating:
                return

            if step_idx <= total_steps:
                t = step_idx / total_steps
                # Smooth cubic ease-out curve
                ease = 1.0 - (1.0 - t) ** 3
                if is_back:
                    old_frame.place_configure(relx=ease)
                else:
                    new_frame.place_configure(relx=1.0 - ease)

                self._anim_timer = self.root.after(step_ms, lambda: do_step(step_idx + 1))
            else:
                new_frame.place(relx=0, rely=0, relwidth=1.0, relheight=1.0)
                new_frame.tkraise()
                old_frame.place_forget()
                self._animating = False
                self._anim_timer = None
                self._anim_old = None
                self._anim_new = None

        do_step(0)


# Backward compatibility alias
PDFCommandApp = PDFCommanderApp