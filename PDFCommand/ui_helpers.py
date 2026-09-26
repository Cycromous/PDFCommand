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


def create_tool_card(parent, title, description, command,
                      badge="", width=260, height=155):
    """Clean, professional tool card without emojis, with title, badge, description, and hover effect."""
    card = tk.Frame(parent, bg="#FFFFFF", width=width, height=height,
                    highlightthickness=1, highlightbackground="#E5E7EB",
                    cursor="hand2", padx=22, pady=18)
    card.pack_propagate(False)

    top_frame = tk.Frame(card, bg="#FFFFFF")
    top_frame.pack(fill=tk.X, pady=(0, 6))

    lbl_title = tk.Label(top_frame, text=title, font=("Segoe UI", 13, "bold"),
                         bg="#FFFFFF", fg="#1F2937", anchor="w")
    lbl_title.pack(side=tk.LEFT)

    lbl_badge = None
    if badge:
        lbl_badge = tk.Label(top_frame, text=badge.upper(), font=("Segoe UI", 8, "bold"),
                             bg="#ECFDF5", fg="#059669", padx=7, pady=2)
        lbl_badge.pack(side=tk.RIGHT)

    lbl_desc = tk.Label(card, text=description, font=("Segoe UI", 9),
                        bg="#FFFFFF", fg="#64748B", wraplength=width - 44,
                        anchor="w", justify="left")
    lbl_desc.pack(fill=tk.BOTH, expand=True, pady=(0, 6))

    lbl_action = tk.Label(card, text="Open Tool →", font=("Segoe UI", 9, "bold"),
                          bg="#FFFFFF", fg="#059669", anchor="w")
    lbl_action.pack(fill=tk.X)

    widgets_to_bind = [card, top_frame, lbl_title, lbl_desc, lbl_action]
    if lbl_badge:
        widgets_to_bind.append(lbl_badge)

    is_opening = [False]

    def on_enter(_e):
        if is_opening[0]:
            return
        card.config(highlightbackground="#10B981", highlightthickness=2, bg="#F8FAFC")
        top_frame.config(bg="#F8FAFC")
        lbl_title.config(bg="#F8FAFC", fg="#0F172A")
        lbl_desc.config(bg="#F8FAFC")
        lbl_action.config(bg="#F8FAFC", fg="#047857")

    def on_leave(_e):
        if is_opening[0]:
            return
        card.config(highlightbackground="#E5E7EB", highlightthickness=1, bg="#FFFFFF")
        top_frame.config(bg="#FFFFFF")
        lbl_title.config(bg="#FFFFFF", fg="#1F2937")
        lbl_desc.config(bg="#FFFFFF")
        lbl_action.config(bg="#FFFFFF", fg="#059669")

    def reset_card():
        is_opening[0] = False
        lbl_action.config(text="Open Tool →")
        if lbl_badge:
            lbl_badge.config(bg="#ECFDF5", fg="#059669")
        card.config(highlightbackground="#E5E7EB", highlightthickness=1, bg="#FFFFFF")
        top_frame.config(bg="#FFFFFF")
        lbl_title.config(bg="#FFFFFF", fg="#1F2937")
        lbl_desc.config(bg="#FFFFFF")
        lbl_action.config(bg="#FFFFFF", fg="#059669")

    def on_click(_e):
        if is_opening[0]:
            return
        is_opening[0] = True
        # Subtle, crisp opening press animation
        card.config(highlightbackground="#059669", highlightthickness=2, bg="#ECFDF5")
        top_frame.config(bg="#ECFDF5")
        lbl_title.config(bg="#ECFDF5", fg="#065F46")
        lbl_desc.config(bg="#ECFDF5")
        lbl_action.config(bg="#ECFDF5", fg="#047857", text="Opening... ➜")
        if lbl_badge:
            lbl_badge.config(bg="#D1FAE5", fg="#047857")

        def trigger():
            command()
            card.after(350, reset_card)

        card.after(60, trigger)

    for w in widgets_to_bind:
        w.bind("<Enter>", on_enter)
        w.bind("<Leave>", on_leave)
        w.bind("<Button-1>", on_click)

    return card