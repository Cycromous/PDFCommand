import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, colorchooser, ttk
import fitz
import base64 
import os
import sys
import threading

class ModernPDFEditor:
    def __init__(self, root, main_app_window=None):
        self.root = root
        self.main_app_window = main_app_window
        self.root.title("PDF Editor")
        
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

    def create_tool_button(self, parent, text, bg_color, fg_color, command, width=100, height=36):
        canvas = tk.Canvas(parent, width=width, height=height, bg="#93E9BE", highlightthickness=0, bd=0)
        radius = height / 2
        x1, y1, x2, y2 = 2, 2, width-2, height-2
        points = [
            x1+radius, y1, x2-radius, y1, x2, y1, x2, y1+radius,
            x2, y2-radius, x2, y2, x2-radius, y2, x1+radius, y2,
            x1, y2, x1, y2-radius, x1, y1+radius, x1, y1
        ]
        
        shape = canvas.create_polygon(points, smooth=True, fill=bg_color)
        txt = canvas.create_text(width/2, height/2, text=text, fill=fg_color, font=("Segoe UI", 9, "bold"))
        
        def on_click(e): command()
        canvas.bind("<Button-1>", on_click)
        canvas.configure(cursor="hand2")
        return canvas, shape, txt

    def setup_gui(self):
        self.toolbar_color = "#93E9BE"
        toolbar = tk.Frame(self.root, bg=self.toolbar_color, bd=0)
        toolbar.pack(fill=tk.X, side=tk.TOP, pady=(0, 0))

        inner_toolbar = tk.Frame(toolbar, bg=self.toolbar_color, pady=12, padx=15)
        inner_toolbar.pack(fill=tk.X)

        tk.Button(inner_toolbar, text="Home", command=self.go_home, bg=self.toolbar_color, fg="#1F2937", font=("Segoe UI", 10, "bold"), bd=0, activebackground=self.toolbar_color, cursor="hand2").pack(side=tk.LEFT, padx=(0, 15))
        self.create_rounded_button(inner_toolbar, text="Open PDF", bg_color="#FFFFFF", fg_color="#374151", command=self.open_pdf, width=140).pack(side=tk.LEFT, padx=(0, 10))

        tk.Frame(inner_toolbar, bg="#71C89F", width=2).pack(side=tk.LEFT, fill=tk.Y, pady=5, padx=10)

        tools_frame = tk.Frame(inner_toolbar, bg=self.toolbar_color)
        tools_frame.pack(side=tk.LEFT, padx=5)
        
        tk.Label(tools_frame, text="Active Tool", bg=self.toolbar_color, fg="#1F2937", font=("Segoe UI", 9, "bold")).pack(side=tk.TOP, anchor="w")
        
        btns_frame = tk.Frame(tools_frame, bg=self.toolbar_color)
        btns_frame.pack(side=tk.TOP)
        
        self.btn_text = self.create_tool_button(btns_frame, "Text", "#111827", "#FFFFFF", lambda: self.set_mode("text"))
        self.btn_text[0].pack(side=tk.LEFT, padx=2)
        
        self.btn_shape = self.create_tool_button(btns_frame, "Shape", "#FFFFFF", "#374151", lambda: self.set_mode("shape"))
        self.btn_shape[0].pack(side=tk.LEFT, padx=2)

        self.shape_combo = ttk.Combobox(btns_frame, textvariable=self.current_shape_type, values=("rectangle", "oval"), width=8, state="readonly")
        self.shape_combo.pack(side=tk.LEFT, padx=(2, 5))
        
        self.btn_color_canvas = tk.Canvas(btns_frame, width=32, height=32, bg=self.toolbar_color, highlightthickness=0)
        self.color_circle = self.btn_color_canvas.create_oval(4, 4, 28, 28, fill=self.shape_color, outline="#D1D5DB", width=1)
        self.btn_color_canvas.tag_bind(self.color_circle, "<Button-1>", lambda e: self.pick_color())
        self.btn_color_canvas.bind("<Button-1>", lambda e: self.pick_color())
        self.btn_color_canvas.config(cursor="hand2")
        self.btn_color_canvas.pack(side=tk.LEFT, padx=(5, 5))
        
        self.btn_image = self.create_tool_button(btns_frame, "Image", "#FFFFFF", "#374151", self.add_image)
        self.btn_image[0].pack(side=tk.LEFT, padx=2)

        tk.Frame(inner_toolbar, bg="#71C89F", width=2).pack(side=tk.LEFT, fill=tk.Y, pady=5, padx=10)

        font_size_frame = tk.Frame(inner_toolbar, bg=self.toolbar_color)
        font_size_frame.pack(side=tk.LEFT, padx=5)
        tk.Label(font_size_frame, text="Font Size", bg=self.toolbar_color, fg="#1F2937", font=("Segoe UI", 9, "bold")).pack(side=tk.TOP, anchor="w")

        slider_canvas = tk.Canvas(font_size_frame, width=180, height=50, bg=self.toolbar_color, highlightthickness=0, cursor="hand2")
        slider_canvas.pack(side=tk.TOP, pady=(2, 0))

        def _draw_slider(val):
            slider_canvas.delete("all")
            min_v, max_v = 2, 50
            frac = (val - min_v) / (max_v - min_v)
            cx = 15 + frac * 150
            slider_canvas.create_rectangle(15, 22, 165, 28, fill="#A8DFC5", outline="")
            slider_canvas.create_rectangle(15, 22, cx, 28, fill="#2ECC8A", outline="")
            slider_canvas.create_oval(cx-14, 25-14, cx+14, 25+14, fill="#2ECC8A", outline="#FFFFFF", width=3)
            slider_canvas.create_text(cx, 25, text=str(val), font=("Segoe UI", 10, "bold"), fill="#FFFFFF")

        def _on_slider_click_or_drag(event):
            frac = max(0.0, min(1.0, (event.x - 15) / 150))
            snapped = int(round((2 + frac * 48) / 2) * 2)
            self.font_size.set(max(2, min(50, snapped)))
            _draw_slider(self.font_size.get())

        slider_canvas.bind("<Button-1>", _on_slider_click_or_drag)
        slider_canvas.bind("<B1-Motion>", _on_slider_click_or_drag)
        _draw_slider(self.font_size.get())
        self.font_size.trace_add("write", lambda *_: _draw_slider(self.font_size.get()))

        btn_save = self.create_rounded_button(inner_toolbar, text="Save As", bg_color="#111827", fg_color="#FFFFFF", command=self.save_as_pdf, width=120)
        btn_save.pack(side=tk.RIGHT, padx=5)
        
        self.lbl_save_status = tk.Label(inner_toolbar, text="", bg=self.toolbar_color, fg="#059669", font=("Segoe UI", 9, "bold"))
        self.lbl_save_status.pack(side=tk.RIGHT, padx=10)
        
        self.lbl_instructions = tk.Label(inner_toolbar, text="Drag: Move | Click Image: Show Resize Corners", bg=self.toolbar_color, fg="#1F2937", font=("Segoe UI", 10))
        self.lbl_instructions.pack(side=tk.RIGHT, padx=10)

        self.nav_frame = tk.Frame(self.root, bg="#E5E7EB", pady=8)
        self.nav_frame.pack(fill=tk.X)
        
        self.btn_prev = tk.Button(self.nav_frame, text="Previous Page", command=self.prev_page, font=("Segoe UI", 9, "bold"), bg="#FFFFFF", bd=0, padx=15, pady=4, cursor="hand2")
        self.btn_prev.pack(side=tk.LEFT, padx=20)
        
        self.lbl_page_info = tk.Label(self.nav_frame, text="Page 0 of 0", font=("Segoe UI", 10, "bold"), bg="#E5E7EB", fg="#374151")
        self.lbl_page_info.pack(side=tk.LEFT, expand=True)
        
        self.btn_next = tk.Button(self.nav_frame, text="Next Page", command=self.next_page, font=("Segoe UI", 9, "bold"), bg="#FFFFFF", bd=0, padx=15, pady=4, cursor="hand2")
        self.btn_next.pack(side=tk.RIGHT, padx=20)

        canvas_frame = tk.Frame(self.root, bg="#F0F2F5", bd=0)
        canvas_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        self.canvas = tk.Canvas(canvas_frame, bg="#F0F2F5", bd=0, highlightthickness=0)
        self.canvas.pack(expand=True, fill=tk.BOTH) 
        
        self.canvas.bind("<ButtonPress-1>", self.on_left_click)  
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)     
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release) 
        self.canvas.bind("<Button-3>", self.on_right_click)      

    def set_mode(self, mode):
        self.current_mode = mode
        if mode == "text":
            self.btn_text[0].itemconfig(self.btn_text[1], fill="#111827")
            self.btn_text[0].itemconfig(self.btn_text[2], fill="#FFFFFF")
            self.btn_shape[0].itemconfig(self.btn_shape[1], fill="#FFFFFF")
            self.btn_shape[0].itemconfig(self.btn_shape[2], fill="#374151")
            self.lbl_instructions.config(text="Drag: Move | Click Image: Show Resize Corners")
        else:
            self.btn_shape[0].itemconfig(self.btn_shape[1], fill="#111827")
            self.btn_shape[0].itemconfig(self.btn_shape[2], fill="#FFFFFF")
            self.btn_text[0].itemconfig(self.btn_text[1], fill="#FFFFFF")
            self.btn_text[0].itemconfig(self.btn_text[2], fill="#374151")
            self.lbl_instructions.config(text="Click & Drag to draw Shape | Right-click to delete")

    def pick_color(self):
        color_code = colorchooser.askcolor(title="Choose Shape Color", initialcolor=self.shape_color)[1]
        if color_code:
            self.shape_color = color_code
            self.btn_color_canvas.itemconfig(self.color_circle, fill=self.shape_color)

    def update_handles(self):
        self.canvas.delete("handle")
        self.canvas.delete("bbox")
        
        if not self.selected_image or not self.canvas.coords(self.selected_image):
            return

        x, y = self.canvas.coords(self.selected_image)
        data = self.master_image_items[self.current_page_num][self.selected_image]
        w = data['current_width'] / self.scale_factor
        h = data['current_height'] / self.scale_factor

        self.canvas.create_rectangle(x, y, x+w, y+h, outline="#2ECC8A", dash=(4, 4), width=2, tags=("bbox",))

        r = 5 
        self.canvas.create_rectangle(x-r, y-r, x+r, y+r, fill="#FFFFFF", outline="#2ECC8A", width=2, tags=("handle", "nw"))
        self.canvas.create_rectangle(x+w-r, y-r, x+w+r, y+r, fill="#FFFFFF", outline="#2ECC8A", width=2, tags=("handle", "ne"))
        self.canvas.create_rectangle(x-r, y+h-r, x+r, y+h+r, fill="#FFFFFF", outline="#2ECC8A", width=2, tags=("handle", "sw"))
        self.canvas.create_rectangle(x+w-r, y+h-r, x+w+r, y+h+r, fill="#FFFFFF", outline="#2ECC8A", width=2, tags=("handle", "se"))

    def add_image(self):
        if not hasattr(self, 'x_offset'):
            messagebox.showwarning("Empty", "Please open a PDF first before adding an image.")
            return

        filepath = filedialog.askopenfilename(
            title="Select Image or Signature",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")]
        )
        if not filepath: return

        try:
            raw_doc = fitz.open(filepath)
            pdf_bytes = raw_doc.convert_to_pdf()
            raw_doc.close()

            img_doc = fitz.open("pdf", pdf_bytes)
            img_page = img_doc[0]
            
            rect = img_page.rect
            max_size = 250.0
            scale = 1.0
            if rect.width > max_size or rect.height > max_size:
                scale = min(max_size / rect.width, max_size / rect.height)
            
            mat = fitz.Matrix(scale, scale)
            pix = img_page.get_pixmap(matrix=mat, alpha=True)

            png_bytes = pix.tobytes("png")
            b64_data = base64.b64encode(png_bytes)
            tk_img = tk.PhotoImage(data=b64_data)

            spawn_x = self.x_offset + 50
            spawn_y = self.y_offset + 50

            item_id = self.canvas.create_image(spawn_x, spawn_y, anchor=tk.NW, image=tk_img, tags=("draggable", "image"))

            self.tk_images[item_id] = tk_img
            
            self.master_image_items[self.current_page_num][item_id] = {
                'filepath': filepath,
                'pdf_bytes': pdf_bytes, 
                'scale': scale,
                'current_width': pix.width,
                'current_height': pix.height,
                'width': img_page.rect.width, 
                'height': img_page.rect.height
            }
            
            img_doc.close()
            self.set_mode("text")
            
            self.selected_image = item_id
            self.update_handles()
            self.trigger_autosave()

        except Exception as e:
            messagebox.showerror("Error", f"Could not load image:\n\n{e}")

    def update_nav_buttons(self):
        self.lbl_page_info.config(text=f"Page {self.current_page_num + 1} of {self.total_pages}")
        
        if self.current_page_num == 0:
            self.btn_prev.config(state=tk.DISABLED, bg="#E5E7EB", fg="#9CA3AF")
        else:
            self.btn_prev.config(state=tk.NORMAL, bg="#FFFFFF", fg="#111827")
            
        if self.current_page_num == self.total_pages - 1:
            self.btn_next.config(state=tk.DISABLED, bg="#E5E7EB", fg="#9CA3AF")
        else:
            self.btn_next.config(state=tk.NORMAL, bg="#FFFFFF", fg="#111827")

    def next_page(self):
        if self.current_page_num < self.total_pages - 1:
            self.current_page_num += 1
            self.render_page()

    def prev_page(self):
        if self.current_page_num > 0:
            self.current_page_num -= 1
            self.render_page()

    def open_pdf(self):
        filepath = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if not filepath: return
        
        self.current_filepath = filepath
        with open(filepath, "rb") as f:
            self.pdf_bytes = f.read()
            
        self.pdf_doc = fitz.open("pdf", self.pdf_bytes)
        self.total_pages = len(self.pdf_doc)
        self.current_page_num = 0
        
        self.master_text_items = {i: {} for i in range(self.total_pages)}
        self.master_shape_items = {i: {} for i in range(self.total_pages)}
        self.master_image_items = {i: {} for i in range(self.total_pages)}
        
        self.tk_images.clear()
        self.selected_image = None
        
        self.root.update_idletasks()
        self.render_page()

    def render_page(self):
        if not self.pdf_doc: return
        page = self.pdf_doc[self.current_page_num]
        
        self.update_nav_buttons()
        self.selected_image = None
        
        canvas_height = self.canvas.winfo_height()
        if canvas_height <= 1: canvas_height = self.root.winfo_screenheight() - 150
            
        target_height = canvas_height * 0.98 
        self.scale_factor = target_height / page.rect.height
        
        mat = fitz.Matrix(self.scale_factor, self.scale_factor)
        pix = page.get_pixmap(matrix=mat)
        
        img_data = pix.tobytes("ppm")
        self.page_image = tk.PhotoImage(data=img_data)
        
        self.canvas.config(width=pix.width, height=pix.height)
        self.canvas.delete("all") 
        
        canvas_width = self.canvas.winfo_width()
        if canvas_width <= 1: canvas_width = self.root.winfo_screenwidth()
            
        x_offset = (canvas_width - pix.width) // 2
        if x_offset < 0: x_offset = 0 
        
        self.canvas.create_rectangle(x_offset + 3, 10 + 3, x_offset + pix.width + 3, 10 + pix.height + 3, fill="#D1D5DB", outline="")
        self.canvas.create_image(x_offset, 10, anchor=tk.NW, image=self.page_image)
        self.x_offset = x_offset 
        self.y_offset = 10
        
        for item_id, data in list(self.master_shape_items[self.current_page_num].items()):
            tx1, ty1, tx2, ty2 = data['true_coords']
            cx1 = (tx1 * self.scale_factor) + self.x_offset
            cy1 = (ty1 * self.scale_factor) + self.y_offset
            cx2 = (tx2 * self.scale_factor) + self.x_offset
            cy2 = (ty2 * self.scale_factor) + self.y_offset
            
            shape_type = data.get('type', 'rectangle')
            if shape_type == 'rectangle':
                new_id = self.canvas.create_rectangle(cx1, cy1, cx2, cy2, fill=data['color'], outline=data['color'], tags=("draggable", "shape"))
            elif shape_type == 'oval':
                new_id = self.canvas.create_oval(cx1, cy1, cx2, cy2, fill=data['color'], outline=data['color'], tags=("draggable", "shape"))
            
            self.master_shape_items[self.current_page_num][new_id] = self.master_shape_items[self.current_page_num].pop(item_id)
            self.master_shape_items[self.current_page_num][new_id]['true_coords'] = (tx1, ty1, tx2, ty2)

        for item_id, data in list(self.master_text_items[self.current_page_num].items()):
            true_x, true_y = data['true_coords']
            cx = (true_x * self.scale_factor) + self.x_offset
            cy = (true_y * self.scale_factor) + self.y_offset
            scaled_size = int(data['size'] * self.scale_factor)
            
            new_id = self.canvas.create_text(cx, cy, text=data['text'], font=("Times Roman", scaled_size), anchor=tk.SW, fill="#000000", tags=("draggable",))
            self.master_text_items[self.current_page_num][new_id] = self.master_text_items[self.current_page_num].pop(item_id)
            self.master_text_items[self.current_page_num][new_id]['true_coords'] = (true_x, true_y)
            
        for item_id, data in list(self.master_image_items[self.current_page_num].items()):
            true_x, true_y = data.get('true_coords', (0, 0))
            
            img_doc = fitz.open("pdf", data['pdf_bytes'])
            mat = fitz.Matrix(data['scale'], data['scale'])
            pix = img_doc[0].get_pixmap(matrix=mat, alpha=True)
            img_doc.close()
            
            png_bytes = pix.tobytes("png")
            b64_data = base64.b64encode(png_bytes)
            tk_img = tk.PhotoImage(data=b64_data)
            
            cx = (true_x * self.scale_factor) + self.x_offset
            cy = (true_y * self.scale_factor) + self.y_offset
            
            if true_x == 0 and true_y == 0:
                cx = self.x_offset + 50
                cy = self.y_offset + 50
                
            new_id = self.canvas.create_text(
                cx, cy, text=data['text'], font=("Times", -max(1, scaled_size)), 
                anchor=tk.SW, fill="#000000", tags=("draggable",)
            )
            
            self.master_image_items[self.current_page_num][new_id] = self.master_image_items[self.current_page_num].pop(item_id)
            self.master_image_items[self.current_page_num][new_id]['true_coords'] = (true_x, true_y)

    def on_left_click(self, event):
        if not self.pdf_doc: return
        
        item = self.canvas.find_withtag("current")
        if item:
            tags = self.canvas.gettags(item[0])
            
            if "handle" in tags:
                self.drag_data["handle"] = tags[1] 
                self.drag_data["start_x"] = event.x
                self.drag_data["start_y"] = event.y
                
                x, y = self.canvas.coords(self.selected_image)
                data = self.master_image_items[self.current_page_num][self.selected_image]
                w = data['current_width'] / self.scale_factor
                h = data['current_height'] / self.scale_factor
                self.drag_data["orig_bbox"] = (x, y, w, h)
                return
            
            elif "image" in tags:
                self.selected_image = item[0]
                self.update_handles()
                self.drag_data["item"] = item[0]
                self.drag_data["x"] = event.x
                self.drag_data["y"] = event.y
                return
            
            elif "draggable" in tags:
                self.selected_image = None
                self.update_handles()
                self.drag_data["item"] = item[0]
                self.drag_data["x"] = event.x
                self.drag_data["y"] = event.y
                return

        self.selected_image = None
        self.update_handles()

        if not hasattr(self, 'x_offset') or event.x < self.x_offset or event.y < self.y_offset: 
            return

        if self.current_mode == "text":
            self.add_text_prompt(event.x, event.y)
        elif self.current_mode == "shape":
            self.start_x = event.x
            self.start_y = event.y
            shape_type = self.current_shape_type.get()
            
            if shape_type == "rectangle":
                self.drawing_shape = self.canvas.create_rectangle(
                    self.start_x, self.start_y, self.start_x, self.start_y,
                    fill=self.shape_color, outline=self.shape_color, tags=("draggable", "shape")
                )
            elif shape_type == "oval":
                self.drawing_shape = self.canvas.create_oval(
                    self.start_x, self.start_y, self.start_x, self.start_y,
                    fill=self.shape_color, outline=self.shape_color, tags=("draggable", "shape")
                )

    def on_canvas_drag(self, event):
        if self.drag_data.get("handle"):
            x, y, w, h = self.drag_data["orig_bbox"]
            corner = self.drag_data["handle"]
            dx = event.x - self.drag_data["start_x"]
            
            ratio = h / w
            nw, nh, nx, ny = w, h, x, y

            if corner == "se":
                nw = max(20, w + dx)
                nh = nw * ratio
            elif corner == "sw":
                nw = max(20, w - dx)
                nh = nw * ratio
                nx = x + (w - nw)
            elif corner == "ne":
                nw = max(20, w + dx)
                nh = nw * ratio
                ny = y + (h - nh)
            elif corner == "nw":
                nw = max(20, w - dx)
                nh = nw * ratio
                nx = x + (w - nw)
                ny = y + (h - nh)

            self.canvas.coords("bbox", nx, ny, nx+nw, ny+nh)
            
            r = 5
            self.canvas.coords("nw", nx-r, ny-r, nx+r, ny+r)
            self.canvas.coords("ne", nx+nw-r, ny-r, nx+nw+r, ny+r)
            self.canvas.coords("sw", nx-r, ny+nh-r, nx+r, ny+nh+r)
            self.canvas.coords("se", nx+nw-r, ny+nh-r, nx+nw+r, ny+nh+r)
            
            self.drag_data["new_bbox"] = (nx, ny, nw, nh)

            data = self.master_image_items[self.current_page_num][self.selected_image]
            orig_w = data['width'] 

            new_scale = nw / orig_w

            try:
                img_doc = fitz.open("pdf", data['pdf_bytes'])
                img_page = img_doc[0]
                mat = fitz.Matrix(new_scale, new_scale)
                pix = img_page.get_pixmap(matrix=mat, alpha=True)

                png_bytes = pix.tobytes("png")
                b64_data = base64.b64encode(png_bytes)
                new_tk_img = tk.PhotoImage(data=b64_data)

                self.canvas.coords(self.selected_image, nx, ny)
                self.canvas.itemconfig(self.selected_image, image=new_tk_img)

                self.tk_images[self.selected_image] = new_tk_img
                data['scale'] = new_scale
                data['current_width'] = pix.width
                data['current_height'] = pix.height

                img_doc.close()
            except Exception:
                pass

        elif self.drag_data.get("item"):
            dx = event.x - self.drag_data["x"]
            dy = event.y - self.drag_data["y"]
            self.canvas.move(self.drag_data["item"], dx, dy)
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y
            
            if self.drag_data["item"] == self.selected_image:
                self.update_handles()
            
        elif self.drawing_shape:
            self.canvas.coords(self.drawing_shape, self.start_x, self.start_y, event.x, event.y)

    def on_canvas_release(self, event):
        data_changed = False
        if self.drag_data.get("handle"):
            self.update_handles()
            self.drag_data["handle"] = None
            self.drag_data.pop("new_bbox", None)
            data_changed = True

        elif self.drawing_shape:
            coords = self.canvas.coords(self.drawing_shape)
            tx1 = (coords[0] - self.x_offset) / self.scale_factor
            ty1 = (coords[1] - self.y_offset) / self.scale_factor
            tx2 = (coords[2] - self.x_offset) / self.scale_factor
            ty2 = (coords[3] - self.y_offset) / self.scale_factor
            
            self.master_shape_items[self.current_page_num][self.drawing_shape] = {
                'type': self.current_shape_type.get(),
                'color': self.shape_color,
                'true_coords': (tx1, ty1, tx2, ty2)
            }
            self.drawing_shape = None
            data_changed = True
            
        elif self.drag_data.get("item"):
            item_id = self.drag_data["item"]
            coords = self.canvas.coords(item_id)
            
            if item_id in self.master_text_items[self.current_page_num]:
                true_x = (coords[0] - self.x_offset) / self.scale_factor
                true_y = (coords[1] - self.y_offset) / self.scale_factor
                self.master_text_items[self.current_page_num][item_id]['true_coords'] = (true_x, true_y)
                data_changed = True
                
            elif item_id in self.master_image_items[self.current_page_num]:
                true_x = (coords[0] - self.x_offset) / self.scale_factor
                true_y = (coords[1] - self.y_offset) / self.scale_factor
                self.master_image_items[self.current_page_num][item_id]['true_coords'] = (true_x, true_y)
                data_changed = True
                
            elif item_id in self.master_shape_items[self.current_page_num]:
                tx1 = (coords[0] - self.x_offset) / self.scale_factor
                ty1 = (coords[1] - self.y_offset) / self.scale_factor
                tx2 = (coords[2] - self.x_offset) / self.scale_factor
                ty2 = (coords[3] - self.y_offset) / self.scale_factor
                self.master_shape_items[self.current_page_num][item_id]['true_coords'] = (tx1, ty1, tx2, ty2)
                data_changed = True
            
        self.drag_data["item"] = None
        
        if data_changed:
            self.trigger_autosave()

    def on_right_click(self, event):
        if not self.pdf_doc: return
        item = self.canvas.find_withtag("current")
        if item and "draggable" in self.canvas.gettags(item[0]):
            item_id = item[0]
            
            if item_id == self.selected_image:
                self.selected_image = None
                self.update_handles()
                
            self.canvas.delete(item_id)
            
            if item_id in self.master_text_items[self.current_page_num]: del self.master_text_items[self.current_page_num][item_id]
            if item_id in self.master_shape_items[self.current_page_num]: del self.master_shape_items[self.current_page_num][item_id]
            if item_id in self.master_image_items[self.current_page_num]: del self.master_image_items[self.current_page_num][item_id]
            if item_id in self.tk_images: del self.tk_images[item_id]
            
            self.trigger_autosave()

    def add_text_prompt(self, x, y):
        text = simpledialog.askstring("Add Text", "Type the text to place here:", parent=self.root)
        self.root.focus_force()
        if text:
            original_size = self.font_size.get()
            scaled_size = int(original_size * self.scale_factor)
            item_id = self.canvas.create_text(
                x, y, text=text, font=("Times", -max(1, scaled_size)), 
                anchor=tk.SW, fill="#000000", tags=("draggable",)
            )
            
            true_x = (x - self.x_offset) / self.scale_factor
            true_y = (y - self.y_offset) / self.scale_factor
            
            self.master_text_items[self.current_page_num][item_id] = {
                'text': text, 
                'size': original_size,
                'true_coords': (true_x, true_y)
            }
            self.trigger_autosave()

    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))
        
    def trigger_autosave(self):
        if not self.current_filepath or not self.pdf_bytes: return
        
        self.lbl_save_status.config(text="Saving...", fg="#D97706") 
        self.root.update_idletasks()
        
        threading.Thread(target=self._perform_save_to_path, args=(self.current_filepath,), daemon=True).start()

    def _perform_save_to_path(self, filepath):
        try:
            temp_doc = fitz.open("pdf", self.pdf_bytes)
            
            for p_num in range(temp_doc.page_count):
                page = temp_doc[p_num]
                
                for item_id, data in self.master_shape_items[p_num].items():
                    tx1, ty1, tx2, ty2 = data['true_coords']
                    rect = fitz.Rect(tx1, ty1, tx2, ty2)
                    rgb = self.hex_to_rgb(data['color'])
                    shape_type = data.get('type', 'rectangle')
                    
                    if shape_type == 'rectangle':
                        page.draw_rect(rect, color=rgb, fill=rgb)
                    elif shape_type == 'oval':
                        page.draw_oval(rect, color=rgb, fill=rgb)

                for item_id, data in self.master_image_items[p_num].items():
                    tx1, ty1 = data.get('true_coords', ((50)/self.scale_factor, (50)/self.scale_factor))
                    tx2 = tx1 + (data['current_width'] / self.scale_factor)
                    ty2 = ty1 + (data['current_height'] / self.scale_factor)
                    rect = fitz.Rect(tx1, ty1, tx2, ty2)
                    
                    img_doc = fitz.open("pdf", data['pdf_bytes'])
                    page.insert_image(rect, pixmap=img_doc[0].get_pixmap(alpha=True))
                    img_doc.close()

                for item_id, data in self.master_text_items[p_num].items():
                    true_x, true_y = data['true_coords']
                    adjusted_y = true_y - (data['size'] * 0.20) 
                    p = fitz.Point(true_x, adjusted_y)
                    page.insert_text(p, data['text'], fontname="tiro", fontsize=data['size'], color=(0, 0, 0))
                
            temp_doc.save(filepath)
            temp_doc.close()
            
            self.root.after(0, self._show_saved_status)
            
        except Exception as e:
            print(f"Autosave failed: {e}")
            self.root.after(0, self._show_error_status)

    def _show_saved_status(self):
        self.lbl_save_status.config(text="All changes saved", fg="#059669")
        if self._save_timer is not None:
            self.root.after_cancel(self._save_timer)
        self._save_timer = self.root.after(3000, lambda: self.lbl_save_status.config(text=""))

    def _show_error_status(self):
        self.lbl_save_status.config(text="Save failed!", fg="#DC2626")

    def save_as_pdf(self):
        if not self.pdf_doc or not self.pdf_bytes:
            messagebox.showwarning("Empty", "Please open a PDF first.")
            return
            
        filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf", filetypes=[("PDF Documents", "*.pdf")], title="Download Edited PDF"
        )
        if filepath:
            self._perform_save_to_path(filepath)
            messagebox.showinfo("Success", "PDF downloaded successfully!")

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernPDFEditor(root)
    root.mainloop()