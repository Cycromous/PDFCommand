import tkinter as tk
from tkinter import filedialog, messagebox
import fitz
import os
import sys

try:
    from docx2pdf import convert as convert_docx
except ImportError:
    convert_docx = None

class ModernPDFConverter:
    def __init__(self, root, main_app_window=None):
        self.root = root
        self.main_app_window = main_app_window
        self.root.title("PDF Converter")
        
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
        
        self.files_to_convert = []
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
        canvas.create_text(width/2, height/2, text=text, fill=fg_color, font=("Segoe UI", 10, "bold"))
        
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

        tk.Button(inner_toolbar, text="Home", command=self.go_home, bg=self.toolbar_color, fg="#1F2937", font=("Segoe UI", 10, "bold"), bd=0, activebackground=self.toolbar_color, cursor="hand2").pack(side=tk.LEFT, padx=(0, 15))
        
        self.create_rounded_button(inner_toolbar, text="Add Files", bg_color="#FFFFFF", fg_color="#374151", command=self.add_files, width=140).pack(side=tk.LEFT, padx=(0, 10))
        self.create_rounded_button(inner_toolbar, text="Clear List", bg_color="#FFFFFF", fg_color="#DC2626", command=self.clear_files, width=140).pack(side=tk.LEFT, padx=(0, 10))
        
        self.btn_convert = self.create_rounded_button(inner_toolbar, text="Convert to PDF", bg_color="#111827", fg_color="#FFFFFF", command=self.process_conversion, width=160)
        self.btn_convert.pack(side=tk.RIGHT, padx=5)

        self.lbl_status = tk.Label(inner_toolbar, text="", bg=self.toolbar_color, fg="#1F2937", font=("Segoe UI", 10, "bold"))
        self.lbl_status.pack(side=tk.RIGHT, padx=15)

        content_frame = tk.Frame(self.root, bg="#F0F2F5", pady=40, padx=50)
        content_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(content_frame, text="Files to Convert", font=("Segoe UI", 18, "bold"), bg="#F0F2F5", fg="#1F2937").pack(anchor="w", pady=(0, 10))

        list_frame = tk.Frame(content_frame, bg="#FFFFFF", highlightthickness=1, highlightbackground="#E5E7EB")
        list_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, font=("Segoe UI", 11), bg="#FFFFFF", fg="#374151", selectbackground="#A8DFC5", selectforeground="#000000", relief=tk.FLAT, highlightthickness=0)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.config(command=self.listbox.yview)

    def add_files(self):
        filetypes = [
            ("Supported Files", "*.docx;*.png;*.jpg;*.jpeg;*.bmp"),
            ("Word Documents", "*.docx"),
            ("Images", "*.png;*.jpg;*.jpeg;*.bmp")
        ]
        filepaths = filedialog.askopenfilenames(title="Select Files to Convert", filetypes=filetypes)
        
        for path in filepaths:
            if path not in self.files_to_convert:
                self.files_to_convert.append(path)
                filename = os.path.basename(path)
                self.listbox.insert(tk.END, filename)

    def clear_files(self):
        self.files_to_convert.clear()
        self.listbox.delete(0, tk.END)
        self.lbl_status.config(text="")

    def process_conversion(self):
        if not self.files_to_convert:
            messagebox.showwarning("Empty List", "Please add files to convert first.")
            return
            
        if any(f.lower().endswith(".docx") for f in self.files_to_convert) and convert_docx is None:
            messagebox.showerror("Missing Dependency", "To convert DOCX files, you must run 'pip install docx2pdf' in your terminal.")
            return

        save_dir = filedialog.askdirectory(title="Select Destination Folder")
        if not save_dir:
            return

        self.lbl_status.config(text="Converting... Please wait.", fg="#D97706")
        self.root.update_idletasks()

        success_count = 0
        
        for file_path in self.files_to_convert:
            filename = os.path.basename(file_path)
            base_name, ext = os.path.splitext(filename)
            ext = ext.lower()
            output_path = os.path.join(save_dir, f"{base_name}.pdf")

            try:
                if ext == ".docx":
                    convert_docx(file_path, output_path)
                    success_count += 1
                elif ext in [".png", ".jpg", ".jpeg", ".bmp"]:
                    doc = fitz.open(file_path)
                    pdf_bytes = doc.convert_to_pdf()
                    img_pdf = fitz.open("pdf", pdf_bytes)
                    img_pdf.save(output_path)
                    img_pdf.close()
                    doc.close()
                    success_count += 1
            except Exception as e:
                messagebox.showerror("Conversion Error", f"Failed to convert {filename}:\n{e}")

        self.lbl_status.config(text=f"Successfully converted {success_count} files.", fg="#059669")
        messagebox.showinfo("Done", f"Conversion complete.\n\nFiles saved to:\n{save_dir}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernPDFConverter(root)
    root.mainloop()