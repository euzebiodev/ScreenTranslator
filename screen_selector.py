"""Overlay de tela cheia para o usuário selecionar uma área com o mouse."""
import ctypes
import tkinter as tk


def virtual_screen_geometry():
    """Retorna (x, y, largura, altura) cobrindo todos os monitores."""
    user32 = ctypes.windll.user32
    SM_XVIRTUALSCREEN = 76
    SM_YVIRTUALSCREEN = 77
    SM_CXVIRTUALSCREEN = 78
    SM_CYVIRTUALSCREEN = 79
    x = user32.GetSystemMetrics(SM_XVIRTUALSCREEN)
    y = user32.GetSystemMetrics(SM_YVIRTUALSCREEN)
    width = user32.GetSystemMetrics(SM_CXVIRTUALSCREEN)
    height = user32.GetSystemMetrics(SM_CYVIRTUALSCREEN)
    return x, y, width, height


def select_region():
    """Abre um overlay e bloqueia até o usuário selecionar uma área.

    Retorna uma tupla (x1, y1, x2, y2) em coordenadas absolutas de tela,
    ou None se o usuário cancelar (tecla Esc).
    """
    vx, vy, vwidth, vheight = virtual_screen_geometry()

    result = {"bbox": None}

    overlay = tk.Toplevel()
    overlay.geometry(f"{vwidth}x{vheight}+{vx}+{vy}")
    overlay.overrideredirect(True)
    overlay.attributes("-alpha", 0.25)
    overlay.attributes("-topmost", True)
    overlay.configure(bg="black")
    overlay.config(cursor="crosshair")
    overlay.focus_force()

    canvas = tk.Canvas(overlay, bg="black", highlightthickness=0, cursor="crosshair")
    canvas.pack(fill="both", expand=True)

    start = {"x": 0, "y": 0}
    rect_id = {"id": None}

    def on_press(event):
        start["x"], start["y"] = event.x, event.y
        if rect_id["id"] is not None:
            canvas.delete(rect_id["id"])
        rect_id["id"] = canvas.create_rectangle(
            event.x, event.y, event.x, event.y,
            outline="#00c853", width=2,
        )

    def on_drag(event):
        if rect_id["id"] is not None:
            canvas.coords(rect_id["id"], start["x"], start["y"], event.x, event.y)

    def on_release(event):
        x1, y1 = start["x"], start["y"]
        x2, y2 = event.x, event.y
        x1, x2 = sorted((x1, x2))
        y1, y2 = sorted((y1, y2))
        if x2 - x1 > 3 and y2 - y1 > 3:
            # Converte de coordenadas do overlay para coordenadas absolutas.
            result["bbox"] = (vx + x1, vy + y1, vx + x2, vy + y2)
        overlay.destroy()

    def on_cancel(event=None):
        result["bbox"] = None
        overlay.destroy()

    canvas.bind("<ButtonPress-1>", on_press)
    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<ButtonRelease-1>", on_release)
    overlay.bind("<Escape>", on_cancel)

    overlay.grab_set()
    overlay.wait_window()

    return result["bbox"]
