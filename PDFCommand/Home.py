import os
import sys
import tkinter as tk
from tkinter import messagebox

from theme import MINT_GREEN, TEXT_COLOR, BG_GRAY, WHITE, SIDEBAR_BG, GENTLE_GRAY_BORDER
from ui_helpers import create_hover_card


class HomeFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_GRAY)
        self.controller = controller
        self.setup_gui()

    def setup_gui(self):
        sidebar = tk.Frame(self, bg=SIDEBAR_BG, width=220, highlightthickness=1,
                            highlightbackground=GENTLE_GRAY_BORDER)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="PDF Commander", font=("Segoe UI", 16, "bold"),
                 fg=TEXT_COLOR, bg=SIDEBAR_BG, pady=25).pack()

        navs = [("🏠 Home", None), ("🔧 Tools", None),
                ("⏱ Tasks History", self.launch_dummy), ("⚙ Preferences", self.launch_dummy)]

        for text, cmd in navs:
            is_active = "Home" in text
            bg_color = MINT_GREEN if is_active else SIDEBAR_BG
            fg_color = "#000000" if is_active else "#6B7280"
            font_type = ("Segoe UI", 11, "bold" if is_active else "normal")

            btn = tk.Label(sidebar, text=text, font=font_type, bg=bg_color, fg=fg_color,
                            anchor="w", padx=25, pady=12, cursor="hand2")
            btn.pack(fill=tk.X, padx=15, pady=4)
            if cmd:
                btn.bind("<Button-1>", lambda e, c=cmd: c())

        main_area = tk.Frame(self, bg=BG_GRAY)
        main_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        header_frame = tk.Frame(main_area, bg=WHITE, highlightthickness=1,
                                 highlightbackground=GENTLE_GRAY_BORDER, pady=30)
        header_frame.pack(fill=tk.X, padx=50, pady=(50, 0))
        tk.Label(header_frame, text="Tools Dashboard", font=("Segoe UI", 28, "bold"),
                 bg=WHITE, fg=TEXT_COLOR).pack()

        tools_container = tk.Frame(main_area, bg=BG_GRAY, pady=40)
        tools_container.pack(fill=tk.BOTH, expand=True, padx=50)

        tk.Label(tools_container, text="Available Tools", font=("Segoe UI", 18, "bold"),
                 bg=BG_GRAY, fg=TEXT_COLOR).pack(pady=(0, 30))

        grid_frame = tk.Frame(tools_container, bg=BG_GRAY)
        grid_frame.pack()

        tools = [
            ("Merge", "merger"),
            ("Editor", "editor"),
            ("Split", "splitter"),
            ("Viewer", "viewer"),
            ("Converter", "converter"),
        ]
        for title, frame_name in tools:
            card = create_hover_card(grid_frame, title,
                                      lambda n=frame_name: self.controller.show_frame(n))
            card.pack(side=tk.LEFT, padx=20)

    def launch_dummy(self):
        messagebox.showinfo("Coming Soon", "This feature is currently under construction!")


# Backward compatibility aliases
ModernPDFHome = HomeFrame


def PDFCommandApp(root, startup_pdf=None):
    from app_controller import PDFCommanderApp
    return PDFCommanderApp(root, startup_pdf=startup_pdf)


if __name__ == "__main__":
    if not getattr(sys, "frozen", False):
        base_python = getattr(sys, "base_prefix", sys.prefix)
        tcl_path = os.path.join(base_python, "tcl", "tcl8.6")
        tk_path = os.path.join(base_python, "tcl", "tk8.6")
        if os.path.isdir(tcl_path):
            os.environ["TCL_LIBRARY"] = tcl_path
        if os.path.isdir(tk_path):
            os.environ["TK_LIBRARY"] = tk_path

    if "Home" not in sys.modules:
        sys.modules["Home"] = sys.modules["__main__"]

    from app_controller import PDFCommanderApp

    root = tk.Tk()

    startup_pdf = None
    if len(sys.argv) > 1 and sys.argv[1].lower().endswith(".pdf"):
        startup_pdf = sys.argv[1]

    app = PDFCommanderApp(root, startup_pdf=startup_pdf)
    root.mainloop()