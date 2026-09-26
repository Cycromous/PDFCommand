import os
import sys
import tkinter as tk

from theme import MINT_GREEN, TEXT_COLOR, BG_GRAY, WHITE
from ui_helpers import create_tool_card


class HomeFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_GRAY)
        self.controller = controller
        self.setup_gui()

    def setup_gui(self):
        # ── Sidebar ──────────────────────────────────────────────────
        sidebar_bg = "#1E293B"  # Slate dark background
        sidebar = tk.Frame(self, bg=sidebar_bg, width=230)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        # App Brand Header (clean text typography, no emoji)
        brand_frame = tk.Frame(sidebar, bg=sidebar_bg, pady=24, padx=18)
        brand_frame.pack(fill=tk.X)
        tk.Label(brand_frame, text="PDF COMMANDER", font=("Segoe UI", 12, "bold"),
                 fg=WHITE, bg=sidebar_bg, anchor="w").pack(fill=tk.X)
        tk.Label(brand_frame, text="Desktop Toolkit", font=("Segoe UI", 8),
                 fg="#94A3B8", bg=sidebar_bg, anchor="w").pack(fill=tk.X, pady=(2, 0))

        # Subtle divider
        tk.Frame(sidebar, bg="#334155", height=1).pack(fill=tk.X, padx=16, pady=(10, 16))

        # Dashboard / Home button (active state)
        nav_home = tk.Label(sidebar, text="  Dashboard", font=("Segoe UI", 10, "bold"),
                            bg=MINT_GREEN, fg="#0F172A", anchor="w", padx=16, pady=10,
                            cursor="hand2")
        nav_home.pack(fill=tk.X, padx=12, pady=2)

        # Section Label: Quick Tools
        tk.Label(sidebar, text="TOOLS", font=("Segoe UI", 8, "bold"),
                 fg="#64748B", bg=sidebar_bg, anchor="w", padx=20).pack(fill=tk.X, pady=(16, 6))

        # Direct links to all functional tools in the sidebar (no emojis)
        sidebar_tools = [
            ("Merge PDFs", "merger"),
            ("PDF Editor", "editor"),
            ("Split PDF", "splitter"),
            ("PDF Viewer", "viewer"),
            ("PDF Converter", "converter"),
        ]

        for text, frame_name in sidebar_tools:
            btn = tk.Label(sidebar, text=f"  {text}", font=("Segoe UI", 9),
                           bg=sidebar_bg, fg="#CBD5E1", anchor="w", padx=16, pady=8,
                           cursor="hand2")
            btn.pack(fill=tk.X, padx=12, pady=1)

            def make_hover(label, f_name):
                label.bind("<Enter>", lambda _e: label.config(bg="#334155", fg=WHITE))
                label.bind("<Leave>", lambda _e: label.config(bg=sidebar_bg, fg="#CBD5E1"))

                def on_sidebar_click(_e):
                    label.config(bg="#0F766E", fg=WHITE)
                    label.after(60, lambda: self.controller.show_frame(f_name))
                    label.after(350, lambda: label.config(bg=sidebar_bg, fg="#CBD5E1"))

                label.bind("<Button-1>", on_sidebar_click)

            make_hover(btn, frame_name)

        # Bottom Version & Offline indicator
        tk.Frame(sidebar, bg=sidebar_bg).pack(fill=tk.BOTH, expand=True)
        footer = tk.Frame(sidebar, bg=sidebar_bg, pady=16, padx=18)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        tk.Label(footer, text="Local & Offline", font=("Segoe UI", 8, "bold"),
                 fg="#10B981", bg=sidebar_bg, anchor="w").pack(fill=tk.X)
        tk.Label(footer, text="Version 1.0.0", font=("Segoe UI", 8),
                 fg="#64748B", bg=sidebar_bg, anchor="w").pack(fill=tk.X, pady=(2, 0))

        # ── Main Content Area ────────────────────────────────────────
        main_area = tk.Frame(self, bg=BG_GRAY)
        main_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Header Title
        header_container = tk.Frame(main_area, bg=BG_GRAY, pady=36, padx=50)
        header_container.pack(fill=tk.X)

        tk.Label(header_container, text="Welcome to PDF Commander",
                 font=("Segoe UI", 24, "bold"), bg=BG_GRAY, fg=TEXT_COLOR,
                 anchor="w").pack(fill=tk.X)
        tk.Label(header_container,
                 text="Select a tool below to edit, merge, split, view, or convert your PDF documents.",
                 font=("Segoe UI", 11), bg=BG_GRAY, fg="#64748B",
                 anchor="w").pack(fill=tk.X, pady=(4, 0))

        # ── Tools Grid Container ─────────────────────────────────────
        grid_container = tk.Frame(main_area, bg=BG_GRAY)
        grid_container.pack(fill=tk.BOTH, expand=True, padx=40, pady=(0, 40))

        # Center rows and columns
        grid_container.grid_rowconfigure(0, weight=1)
        grid_container.grid_rowconfigure(3, weight=1)
        grid_container.grid_columnconfigure(0, weight=1)
        grid_container.grid_columnconfigure(4, weight=1)

        tool_defs = [
            ("Merge PDFs", "Combine multiple PDF documents into a single file in any order.", "merger", "Merge"),
            ("PDF Editor", "Add text, draw shapes, and insert images or signatures onto pages.", "editor", "Edit"),
            ("Split PDF", "Extract specific pages or page ranges into a new standalone PDF.", "splitter", "Split"),
            ("PDF Viewer", "Open, read, and browse PDF documents with fluid navigation.", "viewer", "View"),
            ("PDF Converter", "Convert Word documents (.docx) and image files directly to PDF.", "converter", "Convert"),
        ]

        # Row 1: Merge, Editor, Split
        for col_idx, (title, desc, frame_name, badge) in enumerate(tool_defs[:3]):
            card = create_tool_card(
                grid_container, title, desc,
                lambda f=frame_name: self.controller.show_frame(f),
                badge=badge, width=260, height=155
            )
            card.grid(row=1, column=col_idx + 1, padx=12, pady=12, sticky="nsew")

        # Row 2 container to center the 2 remaining cards (Viewer, Converter)
        row2_frame = tk.Frame(grid_container, bg=BG_GRAY)
        row2_frame.grid(row=2, column=1, columnspan=3, pady=12)

        for title, desc, frame_name, badge in tool_defs[3:]:
            card = create_tool_card(
                row2_frame, title, desc,
                lambda f=frame_name: self.controller.show_frame(f),
                badge=badge, width=260, height=155
            )
            card.pack(side=tk.LEFT, padx=16)


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