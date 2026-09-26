import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox

import fitz  # PyMuPDF

from theme import BG_GRAY, TOOLBAR_COLOR, TEXT_COLOR
from ui_helpers import create_rounded_button


class SplitterFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_GRAY)
        self.controller = controller
        self.pdf_path = None
        self.page_count = 0
        self.setup_gui()

    def go_home(self):
        self.controller.show_frame("home")

    def setup_gui(self):
        toolbar = tk.Frame(self, bg=TOOLBAR_COLOR, bd=0)
        toolbar.pack(fill=tk.X, side=tk.TOP)

        inner = tk.Frame(toolbar, bg=TOOLBAR_COLOR, pady=12, padx=15)
        inner.pack(fill=tk.X)

        tk.Button(
            inner, text="⬅ Home", command=self.go_home, bg=TOOLBAR_COLOR, fg=TEXT_COLOR,
            font=("Segoe UI", 10, "bold"), bd=0, cursor="hand2"
        ).pack(side=tk.LEFT, padx=(0, 15))

        self.btn_load = create_rounded_button(
            inner, "📂 Load PDF", "#FFFFFF", "#374151",
            self.load_pdf, canvas_bg=TOOLBAR_COLOR
        )
        self.btn_load[0].pack(side=tk.LEFT, padx=10)

        self.btn_split = create_rounded_button(
            inner, "✂ Split & Save", "#111827", "#FFFFFF",
            self.split_pdf, canvas_bg=TOOLBAR_COLOR
        )
        self.btn_split[0].pack(side=tk.RIGHT, padx=5)

        # Content Area
        self.work_area = tk.Frame(self, bg=BG_GRAY, pady=50)
        self.work_area.pack(expand=True, fill=tk.BOTH)

        self.info_label = tk.Label(
            self.work_area, text="No PDF Loaded", font=("Segoe UI", 16, "bold"),
            bg=BG_GRAY, fg=TEXT_COLOR
        )
        self.info_label.pack(pady=20)

        self.range_frame = tk.Frame(
            self.work_area, bg="#FFFFFF", padx=30, pady=30,
            highlightthickness=1, highlightbackground="#D1D5DB"
        )

        tk.Label(
            self.range_frame, text="Enter Page Range (e.g. 1-3, 5, 8-10):", bg="#FFFFFF",
            font=("Segoe UI", 11)
        ).pack(pady=(0, 10))
        self.entry_range = tk.Entry(self.range_frame, font=("Segoe UI", 12), width=30, bd=1, relief="solid")
        self.entry_range.pack(pady=10)

    def load_pdf(self):
        path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if path:
            self.pdf_path = path
            doc = fitz.open(path)
            self.page_count = len(doc)
            self.info_label.config(text=f"Loaded: {os.path.basename(path)}\n({self.page_count} Pages)")
            self.range_frame.pack(pady=20)
            doc.close()

    def split_pdf(self):
        if not self.pdf_path:
            return
        range_str = self.entry_range.get().replace(" ", "")
        if not range_str:
            messagebox.showwarning("Input Required", "Please enter a page range.")
            return

        try:
            pages_to_keep = []
            parts = range_str.split(",")
            for part in parts:
                if "-" in part:
                    sub = part.split("-")
                    if len(sub) != 2:
                        raise ValueError(f"Invalid range format: '{part}'")
                    start, end = int(sub[0]), int(sub[1])
                    if start > end:
                        raise ValueError(f"Invalid range '{part}': start page is after end page.")
                    pages_to_keep.extend(range(start - 1, end))
                else:
                    pages_to_keep.append(int(part) - 1)

            pages_to_keep = sorted(set(pages_to_keep))

            if any(p < 0 or p >= self.page_count for p in pages_to_keep):
                messagebox.showerror(
                    "Error",
                    f"Page out of bounds!\n\nYou entered a page number that doesn't exist. "
                    f"This PDF only has {self.page_count} pages."
                )
                return

            save_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
            if save_path:
                src = fitz.open(self.pdf_path)
                src.select(pages_to_keep)
                src.save(save_path)
                src.close()

                messagebox.showinfo("Success", "PDF Split Successfully!")

        except ValueError as e:
            messagebox.showerror(
                "Error",
                f"Invalid range format.\n\n{e}"
                if str(e) else "Invalid range format. Use numbers and dashes only (e.g., 1-3, 5)."
            )
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred while splitting:\n\n{e}")


# Backward compatibility alias
ModernPDFSplitter = SplitterFrame

if __name__ == "__main__":
    from app_controller import PDFCommanderApp

    root = tk.Tk()
    app = PDFCommanderApp(root)
    app.show_frame("splitter")
    root.mainloop()