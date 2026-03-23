import os
import ctypes
import sys
import tkinter as tk
from tkinter import messagebox
import tkinter.font as tkFont

try:
    from PDFEditor import ModernPDFEditor
    from PDFMerger import ModernPDFMerger
    from PDFSplitter import ModernPDFSplitter
    from PDFConverter import ModernPDFConverter
    from PDFViewer import ModernPDFViewer
except ImportError as e:
    messagebox.showerror("Error", f"Could not find a necessary module:\n\n{e}\n\nPlease ensure PDFEditor.py, PDFMerger.py, PDFSplitter.py, and PDFViewer.py are in this folder.")
    sys.exit()

if not getattr(sys, 'frozen', False):
    base_python = getattr(sys, 'base_prefix', sys.prefix)
    tcl_path = os.path.join(base_python, 'tcl', 'tcl8.6')
    tk_path = os.path.join(base_python, 'tcl', 'tk8.6')
    if os.path.isdir(tcl_path):
        os.environ['TCL_LIBRARY'] = tcl_path
    if os.path.isdir(tk_path):
        os.environ['TK_LIBRARY'] = tk_path

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

MINT_GREEN = "#93E9BE"
TEXT_COLOR = "#1F2937"
BG_GRAY = "#F0F2F5"
WHITE = "#FFFFFF"
SIDEBAR_BG = "#FAFAFA"
GENTLE_GRAY_BORDER = "#E5E7EB"


class PDFCommandApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Commander")
        
        try:
            self.root.state('zoomed')
        except:
            self.root.geometry("1400x900")

        try:
            base_path = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.abspath(".")
            self.root.iconbitmap(os.path.join(base_path, "Commander.ico"))
        except:
            pass
        
        self.root.configure(bg=BG_GRAY)

        self.setup_gui()

    def setup_gui(self):
        sidebar = tk.Frame(self.root, bg=SIDEBAR_BG, width=220, highlightthickness=1, highlightbackground=GENTLE_GRAY_BORDER)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="PDF Commander", font=("Segoe UI", 16, "bold"), fg=TEXT_COLOR, bg=SIDEBAR_BG, pady=25).pack()

        navs = [("🏠 Home", None), ("🔧 Tools", None), ("⏱ Tasks History", self.launch_dummy), ("⚙ Preferences", self.launch_dummy)]
        for text, cmd in navs:
            is_active = "Home" in text
            bg_color = MINT_GREEN if is_active else SIDEBAR_BG
            fg_color = "#000000" if is_active else "#6B7280"
            font_type = ("Segoe UI", 11, "bold" if is_active else "normal")
            
            btn = tk.Label(sidebar, text=text, font=font_type, bg=bg_color, fg=fg_color, anchor="w", padx=25, pady=12, cursor="hand2")
            btn.pack(fill=tk.X, padx=15, pady=4)
            if cmd:
                btn.bind("<Button-1>", lambda e, c=cmd: c())

        self.main_area = tk.Frame(self.root, bg=BG_GRAY)
        self.main_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        header_frame = tk.Frame(self.main_area, bg=WHITE, highlightthickness=1, highlightbackground=GENTLE_GRAY_BORDER, pady=30)
        header_frame.pack(fill=tk.X, padx=50, pady=(50, 0))
        tk.Label(header_frame, text="Tools Dashboard", font=("Segoe UI", 28, "bold"), bg=WHITE, fg=TEXT_COLOR).pack()

        tools_container = tk.Frame(self.main_area, bg=BG_GRAY, pady=40)
        tools_container.pack(fill=tk.BOTH, expand=True, padx=50)

        tk.Label(tools_container, text="Available Tools", font=("Segoe UI", 18, "bold"), bg=BG_GRAY, fg=TEXT_COLOR).pack(pady=(0, 30))

        grid_frame = tk.Frame(tools_container, bg=BG_GRAY)
        grid_frame.pack()

        self.create_highly_rounded_card(grid_frame, "Merge", self.launch_merger).pack(side=tk.LEFT, padx=20)
        self.create_highly_rounded_card(grid_frame, "Editor", self.launch_editor).pack(side=tk.LEFT, padx=20)
        self.create_highly_rounded_card(grid_frame, "Split", self.launch_splitter).pack(side=tk.LEFT, padx=20)
        self.create_highly_rounded_card(grid_frame, "Viewer", self.launch_viewer).pack(side=tk.LEFT, padx=20)
        self.create_highly_rounded_card(grid_frame, "Converter", self.launch_converter).pack(side=tk.LEFT, padx=20)


    def create_highly_rounded_card(self, parent, title, command, width=200, height=120, radius=40):
        canvas = tk.Canvas(parent, width=width, height=height, bg=BG_GRAY, highlightthickness=0, cursor="hand2")
        x1, y1, x2, y2 = 4, 4, width-4, height-4
        points = [
            x1+radius, y1, x2-radius, y1, x2, y1, x2, y1+radius,
            x2, y2-radius, x2, y2, x2-radius, y2, x1+radius, y2,
            x1, y2, x1, y2-radius, x1, y1+radius, x1, y1
        ]

        shape = canvas.create_polygon(points, smooth=True, fill="#F9FAFB", outline=GENTLE_GRAY_BORDER, width=2)

        txt = canvas.create_text(width/2, height/2, text=title, font=("Segoe UI", 16, "bold"), fill=TEXT_COLOR)

        def on_enter(e): 
            canvas.itemconfig(shape, fill="#F3F4F6", outline=MINT_GREEN)
            
        def on_leave(e): 
            canvas.itemconfig(shape, fill="#F9FAFB", outline=GENTLE_GRAY_BORDER)
            
        def on_click(e): command()

        canvas.tag_bind(shape, "<Enter>", on_enter)
        canvas.tag_bind(txt, "<Enter>", on_enter)
        canvas.tag_bind(shape, "<Leave>", on_leave)
        canvas.tag_bind(txt, "<Leave>", on_leave)
        canvas.tag_bind(shape, "<Button-1>", on_click)
        canvas.tag_bind(txt, "<Button-1>", on_click)
        canvas.bind("<Button-1>", on_click)
        return canvas

    def launch_dummy(self):
        messagebox.showinfo("Coming Soon", "This feature is currently under construction!")

    def toggle_window(self, existing_window_attr, window_class, window_var_name):
        self.root.withdraw()
        
        existing_window = getattr(self, existing_window_attr, None)
        
        if not existing_window or not existing_window.winfo_exists():
            new_window = tk.Toplevel(self.root)
            setattr(self, existing_window_attr, new_window)
            setattr(self, window_var_name, window_class(new_window, main_app_window=self.root))
        else:
            existing_window.deiconify()
            existing_window.lift()
            try:
                existing_window.state('zoomed')
            except:
                pass

    def launch_editor(self):
        self.toggle_window('editor_window', ModernPDFEditor, 'editor_app')
    
    def launch_merger(self):
        self.toggle_window('merger_window', ModernPDFMerger, 'merger_app')
            
    def launch_splitter(self):
        self.toggle_window('splitter_window', ModernPDFSplitter, 'splitter_app')
        
    def launch_converter(self):
        self.toggle_window('converter_window', ModernPDFConverter, 'converter_app')

    def launch_viewer(self):
        if not hasattr(self, 'viewer_window') or not self.viewer_window.winfo_exists():
            self.root.withdraw()

            self.viewer_window = tk.Toplevel(self.root)
            
            self.viewer_app = ModernPDFViewer(self.viewer_window, main_app_window=self.root)
            
            try:
                self.viewer_window.state('zoomed')
            except:
                pass
        else:
            self.root.withdraw()
            self.viewer_window.deiconify()
            self.viewer_window.lift()

if __name__ == "__main__":
    root = tk.Tk()
    
    if len(sys.argv) > 1 and sys.argv[1].lower().endswith('.pdf'):
        root.withdraw() 
        
        viewer_window = tk.Toplevel(root)
        pdf_path = sys.argv[1]
        try:
            viewer_app = ModernPDFViewer(viewer_window, root, startup_pdf=pdf_path)
        except NameError:
             messagebox.showerror("Error", "ModernPDFViewer class could not be loaded. Please ensure PDFViewer.py is in this folder.")
             root.destroy()
        except TypeError:
             messagebox.showerror("Error", "Your ModernPDFViewer is outdated and does not support automatic loading. Please ask for the updated version.")
             root.destroy()

    else:
        app = PDFCommandApp(root) 
        
    root.mainloop()