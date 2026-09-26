import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox

import fitz  # PyMuPDF

from theme import BG_GRAY, TOOLBAR_COLOR, TOOLBAR_DIVIDER, TEXT_COLOR
from ui_helpers import create_rounded_button


class MergerFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_GRAY)
        self.controller = controller
        self.pdf_data = []
        self.selected_idx = None

        self.setup_gui()

    def go_home(self):
        self.controller.show_frame("home")

    def setup_gui(self):
        toolbar = tk.Frame(self, bg=TOOLBAR_COLOR, bd=0)
        toolbar.pack(fill=tk.X, side=tk.TOP, pady=(0, 0))

        inner_toolbar = tk.Frame(toolbar, bg=TOOLBAR_COLOR, pady=12, padx=15)
        inner_toolbar.pack(fill=tk.X)

        tk.Button(
            inner_toolbar, text="⬅ Home", command=self.go_home, bg=TOOLBAR_COLOR, fg=TEXT_COLOR,
            font=("Segoe UI", 10, "bold"), bd=0, activebackground=TOOLBAR_COLOR,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=(0, 15))

        btn_add = create_rounded_button(
            inner_toolbar, "➕ Add PDFs", "#FFFFFF", "#374151",
            self.add_pdfs, width=120, canvas_bg=TOOLBAR_COLOR
        )
        btn_add[0].pack(side=tk.LEFT, padx=(0, 15))

        tk.Frame(inner_toolbar, bg=TOOLBAR_DIVIDER, width=2).pack(side=tk.LEFT, fill=tk.Y, pady=5, padx=10)

        btn_up = create_rounded_button(
            inner_toolbar, "⬆ Move Up", TOOLBAR_COLOR, TEXT_COLOR,
            self.move_up, width=100, canvas_bg=TOOLBAR_COLOR
        )
        btn_up[0].pack(side=tk.LEFT, padx=5)

        btn_down = create_rounded_button(
            inner_toolbar, "⬇ Move Down", TOOLBAR_COLOR, TEXT_COLOR,
            self.move_down, width=130, canvas_bg=TOOLBAR_COLOR
        )
        btn_down[0].pack(side=tk.LEFT, padx=5)

        btn_remove = create_rounded_button(
            inner_toolbar, "❌ Remove", TOOLBAR_COLOR, "#E53E3E",
            self.remove_pdf, width=100, canvas_bg=TOOLBAR_COLOR
        )
        btn_remove[0].pack(side=tk.LEFT, padx=5)

        btn_merge = create_rounded_button(
            inner_toolbar, "🔗 Merge & Save", "#111827", "#FFFFFF",
            self.merge_pdfs, width=170, canvas_bg=TOOLBAR_COLOR
        )
        btn_merge[0].pack(side=tk.RIGHT, padx=5)

        workspace = tk.Frame(self, bg=BG_GRAY, padx=50, pady=40)
        workspace.pack(expand=True, fill=tk.BOTH)

        tk.Label(
            workspace, text="PDFs to Merge (Top to Bottom):", font=("Segoe UI", 14, "bold"),
            bg=BG_GRAY, fg=TEXT_COLOR
        ).pack(anchor="w", pady=(0, 10))

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
            if self.winfo_ismapped():
                self.canvas_scroll.yview_scroll(int(-1 * (event.delta / 120)), "units")
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
                    "thumb": tk_img,
                })
            except Exception:
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

            card = tk.Frame(
                self.scrollable_inner, bg=bg_color, highlightthickness=2,
                highlightbackground=border_color, padx=15, pady=15, cursor="hand2"
            )
            card.pack(fill=tk.X, pady=6, padx=10)

            def make_select_cmd(index):
                return lambda e: self.select_item(index)

            cmd = make_select_cmd(i)
            card.bind("<Button-1>", cmd)

            lbl_img = tk.Label(
                card, image=data["thumb"], bg=bg_color, highlightthickness=1,
                highlightbackground="#D1D5DB"
            )
            lbl_img.pack(side=tk.LEFT, padx=(0, 20))
            lbl_img.bind("<Button-1>", cmd)

            # Info Text Container
            info_frame = tk.Frame(card, bg=bg_color)
            info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            info_frame.bind("<Button-1>", cmd)

            lbl_name = tk.Label(
                info_frame, text=data["name"], font=("Segoe UI", 13, "bold"),
                bg=bg_color, fg="#1F2937", anchor="w"
            )
            lbl_name.pack(fill=tk.X, pady=(10, 2))
            lbl_name.bind("<Button-1>", cmd)

            lbl_pages = tk.Label(
                info_frame, text=f"📄 {data['pages']} Pages", font=("Segoe UI", 10),
                bg=bg_color, fg="#6B7280", anchor="w"
            )
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
                doc_to_insert = fitz.open(item["path"])
                merged_doc.insert_pdf(doc_to_insert)
                doc_to_insert.close()

            merged_doc.save(save_path)
            merged_doc.close()

            messagebox.showinfo("Success", "PDFs merged successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to merge PDFs:\n\n{e}")


# Backward compatibility alias
ModernPDFMerger = MergerFrame

if __name__ == "__main__":
    from app_controller import PDFCommanderApp

    root = tk.Tk()
    app = PDFCommanderApp(root)
    app.show_frame("merger")
    root.mainloop()
    root.mainloop()