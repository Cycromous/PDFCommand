import os
import tkinter as tk
from tkinter import filedialog, messagebox

import fitz  # PyMuPDF

from theme import BG_GRAY, MINT_GREEN, TEXT_COLOR, WHITE

try:
    from docx2pdf import convert as convert_docx
except ImportError:
    convert_docx = None


class ConverterFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_GRAY)
        self.controller = controller
        self.files_to_convert = []
        self.setup_gui()

    def go_home(self):
        self.controller.show_frame("home")

    def go_to(self, frame_name):
        self.controller.show_frame(frame_name)

    def go_to(self, frame_name):
        self.controller.show_frame(frame_name)
    def setup_gui(self):
        # Sidebar setup
        sidebar = tk.Frame(self, bg="#1E293B", width=230)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        # Brand header
        brand_frame = tk.Frame(sidebar, bg="#1E293B")
        brand_frame.pack(fill=tk.X, pady=(30, 20), padx=20)
        tk.Label(brand_frame, text="PDF COMMANDER", font=("Segoe UI", 16, "bold"), bg="#1E293B", fg="#F8FAFC").pack(anchor="w")
        tk.Label(brand_frame, text="Desktop Toolkit", font=("Segoe UI", 10), bg="#1E293B", fg="#94A3B8").pack(anchor="w")
        # Divider
        tk.Frame(sidebar, bg="#334155", height=1).pack(fill=tk.X, padx=20, pady=(0, 20))
        # Current Tool
        self._create_nav_item(sidebar, "PDF Converter", lambda: None, active=True)
        
        # Tool Actions
        tk.Label(sidebar, text="ACTIONS", font=("Segoe UI", 9, "bold"), bg="#1E293B", fg="#64748B").pack(anchor="w", padx=20, pady=(15, 5))
        self._create_nav_item(sidebar, "Add Files", self.add_files)
        self._create_nav_item(sidebar, "Clear List", self.clear_files)
        self._create_nav_item(sidebar, "Convert to PDF", self.process_conversion)
        # Divider
        tk.Frame(sidebar, bg="#334155", height=1).pack(fill=tk.X, padx=20, pady=20)
        # Navigation
        tk.Label(sidebar, text="NAVIGATION", font=("Segoe UI", 9, "bold"), bg="#1E293B", fg="#64748B").pack(anchor="w", padx=20, pady=(0, 5))
        self._create_nav_item(sidebar, "Dashboard", self.go_home)
        self._create_nav_item(sidebar, "Merge PDFs", lambda: self.go_to("merger"))
        self._create_nav_item(sidebar, "PDF Editor", lambda: self.go_to("editor"))
        self._create_nav_item(sidebar, "Split PDF", lambda: self.go_to("splitter"))
        self._create_nav_item(sidebar, "PDF Viewer", lambda: self.go_to("viewer"))
        # Footer
        footer_frame = tk.Frame(sidebar, bg="#1E293B")
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=20, padx=20)
        tk.Label(footer_frame, text="Local & Offline", font=("Segoe UI", 9), bg="#1E293B", fg="#059669").pack(anchor="w")
        tk.Label(footer_frame, text="Version 1.0.0", font=("Segoe UI", 8), bg="#1E293B", fg="#64748B").pack(anchor="w")
        # Main content area
        content_frame = tk.Frame(self, bg=BG_GRAY)
        content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        header_frame = tk.Frame(content_frame, bg=BG_GRAY)
        header_frame.pack(fill=tk.X, pady=(40, 20), padx=50)
        tk.Label(header_frame, text="PDF Converter", font=("Segoe UI", 24, "bold"), bg=BG_GRAY, fg=TEXT_COLOR).pack(anchor="w")
        tk.Label(header_frame, text="Convert Word documents and images to PDF.", font=("Segoe UI", 11), bg=BG_GRAY, fg="#64748B").pack(anchor="w", pady=(5, 0))
        self.lbl_status = tk.Label(header_frame, text="", bg=BG_GRAY, fg="#059669", font=("Segoe UI", 11, "bold"))
        self.lbl_status.pack(anchor="w", pady=(10, 0))
        list_frame = tk.Frame(content_frame, bg=WHITE, highlightthickness=1, highlightbackground="#E5E7EB", bd=0)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=(0, 50))
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, font=("Segoe UI", 11),
                                   bg=WHITE, fg="#374151", selectbackground="#E5E7EB",
                                   selectforeground="#1F2937", relief=tk.FLAT, highlightthickness=0)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.config(command=self.listbox.yview)
    def _create_nav_item(self, parent, text, command, active=False):
        bg_color = MINT_GREEN if active else "#1E293B"
        fg_color = "#1F2937" if active else "#CBD5E1"
        frame = tk.Frame(parent, bg=bg_color)
        frame.pack(fill=tk.X, padx=10, pady=2)
        btn = tk.Label(frame, text=text, font=("Segoe UI", 10, "bold" if active else "normal"),
                       bg=bg_color, fg=fg_color, anchor="w", padx=10, pady=8, cursor="hand2")
        btn.pack(fill=tk.BOTH, expand=True)
        btn.bind("<Button-1>", lambda e: command())
        if not active:
            btn.bind("<Enter>", lambda e, f=frame, b=btn: self._on_hover(f, b, True))
            btn.bind("<Leave>", lambda e, f=frame, b=btn: self._on_hover(f, b, False))
    def _on_hover(self, frame, btn, hovering):
        if hovering:
            frame.configure(bg="#334155")
            btn.configure(bg="#334155", fg="#FFFFFF")
        else:
            frame.configure(bg="#1E293B")
            btn.configure(bg="#1E293B", fg="#CBD5E1")

    def add_files(self):
        filetypes = [
            ("Supported Files", "*.docx;*.png;*.jpg;*.jpeg;*.bmp"),
            ("Word Documents", "*.docx"),
            ("Images", "*.png;*.jpg;*.jpeg;*.bmp"),
        ]
        filepaths = filedialog.askopenfilenames(title="Select Files to Convert", filetypes=filetypes)

        for path in filepaths:
            if path not in self.files_to_convert:
                self.files_to_convert.append(path)
                self.listbox.insert(tk.END, os.path.basename(path))

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
        self.update_idletasks()

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


# Backward compatibility alias
ModernPDFConverter = ConverterFrame

if __name__ == "__main__":
    from app_controller import PDFCommanderApp

    root = tk.Tk()
    app = PDFCommanderApp(root)
    app.show_frame("converter")
    root.mainloop()