import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox

import fitz  # PyMuPDF

from theme import BG_GRAY, TEXT_COLOR


class SplitterFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_GRAY)
        self.controller = controller
        self.pdf_path = None
        self.page_count = 0
        self.setup_gui()

    def go_home(self):
        self.controller.show_frame("home")

    def go_to(self, view_name):
        self.controller.show_frame(view_name)

    def go_to(self, view_name):
        self.controller.show_frame(view_name)
    def setup_gui(self):
        # Sidebar
        sidebar = tk.Frame(self, bg="#1E293B", width=230)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        # Brand header
        brand_frame = tk.Frame(sidebar, bg="#1E293B", pady=20)
        brand_frame.pack(fill=tk.X)
        tk.Label(brand_frame, text="PDF COMMANDER", font=("Segoe UI", 16, "bold"), bg="#1E293B", fg="#FFFFFF").pack()
        tk.Label(brand_frame, text="Desktop Toolkit", font=("Segoe UI", 10), bg="#1E293B", fg="#64748B").pack()
        # Divider
        tk.Frame(sidebar, bg="#334155", height=1).pack(fill=tk.X, padx=20, pady=10)
        # Active Tool
        active_btn = tk.Button(
            sidebar, text="Split PDF", font=("Segoe UI", 11, "bold"),
            bg="#93E9BE", fg="#1F2937", bd=0, pady=10, cursor="hand2", anchor="w", padx=20
        )
        active_btn.pack(fill=tk.X, padx=10, pady=5)
        # Action buttons
        load_btn = tk.Button(
            sidebar, text="Load PDF", font=("Segoe UI", 11),
            bg="#1E293B", fg="#CBD5E1", bd=0, pady=8, cursor="hand2", anchor="w", padx=20,
            command=self.load_pdf
        )
        load_btn.pack(fill=tk.X, padx=10, pady=2)
        def on_enter_load(e, btn=load_btn): btn.config(bg="#334155", fg="#FFFFFF")
        def on_leave_load(e, btn=load_btn): btn.config(bg="#1E293B", fg="#CBD5E1")
        load_btn.bind("<Enter>", on_enter_load)
        load_btn.bind("<Leave>", on_leave_load)
        split_btn = tk.Button(
            sidebar, text="Split & Save", font=("Segoe UI", 11),
            bg="#1E293B", fg="#CBD5E1", bd=0, pady=8, cursor="hand2", anchor="w", padx=20,
            command=self.split_pdf
        )
        split_btn.pack(fill=tk.X, padx=10, pady=2)
        def on_enter_split(e, btn=split_btn): btn.config(bg="#334155", fg="#FFFFFF")
        def on_leave_split(e, btn=split_btn): btn.config(bg="#1E293B", fg="#CBD5E1")
        split_btn.bind("<Enter>", on_enter_split)
        split_btn.bind("<Leave>", on_leave_split)
        # Divider
        tk.Frame(sidebar, bg="#334155", height=1).pack(fill=tk.X, padx=20, pady=15)
        # Navigation Links
        nav_items = [
            ("Dashboard", "home"),
            ("Merge PDFs", "merger"),
            ("PDF Editor", "editor"),
            ("PDF Viewer", "viewer"),
            ("PDF Converter", "converter")
        ]
        for text, view_name in nav_items:
            btn = tk.Button(
                sidebar, text=text, font=("Segoe UI", 11),
                bg="#1E293B", fg="#CBD5E1", bd=0, pady=8, cursor="hand2", anchor="w", padx=20,
                command=lambda v=view_name: self.go_to(v)
            )
            btn.pack(fill=tk.X, padx=10, pady=2)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#334155", fg="#FFFFFF"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#1E293B", fg="#CBD5E1"))
        # Footer
        footer_frame = tk.Frame(sidebar, bg="#1E293B")
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=20)
        tk.Label(footer_frame, text="Local & Offline", font=("Segoe UI", 9), bg="#1E293B", fg="#64748B").pack()
        tk.Label(footer_frame, text="Version 1.0.0", font=("Segoe UI", 9), bg="#1E293B", fg="#64748B").pack()
        # Main content area
        main_content = tk.Frame(self, bg=BG_GRAY)
        main_content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        header_frame = tk.Frame(main_content, bg=BG_GRAY, pady=30, padx=40)
        header_frame.pack(fill=tk.X)
        tk.Label(header_frame, text="Split PDF", font=("Segoe UI", 24, "bold"), bg=BG_GRAY, fg=TEXT_COLOR, anchor="w").pack(fill=tk.X)
        tk.Label(header_frame, text="Extract specific pages or page ranges into a new PDF.", font=("Segoe UI", 11), bg=BG_GRAY, fg="#64748B", anchor="w").pack(fill=tk.X, pady=(5, 0))
        self.work_area = tk.Frame(main_content, bg=BG_GRAY)
        self.work_area.pack(expand=True, fill=tk.BOTH, padx=40, pady=(0, 40))
        self.card = tk.Frame(self.work_area, bg="#FFFFFF", padx=40, pady=40, highlightthickness=1, highlightbackground="#E5E7EB")
        self.card.pack(anchor="n", pady=20)
        self.info_label = tk.Label(self.card, text="No PDF Loaded", font=("Segoe UI", 16, "bold"), bg="#FFFFFF", fg=TEXT_COLOR)
        self.info_label.pack(pady=20)
        self.range_frame = tk.Frame(self.card, bg="#FFFFFF")
        tk.Label(self.range_frame, text="Enter Page Range (e.g. 1-3, 5, 8-10):", bg="#FFFFFF", font=("Segoe UI", 11), fg=TEXT_COLOR).pack(pady=(0, 10))
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