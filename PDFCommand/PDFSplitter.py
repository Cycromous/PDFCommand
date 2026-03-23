import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import fitz
import os
import sys

class ModernPDFSplitter:
    def __init__(self, root, main_app_window=None):
        self.root = root
        self.main_app_window = main_app_window
        self.root.title("PDF Splitter")
        
        try:
            base_path = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.abspath(".")
            self.root.iconbitmap(os.path.join(base_path, "Commander.ico"))
        except:
            pass
            
        self.root.configure(bg="#F0F2F5")
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}")
        
        try:
            self.root.state('zoomed')
        except:
            pass 
            
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.pdf_path = None
        self.setup_gui()

    def go_home(self):
        if self.main_app_window:
            self.main_app_window.deiconify() 
            try: self.main_app_window.state('zoomed')
            except: pass
            self.root.withdraw() 
        else:
            self.root.destroy()

    def on_close(self):
        if self.main_app_window: self.main_app_window.destroy()
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
        toolbar = tk.Frame(self.root, bg="#93E9BE", bd=0)
        toolbar.pack(fill=tk.X, side=tk.TOP)
        inner = tk.Frame(toolbar, bg="#93E9BE", pady=12, padx=15)
        inner.pack(fill=tk.X)

        tk.Button(inner, text="⬅ Home", command=self.go_home, bg="#93E9BE", fg="#1F2937", font=("Segoe UI", 10, "bold"), bd=0, cursor="hand2").pack(side=tk.LEFT, padx=(0, 15))
        
        self.btn_load = self.create_rounded_button(inner, "📂 Load PDF", "#FFFFFF", "#374151", self.load_pdf)
        self.btn_load.pack(side=tk.LEFT, padx=10)

        self.btn_split = self.create_rounded_button(inner, "✂ Split & Save", "#111827", "#FFFFFF", self.split_pdf)
        self.btn_split.pack(side=tk.RIGHT, padx=5)

        # Content Area
        self.work_area = tk.Frame(self.root, bg="#F0F2F5", pady=50)
        self.work_area.pack(expand=True, fill=tk.BOTH)

        self.info_label = tk.Label(self.work_area, text="No PDF Loaded", font=("Segoe UI", 16, "bold"), bg="#F0F2F5", fg="#1F2937")
        self.info_label.pack(pady=20)

        self.range_frame = tk.Frame(self.work_area, bg="#FFFFFF", padx=30, pady=30, highlightthickness=1, highlightbackground="#D1D5DB")
        
        tk.Label(self.range_frame, text="Enter Page Range (e.g. 1-3, 5, 8-10):", bg="#FFFFFF", font=("Segoe UI", 11)).pack(pady=(0, 10))
        self.entry_range = tk.Entry(self.range_frame, font=("Segoe UI", 12), width=30, bd=1, relief="solid")
        self.entry_range.pack(pady=10)

    def load_pdf(self):
        path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if path:
            self.pdf_path = path
            doc = fitz.open(path)
            self.page_count = len(doc)
            self.info_label.config(text=f"Loaded: {fitz.os.path.basename(path)}\n({self.page_count} Pages)")
            self.range_frame.pack(pady=20)
            doc.close()

    def split_pdf(self):
        if not self.pdf_path: return
        range_str = self.entry_range.get().replace(" ", "")
        if not range_str:
            messagebox.showwarning("Input Required", "Please enter a page range.")
            return

        try:
            pages_to_keep = []
            parts = range_str.split(',')
            for part in parts:
                if '-' in part:
                    start, end = map(int, part.split('-'))
                    pages_to_keep.extend(range(start-1, end))
                else:
                    pages_to_keep.append(int(part)-1)
            
            pages_to_keep = sorted(list(set(pages_to_keep)))

            if any(p < 0 or p >= self.page_count for p in pages_to_keep):
                messagebox.showerror("Error", f"Page out of bounds!\n\nYou entered a page number that doesn't exist. This PDF only has {self.page_count} pages.")
                return

            save_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
            if save_path:
                src = fitz.open(self.pdf_path)
                src.select(pages_to_keep)
                src.save(save_path)
                src.close()
                
                messagebox.showinfo("Success", "PDF Split Successfully!")
                
        except ValueError:
            messagebox.showerror("Error", "Invalid range format. Use numbers and dashes only (e.g., 1-3, 5).")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred while splitting:\n\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernPDFSplitter(root)
    root.mainloop()