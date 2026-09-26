import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox

import fitz  # PyMuPDF

from theme import BG_GRAY, TOOLBAR_COLOR, TEXT_COLOR
from ui_helpers import create_rounded_button

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

    def setup_gui(self):
        toolbar = tk.Frame(self, bg=TOOLBAR_COLOR, bd=0)
        toolbar.pack(fill=tk.X, side=tk.TOP, pady=(0, 0))

        inner_toolbar = tk.Frame(toolbar, bg=TOOLBAR_COLOR, pady=12, padx=15)
        inner_toolbar.pack(fill=tk.X)

        tk.Button(inner_toolbar, text="Home", command=self.go_home, bg=TOOLBAR_COLOR, fg=TEXT_COLOR,
                  font=("Segoe UI", 10, "bold"), bd=0, activebackground=TOOLBAR_COLOR,
                  cursor="hand2").pack(side=tk.LEFT, padx=(0, 15))

        btn_add = create_rounded_button(inner_toolbar, "Add Files", "#FFFFFF", "#374151",
                                         self.add_files, width=140, canvas_bg=TOOLBAR_COLOR)
        btn_add[0].pack(side=tk.LEFT, padx=(0, 10))

        btn_clear = create_rounded_button(inner_toolbar, "Clear List", "#FFFFFF", "#DC2626",
                                           self.clear_files, width=140, canvas_bg=TOOLBAR_COLOR)
        btn_clear[0].pack(side=tk.LEFT, padx=(0, 10))

        self.btn_convert = create_rounded_button(inner_toolbar, "Convert to PDF", "#111827", "#FFFFFF",
                                                  self.process_conversion, width=160, canvas_bg=TOOLBAR_COLOR)
        self.btn_convert[0].pack(side=tk.RIGHT, padx=5)

        self.lbl_status = tk.Label(inner_toolbar, text="", bg=TOOLBAR_COLOR, fg=TEXT_COLOR,
                                    font=("Segoe UI", 10, "bold"))
        self.lbl_status.pack(side=tk.RIGHT, padx=15)

        content_frame = tk.Frame(self, bg=BG_GRAY, pady=40, padx=50)
        content_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(content_frame, text="Files to Convert", font=("Segoe UI", 18, "bold"), bg=BG_GRAY,
                 fg=TEXT_COLOR).pack(anchor="w", pady=(0, 10))

        list_frame = tk.Frame(content_frame, bg="#FFFFFF", highlightthickness=1, highlightbackground="#E5E7EB")
        list_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, font=("Segoe UI", 11),
                                   bg="#FFFFFF", fg="#374151", selectbackground="#A8DFC5",
                                   selectforeground="#000000", relief=tk.FLAT, highlightthickness=0)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.config(command=self.listbox.yview)

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
    root.mainloop()