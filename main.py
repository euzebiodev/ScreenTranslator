"""Screen Translator — ponto de entrada da aplicação.

Fluxo:
1. Usuário pressiona o atalho global (config.HOTKEY).
2. Uma sobreposição de tela permite selecionar uma área com o mouse.
3. Um botão flutuante "Traduzir" aparece no canto da seleção.
4. Ao clicar, a área é lida via OCR, traduzida (EN -> PT) e exibida em
   uma janela com o texto original e a tradução.
5. Cada tradução é salva no banco local SQLite (data/translations.db).
"""
import os
import queue
import sys
import threading
import tkinter as tk

import keyboard
import pystray
from PIL import Image

import config
import capture
import database
import ocr
import screen_selector
import translator
from ui.floating_button import show_floating_button
from ui.history_window import show_history_window
from ui.thread_utils import run_in_background
from ui.translation_window import show_message_window, show_translation_window

trigger_queue: "queue.Queue[str]" = queue.Queue()


def _do_ocr_and_translate(image):
    text = ocr.extract_text(image)
    if not text:
        return "", ""
    translated = translator.translate_text(text)
    database.save_translation(text, translated)
    return text, translated


def _show_toast(root, x, y, text):
    toast = tk.Toplevel(root)
    toast.overrideredirect(True)
    toast.attributes("-topmost", True)
    toast.configure(bg="#1b1b1b")
    tk.Label(
        toast, text=text, bg="#1b1b1b", fg="white",
        font=("Segoe UI", 9), padx=10, pady=6,
    ).pack()
    toast.update_idletasks()
    toast.geometry(f"{toast.winfo_width()}x{toast.winfo_height()}+{x}+{y}")
    return toast


def _process_selection(root, image, x, y):
    toast = _show_toast(root, x, y, "Traduzindo...")

    def on_done(result):
        toast.destroy()
        text, translated = result
        if not text:
            show_message_window(
                root, "Nenhum texto foi detectado na área selecionada.", x, y
            )
        else:
            show_translation_window(root, text, translated, x, y)

    def on_error(exc):
        toast.destroy()
        show_message_window(root, f"Erro ao traduzir:\n{exc}", x, y)

    run_in_background(root, lambda: _do_ocr_and_translate(image), on_done, on_error)


def _start_selection_flow(root):
    bbox = screen_selector.select_region()
    if bbox is None:
        return
    x1, y1, x2, y2 = bbox
    image = capture.capture_region(bbox)
    show_floating_button(
        root, x2 + 8, y2 + 8,
        on_click=lambda: _process_selection(root, image, x2 + 8, y2 + 8),
    )


def _poll_queue(root):
    try:
        while True:
            trigger_queue.get_nowait()
            _start_selection_flow(root)
    except queue.Empty:
        pass
    root.after(150, _poll_queue, root)


_BASE_PATH = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
ICON_PATH = os.path.join(_BASE_PATH, "assets", "icon.png")


def _make_tray_icon():
    return Image.open(ICON_PATH)


def _run_tray(root):
    def on_translate(icon, item):
        trigger_queue.put("go")

    def on_history(icon, item):
        root.after(0, lambda: show_history_window(root))

    def on_quit(icon, item):
        icon.stop()
        keyboard.unhook_all_hotkeys()
        root.after(0, root.quit)

    menu = pystray.Menu(
        pystray.MenuItem("Selecionar área e traduzir", on_translate, default=True),
        pystray.MenuItem("Histórico de traduções", on_history),
        pystray.MenuItem("Sair", on_quit),
    )
    icon = pystray.Icon("ScreenTranslator", _make_tray_icon(), "Screen Translator", menu)
    icon.run()


def main():
    database.init_db()

    root = tk.Tk()
    root.withdraw()  # não mostramos uma janela principal, só o tray + popups
    try:
        root.iconbitmap(os.path.join(os.path.dirname(ICON_PATH), "icon.ico"))
    except tk.TclError:
        pass  # segue sem ícone de janela se o .ico não puder ser carregado

    keyboard.add_hotkey(config.HOTKEY, lambda: trigger_queue.put("go"))

    tray_thread = threading.Thread(target=_run_tray, args=(root,), daemon=True)
    tray_thread.start()

    print(f"Screen Translator rodando. Atalho: {config.HOTKEY}. "
          f"Use o ícone na bandeja do sistema para sair.")

    root.after(150, _poll_queue, root)
    root.mainloop()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
