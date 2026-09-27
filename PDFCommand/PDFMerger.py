import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox

import fitz  # PyMuPDF

from theme import BG_GRAY, TEXT_COLOR, MINT_GREEN, WHITE


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
        # ── Sidebar ──────────────────────────────────────────────────
        sidebar_bg = "#1E293B"  # Slate dark background
        sidebar = tk.Frame(self, bg=sidebar_bg, width=230)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        # App Brand Header
        brand_frame = tk.Frame(sidebar, bg=sidebar_bg, pady=24, padx=18)
        brand_frame.pack(fill=tk.X)
        tk.Label(brand_frame, text="PDF COMMANDER", font=("Segoe UI", 12, "bold"),
                 fg=WHITE, bg=sidebar_bg, anchor="w").pack(fill=tk.X)
        tk.Label(brand_frame, text="Desktop Toolkit", font=("Segoe UI", 8),
                 fg="#94A3B8", bg=sidebar_bg, anchor="w").pack(fill=tk.X, pady=(2, 0))

        # Subtle divider
        tk.Frame(sidebar, bg="#334155", height=1).pack(fill=tk.X, padx=16, pady=(10, 16))

        # Active Tool Highlight
        nav_merger = tk.Label(sidebar, text="  Merge PDFs", font=("Segoe UI", 10, "bold"),
                              bg=MINT_GREEN, fg="#0F172A", anchor="w", padx=16, pady=10)
        nav_merger.pack(fill=tk.X, padx=12, pady=2)

        # Action Buttons
        tk.Label(sidebar, text="ACTIONS", font=("Segoe UI", 8, "bold"),
                 fg="#64748B", bg=sidebar_bg, anchor="w", padx=20).pack(fill=tk.X, pady=(16, 6))

        def create_sidebar_action(text, command, is_primary=False):
            bg_color = MINT_GREEN if is_primary else sidebar_bg
            fg_color = "#0F172A" if is_primary else "#CBD5E1"
            font_weight = "bold" if is_primary else "normal"
            
            btn = tk.Label(sidebar, text=f"  {text}", font=("Segoe UI", 9, font_weight),
                           bg=bg_color, fg=fg_color, anchor="w", padx=16, pady=8,
                           cursor="hand2")
            btn.pack(fill=tk.X, padx=12, pady=1)
            
            if not is_primary:
                btn.bind("<Enter>", lambda _e: btn.config(bg="#334155", fg=WHITE))
                btn.bind("<Leave>", lambda _e: btn.config(bg=sidebar_bg, fg="#CBD5E1"))
                
                def on_click(_e):
                    btn.config(bg="#0F766E", fg=WHITE)
                    btn.after(60, command)
                    btn.after(350, lambda: btn.config(bg=sidebar_bg, fg="#CBD5E1"))
                btn.bind("<Button-1>", on_click)
            else:
                btn.bind("<Enter>", lambda _e: btn.config(bg="#34D399"))
                btn.bind("<Leave>", lambda _e: btn.config(bg=MINT_GREEN))
                
                def on_click_primary(_e):
                    btn.config(bg="#059669")
                    btn.after(60, command)
                    btn.after(350, lambda: btn.config(bg=MINT_GREEN))
                btn.bind("<Button-1>", on_click_primary)
                
            return btn

        create_sidebar_action("Add PDFs", self.add_pdfs, is_primary=True)
        create_sidebar_action("Move Up", self.move_up)
        create_sidebar_action("Move Down", self.move_down)
        create_sidebar_action("Remove", self.remove_pdf)
        create_sidebar_action("Merge & Save", self.merge_pdfs, is_primary=True)


        # Subtle divider
        tk.Frame(sidebar, bg="#334155", height=1).pack(fill=tk.X, padx=16, pady=(16, 16))

        # Navigation Links
        tk.Label(sidebar, text="NAVIGATION", font=("Segoe UI", 8, "bold"),
                 fg="#64748B", bg=sidebar_bg, anchor="w", padx=20).pack(fill=tk.X, pady=(0, 6))

        sidebar_nav = [
            ("Dashboard", "home"),
            ("PDF Editor", "editor"),
            ("Split PDF", "splitter"),
            ("PDF Viewer", "viewer"),
            ("PDF Converter", "converter"),
        ]

        for text, frame_name in sidebar_nav:
            btn = tk.Label(sidebar, text=f"  {text}", font=("Segoe UI", 9),
                           bg=sidebar_bg, fg="#CBD5E1", anchor="w", padx=16, pady=8,
                           cursor="hand2")
            btn.pack(fill=tk.X, padx=12, pady=1)

            def make_hover(label, f_name):
                label.bind("<Enter>", lambda _e: label.config(bg="#334155", fg=WHITE))
                label.bind("<Leave>", lambda _e: label.config(bg=sidebar_bg, fg="#CBD5E1"))

                def on_sidebar_click(_e):
                    label.config(bg="#0F766E", fg=WHITE)
                    label.after(60, lambda: self.controller.show_frame(f_name))
                    label.after(350, lambda: label.config(bg=sidebar_bg, fg="#CBD5E1"))

                label.bind("<Button-1>", on_sidebar_click)

            make_hover(btn, frame_name)

        # Bottom Version & Offline indicator
        tk.Frame(sidebar, bg=sidebar_bg).pack(fill=tk.BOTH, expand=True)
        footer = tk.Frame(sidebar, bg=sidebar_bg, pady=16, padx=18)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        tk.Label(footer, text="Local & Offline", font=("Segoe UI", 8, "bold"),
                 fg="#10B981", bg=sidebar_bg, anchor="w").pack(fill=tk.X)
        tk.Label(footer, text="Version 1.0.0", font=("Segoe UI", 8),
                 fg="#64748B", bg=sidebar_bg, anchor="w").pack(fill=tk.X, pady=(2, 0))

        # ── Main Content Area ────────────────────────────────────────
        main_area = tk.Frame(self, bg=BG_GRAY)
        main_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Header Title
        header_container = tk.Frame(main_area, bg=BG_GRAY, pady=36, padx=50)
        header_container.pack(fill=tk.X)

        tk.Label(header_container, text="Merge PDFs",
                 font=("Segoe UI", 24, "bold"), bg=BG_GRAY, fg=TEXT_COLOR,
                 anchor="w").pack(fill=tk.X)
        tk.Label(header_container,
                 text="Combine multiple PDF documents into a single file.",
                 font=("Segoe UI", 11), bg=BG_GRAY, fg="#64748B",
                 anchor="w").pack(fill=tk.X, pady=(4, 0))

        # Workspace / List
        workspace = tk.Frame(main_area, bg=BG_GRAY)
        workspace.pack(expand=True, fill=tk.BOTH, padx=50, pady=(0, 40))
        
        list_container = tk.Frame(workspace, bg="#FFFFFF", highlightthickness=1, highlightbackground="#E5E7EB")
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
            border_color = "#10B981" if is_selected else "#E5E7EB"

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
                highlightbackground="#E5E7EB"
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
                bg=bg_color, fg="#64748B", anchor="w"
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