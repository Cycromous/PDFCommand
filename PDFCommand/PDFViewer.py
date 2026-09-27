import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox

import fitz  # PyMuPDF

from theme import BG_GRAY, MINT_GREEN, WHITE, TEXT_COLOR
from ui_helpers import create_rounded_button


class ViewerFrame(tk.Frame):
    def __init__(self, parent, controller, startup_pdf=None):
        super().__init__(parent, bg=BG_GRAY)
        self.controller = controller
        self.root = controller.root

        self.pdf_path = None
        self.pdf_doc = None
        self.current_page_num = 0
        self.total_pages = 0

        self.page_image = None
        self.after_id = None

        self.setup_gui()

        if startup_pdf:
            self.load_specific_pdf(startup_pdf)

    def nav_to(self, page_name):
        self.controller.show_frame(page_name)

    def go_home(self):
        self.controller.show_frame("home")
    def create_sidebar_button(self, parent, text, is_active=False, command=None):
        btn = tk.Label(
            parent, text=text,
            bg=MINT_GREEN if is_active else "#1E293B",
            fg="#1F2937" if is_active else "#CBD5E1",
            font=("Segoe UI", 11, "bold" if is_active else "normal"),
            anchor="w", padx=20, pady=10, cursor="hand2"
        )
        btn.pack(fill=tk.X, pady=2, padx=10)
        if not is_active:
            btn.bind("<Enter>", lambda e: btn.config(bg="#334155", fg="#FFFFFF"))
            btn.bind("<Leave>", lambda e: btn.config(bg="#1E293B", fg="#CBD5E1"))
        if command:
            btn.bind("<Button-1>", lambda e: command())
        return btn
    def setup_gui(self):
        sidebar = tk.Frame(self, bg="#1E293B", width=230)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        brand_lbl = tk.Label(sidebar, text="PDF COMMANDER", bg="#1E293B", fg=WHITE,
                             font=("Segoe UI", 16, "bold"), anchor="w", padx=20, pady=15)
        brand_lbl.pack(fill=tk.X)
        sub_lbl = tk.Label(sidebar, text="Desktop Toolkit", bg="#1E293B", fg="#94A3B8",
                           font=("Segoe UI", 9), anchor="w", padx=20)
        sub_lbl.pack(fill=tk.X, pady=(0, 10))
        tk.Frame(sidebar, bg="#334155", height=1).pack(fill=tk.X, padx=20, pady=15)
        self.create_sidebar_button(sidebar, "Open PDF", command=self.open_pdf)
        self.create_sidebar_button(sidebar, "Edit This PDF", command=self.open_in_editor)
        
        tk.Frame(sidebar, bg="#334155", height=1).pack(fill=tk.X, padx=20, pady=15)
        nav_lbl = tk.Label(sidebar, text="PAGE NAVIGATION", bg="#1E293B", fg="#64748B",
                           font=("Segoe UI", 8, "bold"), anchor="w", padx=20)
        nav_lbl.pack(fill=tk.X, pady=(0, 6))
        nav_ctrl_frame = tk.Frame(sidebar, bg="#1E293B")
        nav_ctrl_frame.pack(fill=tk.X, padx=14)
        self.btn_prev = tk.Label(nav_ctrl_frame, text="◀ Prev", bg="#334155", fg="#CBD5E1", 
                                 font=("Segoe UI", 9, "bold"), cursor="hand2", padx=8, pady=5)
        self.btn_prev.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 4))
        self.btn_prev.bind("<Button-1>", lambda e: self.prev_page())
        self.btn_prev.bind("<Enter>", lambda e: self.btn_prev.config(bg="#475569"))
        self.btn_prev.bind("<Leave>", lambda e: self.btn_prev.config(bg="#334155"))
        self.btn_next = tk.Label(nav_ctrl_frame, text="Next ▶", bg="#334155", fg="#CBD5E1", 
                                 font=("Segoe UI", 9, "bold"), cursor="hand2", padx=8, pady=5)
        self.btn_next.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(4, 0))
        self.btn_next.bind("<Button-1>", lambda e: self.next_page())
        self.btn_next.bind("<Enter>", lambda e: self.btn_next.config(bg="#475569"))
        self.btn_next.bind("<Leave>", lambda e: self.btn_next.config(bg="#334155"))
        self.lbl_page = tk.Label(sidebar, text="No PDF Loaded", font=("Segoe UI", 9, "bold"),
                                 bg="#1E293B", fg="#94A3B8", pady=6)
        self.lbl_page.pack(fill=tk.X)
        tk.Frame(sidebar, bg="#334155", height=1).pack(fill=tk.X, padx=20, pady=15)
        nav_label = tk.Label(sidebar, text="NAVIGATION", bg="#1E293B", fg="#64748B",
                             font=("Segoe UI", 8, "bold"), anchor="w", padx=20)
        nav_label.pack(fill=tk.X, pady=(0, 6))
        self.create_sidebar_button(sidebar, "Dashboard", command=self.go_home)
        self.create_sidebar_button(sidebar, "PDF Viewer", is_active=True)
        self.create_sidebar_button(sidebar, "Merge PDFs", command=lambda: self.nav_to("merger"))
        self.create_sidebar_button(sidebar, "PDF Editor", command=lambda: self.nav_to("editor"))
        self.create_sidebar_button(sidebar, "Split PDF", command=lambda: self.nav_to("splitter"))
        self.create_sidebar_button(sidebar, "PDF Converter", command=lambda: self.nav_to("converter"))
        footer = tk.Frame(sidebar, bg="#1E293B")
        footer.pack(side=tk.BOTTOM, fill=tk.X, pady=16)
        tk.Label(footer, text="Local & Offline", bg="#1E293B", fg="#10B981", font=("Segoe UI", 8, "bold")).pack()
        tk.Label(footer, text="Version 1.0.0", bg="#1E293B", fg="#64748B", font=("Segoe UI", 8)).pack()
        self.canvas_frame = tk.Frame(self, bg=BG_GRAY)
        self.canvas_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self.canvas = tk.Canvas(self.canvas_frame, bg=BG_GRAY, bd=0, highlightthickness=0)
        self.canvas.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

    def open_pdf(self):
        path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if path:
            self.load_specific_pdf(path)

    def load_specific_pdf(self, path):
        self.pdf_path = path
        self.pdf_doc = fitz.open(path)
        self.total_pages = len(self.pdf_doc)
        self.current_page_num = 0
        self.render_page()

    def prev_page(self):
        if self.current_page_num > 0:
            self.current_page_num -= 1
            self.render_page()

    def next_page(self):
        if self.current_page_num < self.total_pages - 1:
            self.current_page_num += 1
            self.render_page()

    def on_show(self):
        if self.pdf_doc:
            self.render_page()

    def render_page_delayed(self):
        if self.after_id:
            self.after_cancel(self.after_id)
        self.after_id = self.after(200, self.render_page)

    def render_page(self):
        if not self.pdf_doc:
            return
        page = self.pdf_doc[self.current_page_num]

        self.lbl_page.config(text=f"Page {self.current_page_num + 1} of {self.total_pages}")

        # Update navigation buttons state
        if self.current_page_num > 0:
            self.btn_prev.config(fg="#FFFFFF")
        else:
            self.btn_prev.config(fg="#64748B")

        if self.current_page_num < self.total_pages - 1:
            self.btn_next.config(fg="#FFFFFF")
        else:
            self.btn_next.config(fg="#64748B")

        self.canvas.update_idletasks()
        canvas_height = self.canvas.winfo_height()
        if canvas_height <= 1:
            canvas_height = self.root.winfo_screenheight() - 150

        scale = (canvas_height * 0.98) / page.rect.height
        mat = fitz.Matrix(scale, scale)
        pix = page.get_pixmap(matrix=mat)

        self.page_image = tk.PhotoImage(data=pix.tobytes("ppm"))
        self.canvas.delete("all")

        canvas_width = self.canvas.winfo_width()
        if canvas_width <= 1:
            canvas_width = self.root.winfo_screenwidth() - 230

        x_offset = max(0, (canvas_width - pix.width) // 2)

        self.canvas.create_rectangle(
            x_offset + 3, 13, x_offset + pix.width + 3, 13 + pix.height,
            fill="#D1D5DB", outline=""
        )
        self.canvas.create_image(x_offset, 10, anchor=tk.NW, image=self.page_image)

    def open_in_editor(self):
        if not self.pdf_path:
            messagebox.showwarning("No PDF", "Please open a PDF first to edit it.")
            return

        self.controller.show_frame("editor")
        self.controller.frames["editor"].load_specific_pdf(
            self.pdf_path, start_page=self.current_page_num
        )


# Backward compatibility alias
ModernPDFViewer = ViewerFrame

if __name__ == "__main__":
    from app_controller import PDFCommanderApp

    root = tk.Tk()
    startup_pdf = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].lower().endswith(".pdf") else None
    app = PDFCommanderApp(root, startup_pdf=startup_pdf)
    if not startup_pdf:
        app.show_frame("viewer")
    root.mainloop()