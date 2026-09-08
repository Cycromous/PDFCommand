"""Shared canvas-drawn widgets.

Replaces five separate copies of the same rounded-button code that used
to live in Home, PDFConverter, PDFEditor, PDFMerger, and PDFSplitter.
Each of those copies bound the click handler twice:

    canvas.tag_bind(shape, "<Button-1>", on_click)
    canvas.tag_bind(txt, "<Button-1>", on_click)
    canvas.bind("<Button-1>", on_click)   # fires AGAIN for the same click

Because the polygon covers the whole canvas, one click satisfied both the
tag-level binding and the widget-level binding, so command() ran twice.
Fix: only bind on the drawn items, never on the bare canvas too.
"""

import tkinter as tk


def _rounded_points(width, height, radius, pad=2):
    x1, y1, x2, y2 = pad, pad, width - pad, height - pad
    return [
        x1 + radius, y1, x2 - radius, y1, x2, y1, x2, y1 + radius,
        x2, y2 - radius, x2, y2, x2 - radius, y2, x1 + radius, y2,
        x1, y2, x1, y2 - radius, x1, y1 + radius, x1, y1,
    ]


def create_rounded_button(parent, text, bg_color, fg_color, command,
                           width=140, height=36, canvas_bg=None,
                           font=("Segoe UI", 10, "bold"),
                           disabled_color="#9CA3AF"):
    canvas_bg = canvas_bg or (parent.cget("bg") if hasattr(parent, "cget") else "#FFFFFF")
    canvas = tk.Canvas(parent, width=width, height=height, bg=canvas_bg,
                        highlightthickness=0, bd=0, cursor="hand2")
    radius = height / 2
    points = _rounded_points(width, height, radius)

    shape = canvas.create_polygon(points, smooth=True, fill=bg_color)
    txt = canvas.create_text(width / 2, height / 2, text=text, fill=fg_color, font=font)

    def on_click(_event):
        if canvas.itemcget(txt, "fill") == disabled_color:
            return
        command()

    canvas.tag_bind(shape, "<Button-1>", on_click)
    canvas.tag_bind(txt, "<Button-1>", on_click)

    return canvas, shape, txt


def create_hover_card(parent, title, command, width=200, height=120, radius=40,
                       bg=None, idle_fill="#F9FAFB", idle_outline="#E5E7EB",
                       hover_fill="#F3F4F6", hover_outline="#93E9BE",
                       font=("Segoe UI", 16, "bold"), text_color="#1F2937"):
    bg = bg or (parent.cget("bg") if hasattr(parent, "cget") else "#F0F2F5")
    canvas = tk.Canvas(parent, width=width, height=height, bg=bg,
                        highlightthickness=0, cursor="hand2")
    points = _rounded_points(width, height, radius, pad=4)

    shape = canvas.create_polygon(points, smooth=True, fill=idle_fill, outline=idle_outline, width=2)
    txt = canvas.create_text(width / 2, height / 2, text=title, font=font, fill=text_color)

    def on_enter(_e):
        canvas.itemconfig(shape, fill=hover_fill, outline=hover_outline)

    def on_leave(_e):
        canvas.itemconfig(shape, fill=idle_fill, outline=idle_outline)

    def on_click(_e):
        command()

    for item in (shape, txt):
        canvas.tag_bind(item, "<Enter>", on_enter)
        canvas.tag_bind(item, "<Leave>", on_leave)
        canvas.tag_bind(item, "<Button-1>", on_click)

    return canvas

