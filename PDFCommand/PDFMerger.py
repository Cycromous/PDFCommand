import tkinter as tk
from tkinter import filedialog, messagebox
import fitz
import os
import sys

class ModernPDFMerger:
    def __init__(self, root, main_app_window=None):
        self.root = root
        self.main_app_window = main_app_window
        self.root.title("PDF Merger")
        self.root.configure(bg="#F0F2F5")
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}")
        
        try:
            base_path = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.abspath(".")
            self.root.iconbitmap(os.path.join(base_path, "Commander.ico"))
        except:
            pass
        
        try:
            self.root.state('zoomed')
        except:
            pass 
            
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.pdf_data = [] 
        self.selected_idx = None
        
        self.setup_gui()

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

    def create_rounded_button(self, parent, text, bg_color, fg_color, command, width=140, height=36):
        canvas = tk.Canvas(parent, width=width, height=height, bg="#93E9BE", highlightthickness=0, bd=0)
        radius = height / 2
        x1, y1, x2, y2 = 2, 2, width-2, height-2
        points = [
            x1+radius, y1, x2-radius, y1, x2, y1, x2, y1+radius,
            x2, y2-radius, x2, y2, x2-radius, y2, x1+radius, y2,
            x1, y2, x1, y2-radius, x1, y1+radius, x1, y1
        ]
        
        shape = canvas.create_polygon(points, smooth=True, fill=bg_color)
        txt = canvas.create_text(width/2, height/2, text=text, fill=fg_color, font=("Segoe UI", 10, "bold"))
        
        def on_click(e): command()
        canvas.bind("<Button-1>", on_click)
        canvas.configure(cursor="hand2")
        
        return canvas

    def setup_gui(self):
        self.toolbar_color = "#93E9BE"
        toolbar = tk.Frame(self.root, bg=self.toolbar_color, bd=0)
        toolbar.pack(fill=tk.X, side=tk.TOP, pady=(0, 0))

        inner_toolbar = tk.Frame(toolbar, bg=self.toolbar_color, pady=12, padx=15)
        inner_toolbar.pack(fill=tk.X)

        btn_home = tk.Button(
            inner_toolbar, text="⬅ Home", command=self.go_home,
            bg=self.toolbar_color, fg="#1F2937", font=("Segoe UI", 10, "bold"),
            bd=0, activebackground=self.toolbar_color, cursor="hand2"
        )
        btn_home.pack(side=tk.LEFT, padx=(0, 15))

        btn_add = self.create_rounded_button(
            inner_toolbar, text="➕ Add PDFs", 
            bg_color="#FFFFFF", fg_color="#374151", command=self.add_pdfs, width=120
        )
        btn_add.pack(side=tk.LEFT, padx=(0, 15))

        tk.Frame(inner_toolbar, bg="#71C89F", width=2).pack(side=tk.LEFT, fill=tk.Y, pady=5, padx=10)

        btn_up = self.create_rounded_button(inner_toolbar, text="⬆ Move Up", bg_color=self.toolbar_color, fg_color="#1F2937", command=self.move_up, width=100)
        btn_up.pack(side=tk.LEFT, padx=5)
        
        btn_down = self.create_rounded_button(inner_toolbar, text="⬇ Move Down", bg_color=self.toolbar_color, fg_color="#1F2937", command=self.move_down, width=130)
        btn_down.pack(side=tk.LEFT, padx=5)

        btn_remove = self.create_rounded_button(inner_toolbar, text="❌ Remove", bg_color=self.toolbar_color, fg_color="#E53E3E", command=self.remove_pdf, width=100)
        btn_remove.pack(side=tk.LEFT, padx=5)

        btn_merge = self.create_rounded_button(
            inner_toolbar, text="🔗 Merge & Save", 
            bg_color="#111827", fg_color="#FFFFFF", command=self.merge_pdfs, width=170
        )
        btn_merge.pack(side=tk.RIGHT, padx=5)

        workspace = tk.Frame(self.root, bg="#F0F2F5", padx=50, pady=40)
        workspace.pack(expand=True, fill=tk.BOTH)

        tk.Label(workspace, text="PDFs to Merge (Top to Bottom):", font=("Segoe UI", 14, "bold"), bg="#F0F2F5", fg="#1F2937").pack(anchor="w", pady=(0, 10))

        list_container = tk.Frame(workspace, bg="#FFFFFF", highlightthickness=1, highlightbackground="#D1D5DB")
        list_container.pack(expand=True, fill=tk.BOTH)
        
        self.canvas_scroll = tk.Canvas(list_container, bg="#FFFFFF", highlightthickness=0)
        scrollbar = tk.Scrollbar(list_container, orient=tk.VERTICAL, command=self.canvas_scroll.yview)
        self.scrollable_inner = tk.Frame(self.canvas_scroll, bg="#FFFFFF")

        self.scrollable_inner.bind(
            "<Configure>",
            lambda e: self.canvas_scroll.configure(scrollregion=self.canvas_scroll.bbox("all"))
        )

        self.canvas_frame_window = self.canvas_scroll.create_window((0, 0), window=self.scrollable_inner, anchor="nw")

        self.canvas_scroll.bind(
            "<Configure>",
            lambda e: self.canvas_scroll.itemconfig(self.canvas_frame_window, width=e.width)
        )

        self.canvas_scroll.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas_scroll.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Enable mouse wheel scrolling
        def _on_mousewheel(event):
            self.canvas_scroll.yview_scroll(int(-1*(event.delta/120)), "units")
        self.canvas_scroll.bind_all("<MouseWheel>", _on_mousewheel)

    def add_pdfs(self):
        filepaths = filedialog.askopenfilenames(filetypes=[("PDF Files", "*.pdf")])
        for path in filepaths:
            try:
                doc = fitz.open(path)
                page_count = len(doc)
                
                page = doc[0]
                scale = 100.0 / page.rect.height
                mat = fitz.Matrix(scale, scale)
                pix = page.get_pixmap(matrix=mat)
                
                tk_img = tk.PhotoImage(data=pix.tobytes("ppm"))
                doc.close()

                self.pdf_data.append({
                    "path": path,
                    "name": os.path.basename(path),
                    "pages": page_count,
                    "thumb": tk_img
                })
            except Exception as e:
                messagebox.showerror("Error", f"Could not load thumbnail for {os.path.basename(path)}")
        
        if len(self.pdf_data) > 0 and self.selected_idx is None:
            self.selected_idx = 0
            
        self.render_visual_list()

    def render_visual_list(self):
        """ Destroys and redraws all the visual PDF cards instantly """
        for widget in self.scrollable_inner.winfo_children():
            widget.destroy()

        for i, data in enumerate(self.pdf_data):
            is_selected = (i == self.selected_idx)
            bg_color = "#D1F4E0" if is_selected else "#FFFFFF"
            border_color = "#2ECC8A" if is_selected else "#E5E7EB"

            card = tk.Frame(self.scrollable_inner, bg=bg_color, highlightthickness=2, highlightbackground=border_color, padx=15, pady=15, cursor="hand2")
            card.pack(fill=tk.X, pady=6, padx=10)

            def make_select_cmd(index):
                return lambda e: self.select_item(index)
            
            cmd = make_select_cmd(i)
            card.bind("<Button-1>", cmd)

            lbl_img = tk.Label(card, image=data['thumb'], bg=bg_color, highlightthickness=1, highlightbackground="#D1D5DB")
            lbl_img.pack(side=tk.LEFT, padx=(0, 20))
            lbl_img.bind("<Button-1>", cmd)

            # Info Text Container
            info_frame = tk.Frame(card, bg=bg_color)
            info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            info_frame.bind("<Button-1>", cmd)

            lbl_name = tk.Label(info_frame, text=data['name'], font=("Segoe UI", 13, "bold"), bg=bg_color, fg="#1F2937", anchor="w")
            lbl_name.pack(fill=tk.X, pady=(10, 2))
            lbl_name.bind("<Button-1>", cmd)

            lbl_pages = tk.Label(info_frame, text=f"📄 {data['pages']} Pages", font=("Segoe UI", 10), bg=bg_color, fg="#6B7280", anchor="w")
            lbl_pages.pack(fill=tk.X)
            lbl_pages.bind("<Button-1>", cmd)

        self.scrollable_inner.update_idletasks()
        self.canvas_scroll.configure(scrollregion=self.canvas_scroll.bbox("all"))

    def select_item(self, idx):
        self.selected_idx = idx
        self.render_visual_list()

    def move_up(self):
        if self.selected_idx is not None and self.selected_idx > 0:
            idx = self.selected_idx
            self.pdf_data[idx], self.pdf_data[idx - 1] = self.pdf_data[idx - 1], self.pdf_data[idx]
            self.selected_idx -= 1
            self.render_visual_list()

    def move_down(self):
        if self.selected_idx is not None and self.selected_idx < len(self.pdf_data) - 1:
            idx = self.selected_idx
            self.pdf_data[idx], self.pdf_data[idx + 1] = self.pdf_data[idx + 1], self.pdf_data[idx]
            self.selected_idx += 1
            self.render_visual_list()

    def remove_pdf(self):
        if self.selected_idx is not None:
            self.pdf_data.pop(self.selected_idx)
            
            if self.selected_idx >= len(self.pdf_data):
                self.selected_idx = len(self.pdf_data) - 1
            if self.selected_idx < 0:
                self.selected_idx = None
                
            self.render_visual_list()

    def merge_pdfs(self):
        if len(self.pdf_data) < 2:
            messagebox.showwarning("Not Enough Files", "Please add at least 2 PDFs to merge.")
            return
            
        save_path = filedialog.asksaveasfilename(
            defaultextension=".pdf", 
            filetypes=[("PDF Documents", "*.pdf")],
            title="Save Merged PDF As..."
        )
        
        if not save_path:
            return
            
        try:
            merged_doc = fitz.open()
            
            for item in self.pdf_data:
                doc_to_insert = fitz.open(item['path'])
                merged_doc.insert_pdf(doc_to_insert)
                doc_to_insert.close()
                
            merged_doc.save(save_path)
            merged_doc.close()
            
            messagebox.showinfo("Success", "PDFs merged successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to merge PDFs:\n\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernPDFMerger(root)
    root.mainloop()