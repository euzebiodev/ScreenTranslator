"""Janela flutuante escura e semi-transparente com original/tradução lado a lado."""
import tkinter as tk

import settings
from screen_selector import virtual_screen_geometry

BG = "#181820"
PANEL_BG = "#22222e"
DIVIDER = "#33333f"
HEADER_FG = "#8b8ba0"
TEXT_FG = "#e8e8f0"
ACCENT = "#00c853"
ACCENT_HOVER = "#3ddc84"
CLOSE_FG = "#8b8ba0"
CLOSE_HOVER = "#ff5f56"
ALPHA = 0.95

MIN_WIDTH = 420
MIN_HEIGHT = 240
GRIP_SIZE = 14


def _clamp_position(x, y, width, height):
    vx, vy, vwidth, vheight = virtual_screen_geometry()
    x = max(vx, min(x, vx + vwidth - width))
    y = max(vy, min(y, vy + vheight - height))
    return x, y


def _make_draggable(win, handle):
    state = {"x": 0, "y": 0}

    def start(event):
        state["x"], state["y"] = event.x, event.y

    def move(event):
        win.geometry(f"+{win.winfo_x() + event.x - state['x']}+{win.winfo_y() + event.y - state['y']}")

    handle.bind("<ButtonPress-1>", start)
    handle.bind("<B1-Motion>", move)


def _make_resizable(win, grip):
    """Alça de redimensionamento no canto inferior direito.

    Necessária porque `overrideredirect(True)` remove as bordas nativas
    do Windows (e com elas, o redimensionamento padrão).
    """
    state = {}

    def start(event):
        state["x"] = event.x_root
        state["y"] = event.y_root
        state["w"] = win.winfo_width()
        state["h"] = win.winfo_height()

    def do_resize(event):
        new_w = max(MIN_WIDTH, state["w"] + (event.x_root - state["x"]))
        new_h = max(MIN_HEIGHT, state["h"] + (event.y_root - state["y"]))
        win.geometry(f"{new_w}x{new_h}")

    grip.bind("<ButtonPress-1>", start)
    grip.bind("<B1-Motion>", do_resize)


def _base_window(root, width, height, x, y):
    win = tk.Toplevel(root)
    win.overrideredirect(True)
    win.attributes("-topmost", True)
    win.attributes("-alpha", ALPHA)
    win.configure(bg=DIVIDER)

    win.update_idletasks()
    if x is not None and y is not None:
        x, y = _clamp_position(x, y, width, height)
    else:
        vx, vy, vwidth, vheight = virtual_screen_geometry()
        x = vx + (vwidth - width) // 2
        y = vy + (vheight - height) // 2
    win.geometry(f"{width}x{height}+{x}+{y}")
    win.bind("<Escape>", lambda e: win.destroy())

    grip = tk.Label(win, bg=DIVIDER, fg=HEADER_FG, text="⋰", cursor="size_nw_se")
    grip.place(relx=1.0, rely=1.0, anchor="se", width=GRIP_SIZE, height=GRIP_SIZE)
    grip.lift()
    _make_resizable(win, grip)

    return win


def _hover_label(parent, text, color, hover_color, command, font=("Segoe UI", 10, "bold")):
    label = tk.Label(
        parent, text=text, bg=BG, fg=color,
        font=font, padx=8, cursor="hand2",
    )
    label.bind("<Button-1>", lambda e: command())
    label.bind("<Enter>", lambda e: label.configure(fg=hover_color))
    label.bind("<Leave>", lambda e: label.configure(fg=color))
    return label


def _title_bar(win, title, on_decrease=None, on_increase=None):
    bar = tk.Frame(win, bg=BG, height=36)
    bar.pack(fill="x", side="top", padx=1, pady=(1, 0))
    bar.pack_propagate(False)

    tk.Label(
        bar, text=title, bg=BG, fg=TEXT_FG,
        font=("Segoe UI", 11, "bold"), padx=14,
    ).pack(side="left")

    close_btn = tk.Label(
        bar, text="✕", bg=BG, fg=CLOSE_FG,
        font=("Segoe UI", 13), padx=14, cursor="hand2",
    )
    close_btn.pack(side="right")
    close_btn.bind("<Enter>", lambda e: close_btn.configure(fg=CLOSE_HOVER))
    close_btn.bind("<Leave>", lambda e: close_btn.configure(fg=CLOSE_FG))
    close_btn.bind("<Button-1>", lambda e: win.destroy())

    if on_increase is not None:
        _hover_label(bar, "A+", TEXT_FG, ACCENT_HOVER, on_increase).pack(side="right")
    if on_decrease is not None:
        _hover_label(bar, "A-", TEXT_FG, ACCENT_HOVER, on_decrease).pack(side="right")

    _make_draggable(win, bar)
    return bar


def _text_panel(parent, label, content, on_copy, font_size):
    panel = tk.Frame(parent, bg=PANEL_BG)

    header = tk.Frame(panel, bg=PANEL_BG)
    header.pack(fill="x", padx=16, pady=(14, 6))
    tk.Label(
        header, text=label, bg=PANEL_BG, fg=HEADER_FG,
        font=("Segoe UI", 9, "bold"),
    ).pack(side="left")
    _hover_label(
        header, "COPIAR", ACCENT, ACCENT_HOVER, on_copy,
        font=("Segoe UI", 8, "bold"),
    ).pack(side="right")

    text_widget = tk.Text(
        panel, wrap="word", bg=PANEL_BG, fg=TEXT_FG,
        font=("Segoe UI", font_size), relief="flat", padx=16, pady=4,
        insertbackground=TEXT_FG, highlightthickness=0, bd=0,
    )
    text_widget.insert("1.0", content)
    text_widget.configure(state="disabled")
    text_widget.pack(fill="both", expand=True, padx=2, pady=(0, 14))

    panel.text_widget = text_widget
    return panel


def show_translation_window(root, original_text, translated_text, x=None, y=None):
    width, height = 680, 400
    win = _base_window(root, width, height, x, y)
    win.minsize(MIN_WIDTH, MIN_HEIGHT)

    font_size = {"value": settings.get_font_size()}
    panels = []

    def copy(text):
        win.clipboard_clear()
        win.clipboard_append(text)

    def apply_font_size():
        for panel in panels:
            panel.text_widget.configure(font=("Segoe UI", font_size["value"]))

    def change_font(delta):
        font_size["value"] = settings.set_font_size(font_size["value"] + delta)
        apply_font_size()

    _title_bar(
        win, "🌐  Tradução",
        on_decrease=lambda: change_font(-1),
        on_increase=lambda: change_font(1),
    )

    body = tk.Frame(win, bg=DIVIDER)
    body.pack(fill="both", expand=True, padx=1, pady=(0, 1))
    body.columnconfigure(0, weight=1)
    body.columnconfigure(1, weight=1)
    body.rowconfigure(0, weight=1)

    left = _text_panel(
        body, "TEXTO ORIGINAL · EN", original_text, lambda: copy(original_text),
        font_size["value"],
    )
    left.grid(row=0, column=0, sticky="nsew", padx=(0, 1))
    panels.append(left)

    right = _text_panel(
        body, "TRADUÇÃO · PT-BR", translated_text, lambda: copy(translated_text),
        font_size["value"],
    )
    right.grid(row=0, column=1, sticky="nsew", padx=(1, 0))
    panels.append(right)

    win.lift()
    win.focus_force()
    return win


def show_message_window(root, message, x=None, y=None):
    """Janela simples usada para erros ou avisos (ex: nenhum texto detectado)."""
    width, height = 400, 170
    win = _base_window(root, width, height, x, y)
    win.minsize(300, 140)
    _title_bar(win, "Screen Translator")

    body = tk.Frame(win, bg=PANEL_BG)
    body.pack(fill="both", expand=True, padx=1, pady=(0, 1))

    tk.Label(
        body, text=message, bg=PANEL_BG, fg=TEXT_FG,
        font=("Segoe UI", 11), wraplength=width - 40,
        justify="left", padx=18, pady=18,
    ).pack(fill="both", expand=True)

    win.lift()
    win.focus_force()
    return win
