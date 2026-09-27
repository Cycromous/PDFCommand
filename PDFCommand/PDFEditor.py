import base64
import threading
import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox, simpledialog, ttk

import fitz  # PyMuPDF

from theme import BG_GRAY, TEXT_COLOR, MINT_GREEN, WHITE
from ui_helpers import create_rounded_button


class EditorFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_GRAY)
        self.controller = controller
        self.root = controller.root

        self.current_filepath = None
        self.pdf_bytes = None
        self.pdf_doc = None
        self.page_image = None

        self.current_page_num = 0
        self.total_pages = 0

        self.master_text_items = {}
        self.master_shape_items = {}
        self.master_image_items = {}
        self.tk_images = {}

        self.drag_data = {"item": None, "x": 0, "y": 0, "handle": None}
        self.current_mode = "text"
        self.shape_color = "#FFFFFF"
        self.current_shape_type = tk.StringVar(value="rectangle")
        self.drawing_shape = None
        self.start_x = 0
        self.start_y = 0
        self.selected_image = None
        self._save_timer = None

        self.font_size = tk.IntVar(value=14)

        self.setup_gui()

    def go_home(self):
        self.controller.show_frame("home")

    def setup_gui(self):
        # ── Sidebar ──────────────────────────────────────────────────
        sidebar_bg = "#1E293B"  # Slate dark background
        sidebar = tk.Frame(self, bg=sidebar_bg, width=240)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        # App Brand Header
        brand_frame = tk.Frame(sidebar, bg=sidebar_bg, pady=20, padx=18)
        brand_frame.pack(fill=tk.X)
        tk.Label(brand_frame, text="PDF COMMANDER", font=("Segoe UI", 12, "bold"),
                 fg=WHITE, bg=sidebar_bg, anchor="w").pack(fill=tk.X)
        tk.Label(brand_frame, text="Desktop Toolkit", font=("Segoe UI", 8),
                 fg="#94A3B8", bg=sidebar_bg, anchor="w").pack(fill=tk.X, pady=(2, 0))

        # Subtle divider
        tk.Frame(sidebar, bg="#334155", height=1).pack(fill=tk.X, padx=16, pady=(5, 12))

        # Active Tool Indicator
        nav_editor = tk.Label(sidebar, text="  PDF Editor", font=("Segoe UI", 10, "bold"),
                              bg=MINT_GREEN, fg="#0F172A", anchor="w", padx=16, pady=8)
        nav_editor.pack(fill=tk.X, padx=12, pady=2)

        # ── File Actions Section ─────────────────────────────────────
        tk.Label(sidebar, text="FILE ACTIONS", font=("Segoe UI", 8, "bold"),
                 fg="#64748B", bg=sidebar_bg, anchor="w", padx=20).pack(fill=tk.X, pady=(12, 4))

        def create_sidebar_btn(text, command, is_primary=False):
            bg_color = MINT_GREEN if is_primary else sidebar_bg
            fg_color = "#0F172A" if is_primary else "#CBD5E1"
            font_weight = "bold" if is_primary else "normal"
            btn = tk.Label(sidebar, text=f"  {text}", font=("Segoe UI", 9, font_weight),
                           bg=bg_color, fg=fg_color, anchor="w", padx=16, pady=7,
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

        create_sidebar_btn("Open PDF", self.open_pdf, is_primary=True)
        create_sidebar_btn("Save As", self.save_as_pdf)

        self.lbl_save_status = tk.Label(sidebar, text="", bg=sidebar_bg, fg="#10B981",
                                         font=("Segoe UI", 8, "bold"), anchor="w", padx=20)
        self.lbl_save_status.pack(fill=tk.X, pady=(2, 0))

        # Subtle divider
        tk.Frame(sidebar, bg="#334155", height=1).pack(fill=tk.X, padx=16, pady=(10, 10))

        # ── Editing Tools Section ────────────────────────────────────
        tk.Label(sidebar, text="EDITING TOOLS", font=("Segoe UI", 8, "bold"),
                 fg="#64748B", bg=sidebar_bg, anchor="w", padx=20).pack(fill=tk.X, pady=(0, 6))

        tool_row = tk.Frame(sidebar, bg=sidebar_bg)
        tool_row.pack(fill=tk.X, padx=12, pady=2)

        self.btn_text = create_rounded_button(tool_row, "Text", "#93E9BE", "#0F172A",
                                              lambda: self.set_mode("text"),
                                              width=65, height=30, canvas_bg=sidebar_bg,
                                              font=("Segoe UI", 9, "bold"))
        self.btn_text[0].pack(side=tk.LEFT, padx=2)

        self.btn_shape = create_rounded_button(tool_row, "Shape", "#334155", "#CBD5E1",
                                               lambda: self.set_mode("shape"),
                                               width=65, height=30, canvas_bg=sidebar_bg,
                                               font=("Segoe UI", 9, "bold"))
        self.btn_shape[0].pack(side=tk.LEFT, padx=2)

        self.btn_image = create_rounded_button(tool_row, "Image", "#334155", "#CBD5E1",
                                               self.add_image,
                                               width=65, height=30, canvas_bg=sidebar_bg,
                                               font=("Segoe UI", 9, "bold"))
        self.btn_image[0].pack(side=tk.LEFT, padx=2)

        # Shape controls
        shape_ctrls = tk.Frame(sidebar, bg=sidebar_bg)
        shape_ctrls.pack(fill=tk.X, padx=14, pady=(6, 2))

        self.shape_combo = ttk.Combobox(shape_ctrls, textvariable=self.current_shape_type,
                                         values=("rectangle", "oval"), width=10, state="readonly",
                                         font=("Segoe UI", 8))
        self.shape_combo.pack(side=tk.LEFT, padx=(0, 8))

        self.btn_color_canvas = tk.Canvas(shape_ctrls, width=28, height=28, bg=sidebar_bg,
                                           highlightthickness=0, cursor="hand2")
        self.color_circle = self.btn_color_canvas.create_oval(2, 2, 26, 26, fill=self.shape_color,
                                                               outline="#64748B", width=1)
        self.btn_color_canvas.bind("<Button-1>", lambda e: self.pick_color())
        self.btn_color_canvas.pack(side=tk.LEFT)

        # Font Size Slider
        font_frame = tk.Frame(sidebar, bg=sidebar_bg)
        font_frame.pack(fill=tk.X, padx=14, pady=(8, 2))
        self.lbl_font_size = tk.Label(font_frame, text=f"Font Size: {self.font_size.get()}pt",
                                      font=("Segoe UI", 8, "bold"), bg=sidebar_bg, fg="#94A3B8", anchor="w")
        self.lbl_font_size.pack(fill=tk.X)

        slider_canvas = tk.Canvas(sidebar, width=190, height=32, bg=sidebar_bg,
                                   highlightthickness=0, cursor="hand2")
        slider_canvas.pack(fill=tk.X, padx=14, pady=(2, 4))

        def _draw_slider(val):
            slider_canvas.delete("all")
            min_v, max_v = 2, 50
            frac = (val - min_v) / (max_v - min_v)
            cx = 12 + frac * 170
            slider_canvas.create_rectangle(12, 14, 182, 18, fill="#334155", outline="")
            slider_canvas.create_rectangle(12, 14, cx, 18, fill="#10B981", outline="")
            slider_canvas.create_oval(cx - 8, 16 - 8, cx + 8, 16 + 8, fill="#10B981",
                                       outline="#FFFFFF", width=2)
            self.lbl_font_size.config(text=f"Font Size: {val}pt")

        def _on_slider_click_or_drag(event):
            frac = max(0.0, min(1.0, (event.x - 12) / 170))
            snapped = int(round((2 + frac * 48) / 2) * 2)
            self.font_size.set(max(2, min(50, snapped)))
            _draw_slider(self.font_size.get())

        slider_canvas.bind("<Button-1>", _on_slider_click_or_drag)
        slider_canvas.bind("<B1-Motion>", _on_slider_click_or_drag)
        _draw_slider(self.font_size.get())
        self.font_size.trace_add("write", lambda *_: _draw_slider(self.font_size.get()))

        # Subtle divider
        tk.Frame(sidebar, bg="#334155", height=1).pack(fill=tk.X, padx=16, pady=(10, 10))

        # ── Page Navigation Section ──────────────────────────────────
        tk.Label(sidebar, text="PAGE NAVIGATION", font=("Segoe UI", 8, "bold"),
                 fg="#64748B", bg=sidebar_bg, anchor="w", padx=20).pack(fill=tk.X, pady=(0, 6))

        nav_row = tk.Frame(sidebar, bg=sidebar_bg)
        nav_row.pack(fill=tk.X, padx=14, pady=2)

        self.btn_prev = tk.Button(nav_row, text="◀ Prev", command=self.prev_page,
                                   font=("Segoe UI", 9, "bold"), bg="#334155", fg="#FFFFFF",
                                   bd=0, padx=8, pady=5, cursor="hand2", activebackground="#475569")
        self.btn_prev.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 4))

        self.btn_next = tk.Button(nav_row, text="Next ▶", command=self.next_page,
                                   font=("Segoe UI", 9, "bold"), bg="#334155", fg="#FFFFFF",
                                   bd=0, padx=8, pady=5, cursor="hand2", activebackground="#475569")
        self.btn_next.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(4, 0))

        self.lbl_page_info = tk.Label(sidebar, text="Page 0 of 0", font=("Segoe UI", 9, "bold"),
                                       bg=sidebar_bg, fg="#94A3B8", pady=4)
        self.lbl_page_info.pack(fill=tk.X)

        # Subtle divider
        tk.Frame(sidebar, bg="#334155", height=1).pack(fill=tk.X, padx=16, pady=(10, 10))

        # ── Navigation Links ─────────────────────────────────────────
        tk.Label(sidebar, text="NAVIGATION", font=("Segoe UI", 8, "bold"),
                 fg="#64748B", bg=sidebar_bg, anchor="w", padx=20).pack(fill=tk.X, pady=(0, 4))

        sidebar_nav = [
            ("Dashboard", "home"),
            ("Merge PDFs", "merger"),
            ("Split PDF", "splitter"),
            ("PDF Viewer", "viewer"),
            ("PDF Converter", "converter"),
        ]

        for text, frame_name in sidebar_nav:
            btn = tk.Label(sidebar, text=f"  {text}", font=("Segoe UI", 9),
                           bg=sidebar_bg, fg="#CBD5E1", anchor="w", padx=16, pady=6,
                           cursor="hand2")
            btn.pack(fill=tk.X, padx=12, pady=1)

            def make_hover(label, f_name):
                label.bind("<Enter>", lambda _e: label.config(bg="#334155", fg=WHITE))
                label.bind("<Leave>", lambda _e: label.config(bg=sidebar_bg, fg="#CBD5E1"))

                def on_nav_click(_e):
                    label.config(bg="#0F766E", fg=WHITE)
                    label.after(60, lambda: self.controller.show_frame(f_name))
                    label.after(350, lambda: label.config(bg=sidebar_bg, fg="#CBD5E1"))

                label.bind("<Button-1>", on_nav_click)

            make_hover(btn, frame_name)

        # Bottom Version & Offline indicator
        tk.Frame(sidebar, bg=sidebar_bg).pack(fill=tk.BOTH, expand=True)
        footer = tk.Frame(sidebar, bg=sidebar_bg, pady=12, padx=18)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        tk.Label(footer, text="Local & Offline", font=("Segoe UI", 8, "bold"),
                 fg="#10B981", bg=sidebar_bg, anchor="w").pack(fill=tk.X)
        tk.Label(footer, text="Version 1.0.0", font=("Segoe UI", 8),
                 fg="#64748B", bg=sidebar_bg, anchor="w").pack(fill=tk.X, pady=(2, 0))

        # ── Main Workspace ───────────────────────────────────────────
        main_area = tk.Frame(self, bg=BG_GRAY)
        main_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        top_bar = tk.Frame(main_area, bg="#FFFFFF", highlightthickness=1,
                           highlightbackground="#E5E7EB", pady=10, padx=20)
        top_bar.pack(fill=tk.X)

        self.lbl_instructions = tk.Label(
            top_bar, text="Drag: Move | Click Image: Show Resize Corners | Right-click: Delete",
            bg="#FFFFFF", fg="#475569", font=("Segoe UI", 9)
        )
        self.lbl_instructions.pack(side=tk.LEFT)

        canvas_frame = tk.Frame(main_area, bg=BG_GRAY, bd=0)
        canvas_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=15)
        self.canvas = tk.Canvas(canvas_frame, bg=BG_GRAY, bd=0, highlightthickness=0)
        self.canvas.pack(expand=True, fill=tk.BOTH)

        self.canvas.bind("<ButtonPress-1>", self.on_left_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<Button-3>", self.on_right_click)

    def set_mode(self, mode):
        self.current_mode = mode
        if mode == "text":
            self.btn_text[0].itemconfig(self.btn_text[1], fill="#93E9BE")
            self.btn_text[0].itemconfig(self.btn_text[2], fill="#0F172A")
            self.btn_shape[0].itemconfig(self.btn_shape[1], fill="#334155")
            self.btn_shape[0].itemconfig(self.btn_shape[2], fill="#CBD5E1")
            self.lbl_instructions.config(text="Drag: Move | Click Image: Show Resize Corners | Right-click: Delete")
        else:
            self.btn_shape[0].itemconfig(self.btn_shape[1], fill="#93E9BE")
            self.btn_shape[0].itemconfig(self.btn_shape[2], fill="#0F172A")
            self.btn_text[0].itemconfig(self.btn_text[1], fill="#334155")
            self.btn_text[0].itemconfig(self.btn_text[2], fill="#CBD5E1")
            self.lbl_instructions.config(text="Click & Drag to draw Shape | Right-click to delete")

    def pick_color(self):
        color_code = colorchooser.askcolor(title="Choose Shape Color", initialcolor=self.shape_color)[1]
        if color_code:
            self.shape_color = color_code
            self.btn_color_canvas.itemconfig(self.color_circle, fill=self.shape_color)

    def open_pdf(self):
        filepath = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if filepath:
            self.load_specific_pdf(filepath)

    def load_specific_pdf(self, filepath, start_page=0):
        self.current_filepath = filepath
        with open(filepath, "rb") as f:
            self.pdf_bytes = f.read()

        self.pdf_doc = fitz.open("pdf", self.pdf_bytes)
        self.total_pages = len(self.pdf_doc)
        self.current_page_num = min(start_page, max(0, self.total_pages - 1))

        self.master_text_items = {i: {} for i in range(self.total_pages)}
        self.master_shape_items = {i: {} for i in range(self.total_pages)}
        self.master_image_items = {i: {} for i in range(self.total_pages)}

        self.tk_images.clear()
        self.selected_image = None

        self.update_idletasks()
        self.render_page()

    def update_nav_buttons(self):
        self.lbl_page_info.config(text=f"Page {self.current_page_num + 1} of {self.total_pages}")

        if self.current_page_num == 0:
            self.btn_prev.config(state=tk.DISABLED, bg="#1E293B", fg="#64748B")
        else:
            self.btn_prev.config(state=tk.NORMAL, bg="#334155", fg="#FFFFFF")

        if self.current_page_num == self.total_pages - 1:
            self.btn_next.config(state=tk.DISABLED, bg="#1E293B", fg="#64748B")
        else:
            self.btn_next.config(state=tk.NORMAL, bg="#334155", fg="#FFFFFF")

    def next_page(self):
        if self.current_page_num < self.total_pages - 1:
            self.current_page_num += 1
            self.render_page()

    def prev_page(self):
        if self.current_page_num > 0:
            self.current_page_num -= 1
            self.render_page()

    def on_show(self):
        if self.pdf_doc:
            self.render_page()

    def render_page(self):
        if not self.pdf_doc:
            return

        self.update_nav_buttons()
        page = self.pdf_doc[self.current_page_num]

        self.canvas.update_idletasks()
        canvas_height = self.canvas.winfo_height()
        if canvas_height <= 1:
            canvas_height = self.root.winfo_screenheight() - 150

        self.scale = (canvas_height * 0.95) / page.rect.height
        mat = fitz.Matrix(self.scale, self.scale)
        pix = page.get_pixmap(matrix=mat)

        self.page_image = tk.PhotoImage(data=pix.tobytes("ppm"))
        self.canvas.delete("all")

        canvas_width = self.canvas.winfo_width()
        if canvas_width <= 1:
            canvas_width = self.root.winfo_screenwidth() - 240

        self.x_offset = max(0, (canvas_width - pix.width) // 2)
        self.y_offset = 15

        self.canvas.create_rectangle(
            self.x_offset + 3, self.y_offset + 3,
            self.x_offset + pix.width + 3, self.y_offset + pix.height + 3,
            fill="#D1D5DB", outline=""
        )

        self.canvas.create_image(
            self.x_offset, self.y_offset, anchor=tk.NW, image=self.page_image
        )

        curr_shapes = self.master_shape_items.get(self.current_page_num, {})
        for item_id, data in list(curr_shapes.items()):
            coords = [
                self.x_offset + data["orig_box"][0] * self.scale,
                self.y_offset + data["orig_box"][1] * self.scale,
                self.x_offset + data["orig_box"][2] * self.scale,
                self.y_offset + data["orig_box"][3] * self.scale,
            ]
            fill_c = data.get("color", "#FFFFFF")
            stype = data.get("shape_type", "rectangle")
            if stype == "oval":
                cid = self.canvas.create_oval(*coords, fill=fill_c, outline=fill_c, tags=("added_shape",))
            else:
                cid = self.canvas.create_rectangle(*coords, fill=fill_c, outline=fill_c, tags=("added_shape",))
            data["canvas_id"] = cid

        curr_images = self.master_image_items.get(self.current_page_num, {})
        for item_id, data in list(curr_images.items()):
            b_w = data["orig_box"][2] - data["orig_box"][0]
            b_h = data["orig_box"][3] - data["orig_box"][1]
            scale_w = int(b_w * self.scale)
            scale_h = int(b_h * self.scale)

            raw_bytes = base64.b64decode(data["png_bytes"])
            img_doc = fitz.open("png", raw_bytes)
            pix_img = img_doc[0].get_pixmap()

            sx = scale_w / pix_img.width if pix_img.width > 0 else 1
            sy = scale_h / pix_img.height if pix_img.height > 0 else 1
            scaled_pix = img_doc[0].get_pixmap(matrix=fitz.Matrix(sx, sy))
            img_doc.close()

            tk_img = tk.PhotoImage(data=scaled_pix.tobytes("ppm"))
            self.tk_images[item_id] = tk_img

            cx = self.x_offset + data["orig_box"][0] * self.scale
            cy = self.y_offset + data["orig_box"][1] * self.scale
            cid = self.canvas.create_image(cx, cy, anchor=tk.NW, image=tk_img, tags=("added_image",))
            data["canvas_id"] = cid

        curr_texts = self.master_text_items.get(self.current_page_num, {})
        for item_id, data in list(curr_texts.items()):
            scaled_size = max(1, int(data.get("size", 14) * self.scale))
            cx = self.x_offset + data["orig_pos"][0] * self.scale
            cy = self.y_offset + data["orig_pos"][1] * self.scale
            cid = self.canvas.create_text(
                cx, cy, text=data["text"], anchor=tk.NW,
                font=("Arial", scaled_size), fill=data.get("color", "#000000"),
                tags=("added_text",)
            )
            data["canvas_id"] = cid

    def add_image(self):
        if not self.pdf_doc:
            return
        filepath = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")]
        )
        if not filepath:
            return

        img_doc = fitz.open(filepath)
        pix = img_doc[0].get_pixmap()
        img_doc.close()

        orig_w = pix.width
        orig_h = pix.height
        max_dim = 200
        if orig_w > max_dim or orig_h > max_dim:
            if orig_w > orig_h:
                new_w = max_dim
                new_h = int(orig_h * (max_dim / orig_w))
            else:
                new_h = max_dim
                new_w = int(orig_w * (max_dim / orig_h))
        else:
            new_w, new_h = orig_w, orig_h

        sx = new_w / orig_w
        sy = new_h / orig_h
        img_doc2 = fitz.open(filepath)
        scaled_pix = img_doc2[0].get_pixmap(matrix=fitz.Matrix(sx, sy))
        img_doc2.close()

        png_bytes = scaled_pix.tobytes("png")
        b64_str = base64.b64encode(png_bytes).decode("ascii")

        page = self.pdf_doc[self.current_page_num]
        insert_x = (page.rect.width - new_w) / 2
        insert_y = (page.rect.height - new_h) / 2

        item_id = f"img_{len(self.master_image_items.get(self.current_page_num, {}))}_{self.current_page_num}"
        self.master_image_items[self.current_page_num][item_id] = {
            "png_bytes": b64_str,
            "orig_box": [insert_x, insert_y, insert_x + new_w, insert_y + new_h],
        }

        self.selected_image = item_id
        self.render_page()
        self.draw_image_handles(item_id)
        self.trigger_autosave()

    def on_left_click(self, event):
        if not self.pdf_doc:
            return

        cx, cy = event.x, event.y
        self.start_x = cx
        self.start_y = cy

        handle_clicked = False
        if self.selected_image:
            overlap = self.canvas.find_overlapping(cx - 3, cy - 3, cx + 3, cy + 3)
            for item in overlap:
                tags = self.canvas.gettags(item)
                for t in tags:
                    if t.startswith("handle_"):
                        handle_name = t.split("_")[1]
                        self.drag_data = {
                            "item": self.selected_image,
                            "type": "image_resize",
                            "handle": handle_name,
                            "x": cx, "y": cy
                        }
                        handle_clicked = True
                        break
                if handle_clicked:
                    break

        if handle_clicked:
            return

        if self.current_mode == "shape":
            self.remove_image_handles()
            self.selected_image = None
            if self.current_shape_type.get() == "oval":
                self.drawing_shape = self.canvas.create_oval(
                    cx, cy, cx, cy, fill=self.shape_color, outline=self.shape_color
                )
            else:
                self.drawing_shape = self.canvas.create_rectangle(
                    cx, cy, cx, cy, fill=self.shape_color, outline=self.shape_color
                )
            return

        overlap = self.canvas.find_overlapping(cx - 2, cy - 2, cx + 2, cy + 2)
        topmost = None
        for item in reversed(overlap):
            tags = self.canvas.gettags(item)
            if "added_text" in tags or "added_shape" in tags or "added_image" in tags:
                topmost = item
                break

        if topmost:
            item_type = None
            item_key = None
            tags = self.canvas.gettags(topmost)

            if "added_text" in tags:
                item_type = "text"
                for k, v in self.master_text_items.get(self.current_page_num, {}).items():
                    if v.get("canvas_id") == topmost:
                        item_key = k
                        break
            elif "added_shape" in tags:
                item_type = "shape"
                for k, v in self.master_shape_items.get(self.current_page_num, {}).items():
                    if v.get("canvas_id") == topmost:
                        item_key = k
                        break
            elif "added_image" in tags:
                item_type = "image"
                for k, v in self.master_image_items.get(self.current_page_num, {}).items():
                    if v.get("canvas_id") == topmost:
                        item_key = k
                        break

            if item_key:
                if item_type == "image":
                    self.selected_image = item_key
                    self.draw_image_handles(item_key)
                else:
                    self.remove_image_handles()
                    self.selected_image = None

                self.drag_data = {"item": item_key, "type": item_type, "x": cx, "y": cy}
                return

        self.remove_image_handles()
        self.selected_image = None

        if self.current_mode == "text":
            orig_x = (cx - self.x_offset) / self.scale
            orig_y = (cy - self.y_offset) / self.scale

            page = self.pdf_doc[self.current_page_num]
            if 0 <= orig_x <= page.rect.width and 0 <= orig_y <= page.rect.height:
                user_text = simpledialog.askstring("Add Text", "Enter text to add:")
                if user_text:
                    item_id = f"txt_{len(self.master_text_items.get(self.current_page_num, {}))}_{self.current_page_num}"
                    self.master_text_items[self.current_page_num][item_id] = {
                        "text": user_text,
                        "orig_pos": (orig_x, orig_y),
                        "color": "#000000",
                        "size": self.font_size.get(),
                    }
                    self.render_page()
                    self.trigger_autosave()

    def on_canvas_drag(self, event):
        if self.drawing_shape:
            self.canvas.coords(self.drawing_shape, self.start_x, self.start_y, event.x, event.y)
            return

        if self.drag_data["item"] is None:
            return

        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]
        item_id = self.drag_data["item"]
        item_type = self.drag_data["type"]

        if item_type == "image_resize":
            handle = self.drag_data["handle"]
            data = self.master_image_items[self.current_page_num][item_id]
            box = data["orig_box"]

            scaled_x1 = self.x_offset + box[0] * self.scale
            scaled_y1 = self.y_offset + box[1] * self.scale
            scaled_x2 = self.x_offset + box[2] * self.scale
            scaled_y2 = self.y_offset + box[3] * self.scale

            if handle == "se":
                scaled_x2 = max(scaled_x1 + 15, event.x)
                scaled_y2 = max(scaled_y1 + 15, event.y)
            elif handle == "sw":
                scaled_x1 = min(scaled_x2 - 15, event.x)
                scaled_y2 = max(scaled_y1 + 15, event.y)
            elif handle == "ne":
                scaled_x2 = max(scaled_x1 + 15, event.x)
                scaled_y1 = min(scaled_y2 - 15, event.y)
            elif handle == "nw":
                scaled_x1 = min(scaled_x2 - 15, event.x)
                scaled_y1 = min(scaled_y2 - 15, event.y)

            box[0] = (scaled_x1 - self.x_offset) / self.scale
            box[1] = (scaled_y1 - self.y_offset) / self.scale
            box[2] = (scaled_x2 - self.x_offset) / self.scale
            box[3] = (scaled_y2 - self.y_offset) / self.scale

            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y
            self.render_page()
            self.draw_image_handles(item_id)
            return

        delta_orig_x = dx / self.scale
        delta_orig_y = dy / self.scale

        if item_type == "text":
            data = self.master_text_items[self.current_page_num][item_id]
            data["orig_pos"] = (
                data["orig_pos"][0] + delta_orig_x,
                data["orig_pos"][1] + delta_orig_y,
            )
            self.canvas.move(data["canvas_id"], dx, dy)

        elif item_type == "shape":
            data = self.master_shape_items[self.current_page_num][item_id]
            data["orig_box"] = [
                data["orig_box"][0] + delta_orig_x,
                data["orig_box"][1] + delta_orig_y,
                data["orig_box"][2] + delta_orig_x,
                data["orig_box"][3] + delta_orig_y,
            ]
            self.canvas.move(data["canvas_id"], dx, dy)

        elif item_type == "image":
            data = self.master_image_items[self.current_page_num][item_id]
            data["orig_box"] = [
                data["orig_box"][0] + delta_orig_x,
                data["orig_box"][1] + delta_orig_y,
                data["orig_box"][2] + delta_orig_x,
                data["orig_box"][3] + delta_orig_y,
            ]
            self.canvas.move(data["canvas_id"], dx, dy)
            self.draw_image_handles(item_id)

        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def on_canvas_release(self, event):
        if self.drawing_shape:
            coords = self.canvas.coords(self.drawing_shape)
            self.canvas.delete(self.drawing_shape)
            self.drawing_shape = None

            x1 = min(coords[0], coords[2])
            y1 = min(coords[1], coords[3])
            x2 = max(coords[0], coords[2])
            y2 = max(coords[1], coords[3])

            if (x2 - x1) > 5 and (y2 - y1) > 5:
                orig_x1 = (x1 - self.x_offset) / self.scale
                orig_y1 = (y1 - self.y_offset) / self.scale
                orig_x2 = (x2 - self.x_offset) / self.scale
                orig_y2 = (y2 - self.y_offset) / self.scale

                item_id = f"shape_{len(self.master_shape_items.get(self.current_page_num, {}))}_{self.current_page_num}"
                self.master_shape_items[self.current_page_num][item_id] = {
                    "orig_box": [orig_x1, orig_y1, orig_x2, orig_y2],
                    "color": self.shape_color,
                    "shape_type": self.current_shape_type.get(),
                }
                self.render_page()
                self.trigger_autosave()
            return

        if self.drag_data["item"]:
            self.drag_data = {"item": None, "x": 0, "y": 0, "handle": None}
            self.trigger_autosave()

    def on_right_click(self, event):
        if not self.pdf_doc:
            return

        overlap = self.canvas.find_overlapping(event.x - 2, event.y - 2, event.x + 2, event.y + 2)
        topmost = None
        for item in reversed(overlap):
            tags = self.canvas.gettags(item)
            if "added_text" in tags or "added_shape" in tags or "added_image" in tags:
                topmost = item
                break

        if topmost:
            item_type = None
            item_key = None
            tags = self.canvas.gettags(topmost)

            if "added_text" in tags:
                item_type = "text"
                for k, v in self.master_text_items.get(self.current_page_num, {}).items():
                    if v.get("canvas_id") == topmost:
                        item_key = k
                        break
            elif "added_shape" in tags:
                item_type = "shape"
                for k, v in self.master_shape_items.get(self.current_page_num, {}).items():
                    if v.get("canvas_id") == topmost:
                        item_key = k
                        break
            elif "added_image" in tags:
                item_type = "image"
                for k, v in self.master_image_items.get(self.current_page_num, {}).items():
                    if v.get("canvas_id") == topmost:
                        item_key = k
                        break

            if item_key:
                confirm = messagebox.askyesno("Delete Item", f"Delete this {item_type}?")
                if confirm:
                    if item_type == "text":
                        del self.master_text_items[self.current_page_num][item_key]
                    elif item_type == "shape":
                        del self.master_shape_items[self.current_page_num][item_key]
                    elif item_type == "image":
                        del self.master_image_items[self.current_page_num][item_key]
                        self.remove_image_handles()
                        self.selected_image = None

                    self.render_page()
                    self.trigger_autosave()

    def draw_image_handles(self, item_id):
        self.remove_image_handles()
        data = self.master_image_items.get(self.current_page_num, {}).get(item_id)
        if not data:
            return

        box = data["orig_box"]
        x1 = self.x_offset + box[0] * self.scale
        y1 = self.y_offset + box[1] * self.scale
        x2 = self.x_offset + box[2] * self.scale
        y2 = self.y_offset + box[3] * self.scale

        corners = {
            "nw": (x1, y1),
            "ne": (x2, y1),
            "se": (x2, y2),
            "sw": (x1, y2)
        }

        r = 5
        for name, (hx, hy) in corners.items():
            self.canvas.create_rectangle(
                hx - r, hy - r, hx + r, hy + r,
                fill="#2ECC8A", outline="#FFFFFF", width=1,
                tags=("img_handle", f"handle_{name}")
            )

    def remove_image_handles(self):
        self.canvas.delete("img_handle")

    def trigger_autosave(self):
        if not self.current_filepath:
            return

        if self._save_timer:
            self.root.after_cancel(self._save_timer)

        self._save_timer = self.root.after(1000, self.save_in_background)

    def save_in_background(self):
        self.lbl_save_status.config(text="Saving...", fg="#D97706")
        thread = threading.Thread(target=self._apply_and_save, daemon=True)
        thread.start()

    def _apply_and_save(self):
        try:
            doc = fitz.open("pdf", self.pdf_bytes)

            for page_idx in range(len(doc)):
                page = doc[page_idx]

                page_shapes = self.master_shape_items.get(page_idx, {})
                for sid, sdata in page_shapes.items():
                    box = sdata["orig_box"]
                    rect = fitz.Rect(box[0], box[1], box[2], box[3])
                    hex_c = sdata.get("color", "#FFFFFF").lstrip("#")
                    rgb = tuple(int(hex_c[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
                    stype = sdata.get("shape_type", "rectangle")
                    if stype == "oval":
                        page.draw_oval(rect, color=rgb, fill=rgb)
                    else:
                        page.draw_rect(rect, color=rgb, fill=rgb)

                page_images = self.master_image_items.get(page_idx, {})
                for iid, idata in page_images.items():
                    box = idata["orig_box"]
                    rect = fitz.Rect(box[0], box[1], box[2], box[3])
                    raw_bytes = base64.b64decode(idata["png_bytes"])
                    page.insert_image(rect, stream=raw_bytes)

                page_texts = self.master_text_items.get(page_idx, {})
                for tid, tdata in page_texts.items():
                    pos = tdata["orig_pos"]
                    size = tdata.get("size", 14)
                    hex_c = tdata.get("color", "#000000").lstrip("#")
                    rgb = tuple(int(hex_c[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
                    point = fitz.Point(pos[0], pos[1] + size)
                    page.insert_text(point, tdata["text"], fontsize=size, color=rgb)

            output_bytes = doc.tobytes()
            doc.close()

            with open(self.current_filepath, "wb") as f:
                f.write(output_bytes)

            self.root.after(0, self._on_save_success)

        except Exception as e:
            self.root.after(0, lambda: self._on_save_failure(str(e)))

    def _on_save_success(self):
        self.lbl_save_status.config(text="All changes saved", fg="#059669")
        if self._save_timer:
            self.root.after_cancel(self._save_timer)
        self._save_timer = self.root.after(3000, lambda: self.lbl_save_status.config(text=""))

    def _on_save_failure(self, error_msg):
        self.lbl_save_status.config(text="Save failed!", fg="#DC2626")
        messagebox.showerror("Autosave Failed", f"Could not auto-save to file:\n\n{error_msg}")

    def save_as_pdf(self):
        if not self.pdf_doc:
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Documents", "*.pdf")],
            title="Save PDF As..."
        )
        if not save_path:
            return

        try:
            doc = fitz.open("pdf", self.pdf_bytes)

            for page_idx in range(len(doc)):
                page = doc[page_idx]

                page_shapes = self.master_shape_items.get(page_idx, {})
                for sid, sdata in page_shapes.items():
                    box = sdata["orig_box"]
                    rect = fitz.Rect(box[0], box[1], box[2], box[3])
                    hex_c = sdata.get("color", "#FFFFFF").lstrip("#")
                    rgb = tuple(int(hex_c[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
                    stype = sdata.get("shape_type", "rectangle")
                    if stype == "oval":
                        page.draw_oval(rect, color=rgb, fill=rgb)
                    else:
                        page.draw_rect(rect, color=rgb, fill=rgb)

                page_images = self.master_image_items.get(page_idx, {})
                for iid, idata in page_images.items():
                    box = idata["orig_box"]
                    rect = fitz.Rect(box[0], box[1], box[2], box[3])
                    raw_bytes = base64.b64decode(idata["png_bytes"])
                    page.insert_image(rect, stream=raw_bytes)

                page_texts = self.master_text_items.get(page_idx, {})
                for tid, tdata in page_texts.items():
                    pos = tdata["orig_pos"]
                    size = tdata.get("size", 14)
                    hex_c = tdata.get("color", "#000000").lstrip("#")
                    rgb = tuple(int(hex_c[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
                    point = fitz.Point(pos[0], pos[1] + size)
                    page.insert_text(point, tdata["text"], fontsize=size, color=rgb)

            doc.save(save_path)
            doc.close()

            messagebox.showinfo("Saved", f"File saved successfully to:\n{save_path}")

        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save PDF:\n\n{e}")


# Backward compatibility alias
ModernPDFEditor = EditorFrame

if __name__ == "__main__":
    from app_controller import PDFCommanderApp

    root = tk.Tk()
    app = PDFCommanderApp(root)
    app.show_frame("editor")
    root.mainloop()