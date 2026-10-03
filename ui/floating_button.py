"""Botão flutuante que aparece no local onde o usuário selecionou a tela."""
import tkinter as tk

import config


def show_floating_button(root, x, y, on_click):
    """Cria um botão pequeno, sem bordas, sempre no topo, na posição (x, y).

    `on_click()` é chamado quando o usuário clica no botão. O botão se
    fecha sozinho após config.BUTTON_TIMEOUT segundos caso não seja clicado.
    """
    popup = tk.Toplevel(root)
    popup.overrideredirect(True)
    popup.attributes("-topmost", True)
    popup.configure(bg="#1b1b1b")

    def handle_click():
        popup.destroy()
        on_click()

    btn = tk.Button(
        popup,
        text="🌐 Traduzir",
        command=handle_click,
        bg="#00c853",
        fg="white",
        activebackground="#00a344",
        activeforeground="white",
        relief="flat",
        padx=10,
        pady=4,
        font=("Segoe UI", 9, "bold"),
        cursor="hand2",
    )
    btn.pack()

    popup.update_idletasks()
    width = popup.winfo_width()
    height = popup.winfo_height()
    popup.geometry(f"{width}x{height}+{x}+{y}")

    popup.after(config.BUTTON_TIMEOUT * 1000, popup.destroy)
    return popup
