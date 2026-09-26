import os
import sys
import tkinter as tk

# TCL / TK library setup for Windows / PyInstaller if needed
if not getattr(sys, "frozen", False):
    base_python = getattr(sys, "base_prefix", sys.prefix)
    tcl_path = os.path.join(base_python, "tcl", "tcl8.6")
    tk_path = os.path.join(base_python, "tcl", "tk8.6")
    if os.path.isdir(tcl_path):
        os.environ["TCL_LIBRARY"] = tcl_path
    if os.path.isdir(tk_path):
        os.environ["TK_LIBRARY"] = tk_path

from app_controller import PDFCommanderApp

if __name__ == "__main__":
    root = tk.Tk()

    startup_pdf = None
    if len(sys.argv) > 1 and sys.argv[1].lower().endswith(".pdf"):
        startup_pdf = sys.argv[1]

    app = PDFCommanderApp(root, startup_pdf=startup_pdf)
    root.mainloop()

