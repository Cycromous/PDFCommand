import tkinter as tk
from tkinter import filedialog, messagebox
import fitz  # PyMuPDF
import os
import sys

# --- THE HANDOFF: Import your existing Editor app! ---
from PDFEditor import ModernPDFEditor 

class ModernPDFViewer:
    def __init__(self, root, main_app_window=None, startup_pdf=None):
        self.root = root
        self.main_app_window = main_app_window
        self.root.title("PDF Viewer")
        self.root.configure(bg="#F0F2F5")
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}")
        
        try:
            base_path = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.abspath(".")
            self.root.iconbitmap(os.path.join(base_path, "Commander.ico"))
            self.root.state('zoomed')
        except: 
            pass 
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.pdf_path = None
        self.pdf_doc = None
        self.current_page_num = 0
        self.total_pages = 0
        
        self.setup_gui()
        
        if startup_pdf:
            self.load_specific_pdf(startup_pdf)

    def go_home(self):
        if self.main_app_window:
            self.main_app_window.deiconify() 
            try: 
                self.main_app_window.state('zoomed')
            except: 
                pass
            self.root.withdraw() 
        else:
            self.root.destroy()

    def on_close(self):
        if self.main_app_window: 
            self.main_app_window.destroy()
        self.root.destroy()

    # --- UNIFIED UI: Custom Rounded Buttons ---
    def create_rounded_button(self, parent, text, bg_color, fg_color, command, width=140, height=40):
        # We grab the parent's background color so the rounded corners blend perfectly!
        canvas = tk.Canvas(parent, width=width, height=height, bg=parent.cget("bg"), highlightthickness=0, bd=0)
        radius = height / 2
        x1, y1, x2, y2 = 2, 2, width-2, height-2
        points = [
            x1+radius, y1, x2-radius, y1, x2, y1, x2, y1+radius,
            x2, y2-radius, x2, y2, x2-radius, y2, x1+radius, y2,
            x1, y2, x1, y2-radius, x1, y1+radius, x1, y1
        ]
        
        shape = canvas.create_polygon(points, smooth=True, fill=bg_color)
        txt = canvas.create_text(width/2, height/2, text=text, fill=fg_color, font=("Segoe UI", 10, "bold"))
        
        def on_click(e): 
            # Check if the button is "disabled" (grey text) before firing the command
            if canvas.itemcget(txt, "fill") != "#9CA3AF":
                command()

        canvas.tag_bind(shape, "<Button-1>", on_click)
        canvas.tag_bind(txt, "<Button-1>", on_click)
        canvas.bind("<Button-1>", on_click)
        canvas.configure(cursor="hand2")
        
        return canvas, shape, txt

    def setup_gui(self):
        # Toolbar
        self.toolbar_color = "#93E9BE"
        toolbar = tk.Frame(self.root, bg=self.toolbar_color, bd=0)
        toolbar.pack(fill=tk.X, side=tk.TOP)
        
        inner = tk.Frame(toolbar, bg=self.toolbar_color, pady=12, padx=15)
        inner.pack(fill=tk.X)

        tk.Button(inner, text="⬅ Home", command=self.go_home, bg=self.toolbar_color, fg="#1F2937", font=("Segoe UI", 10, "bold"), bd=0, activebackground=self.toolbar_color, cursor="hand2").pack(side=tk.LEFT, padx=(0, 15))
        
        # Rounded "Open PDF" Button
        self.btn_open = self.create_rounded_button(inner, text="📂 Open PDF", bg_color="#FFFFFF", fg_color="#374151", command=self.open_pdf, width=140)
        self.btn_open[0].pack(side=tk.LEFT, padx=(0, 10))

        tk.Frame(inner, bg="#71C89F", width=2).pack(side=tk.LEFT, fill=tk.Y, pady=5, padx=10)
        
        # Rounded "Edit This PDF" Button
        self.btn_edit = self.create_rounded_button(inner, text="✏️ Edit This PDF", bg_color="#111827", fg_color="#FFFFFF", command=self.open_in_editor, width=160)
        self.btn_edit[0].pack(side=tk.LEFT, padx=5)

        # Nav Bar
        self.nav_frame = tk.Frame(self.root, bg="#E5E7EB", pady=8)
        self.nav_frame.pack(fill=tk.X)
        
        # Rounded Navigation Buttons (Starts greyed out)
        self.btn_prev = self.create_rounded_button(self.nav_frame, text="◀ Previous", bg_color="#FFFFFF", fg_color="#9CA3AF", command=self.prev_page, width=110, height=32)
        self.btn_prev[0].pack(side=tk.LEFT, padx=20)
        
        self.lbl_page = tk.Label(self.nav_frame, text="No PDF Loaded", font=("Segoe UI", 10, "bold"), bg="#E5E7EB", fg="#374151")
        self.lbl_page.pack(side=tk.LEFT, expand=True)
        
        self.btn_next = self.create_rounded_button(self.nav_frame, text="Next ▶", bg_color="#FFFFFF", fg_color="#9CA3AF", command=self.next_page, width=110, height=32)
        self.btn_next[0].pack(side=tk.RIGHT, padx=20)
        
        # Workspace Canvas
        canvas_frame = tk.Frame(self.root, bg="#F0F2F5")
        canvas_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        self.canvas = tk.Canvas(canvas_frame, bg="#F0F2F5", bd=0, highlightthickness=0)
        self.canvas.pack(expand=True, fill=tk.BOTH)

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

    def render_page(self):
        if not self.pdf_doc: return
        page = self.pdf_doc[self.current_page_num]
        
        self.lbl_page.config(text=f"Page {self.current_page_num + 1} of {self.total_pages}")
        
        # --- UNIFIED NAV LOGIC: Visually enable/disable the rounded buttons ---
        prev_canvas, _, prev_txt = self.btn_prev
        if self.current_page_num > 0:
            prev_canvas.itemconfig(prev_txt, fill="#1F2937") # Active color
            prev_canvas.config(cursor="hand2")
        else:
            prev_canvas.itemconfig(prev_txt, fill="#9CA3AF") # Disabled grey
            prev_canvas.config(cursor="arrow")

        next_canvas, _, next_txt = self.btn_next
        if self.current_page_num < self.total_pages - 1:
            next_canvas.itemconfig(next_txt, fill="#1F2937") # Active color
            next_canvas.config(cursor="hand2")
        else:
            next_canvas.itemconfig(next_txt, fill="#9CA3AF") # Disabled grey
            next_canvas.config(cursor="arrow")
        # -------------------------------------------------------------------
        
        canvas_height = self.canvas.winfo_height()
        if canvas_height <= 1: canvas_height = self.root.winfo_screenheight() - 150 
            
        scale = (canvas_height * 0.98) / page.rect.height
        mat = fitz.Matrix(scale, scale)
        pix = page.get_pixmap(matrix=mat)
        
        self.page_image = tk.PhotoImage(data=pix.tobytes("ppm"))
        self.canvas.delete("all")
        
        canvas_width = self.canvas.winfo_width()
        if canvas_width <= 1: canvas_width = self.root.winfo_screenwidth()
            
        x_offset = max(0, (canvas_width - pix.width) // 2)
        
        self.canvas.create_rectangle(x_offset + 3, 10 + 3, x_offset + pix.width + 3, 10 + pix.height + 3, fill="#D1D5DB", outline="")
        self.canvas.create_image(x_offset, 10, anchor=tk.NW, image=self.page_image)

    def open_in_editor(self):
        if not self.pdf_path:
            messagebox.showwarning("No PDF", "Please open a PDF first to edit it.")
            return
            
        self.root.withdraw()
        
        editor_window = tk.Toplevel(self.root)
        
        editor_app = ModernPDFEditor(editor_window, self.root)
        
        editor_app.pdf_doc = fitz.open(self.pdf_path)
        editor_app.total_pages = len(editor_app.pdf_doc)
        editor_app.current_page_num = self.current_page_num 
        
        editor_app.master_text_items = {i: {} for i in range(editor_app.total_pages)}
        editor_app.master_shape_items = {i: {} for i in range(editor_app.total_pages)}
        editor_app.master_image_items = {i: {} for i in range(editor_app.total_pages)}
        
        editor_app.render_page()

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernPDFViewer(root)
    root.mainloop()