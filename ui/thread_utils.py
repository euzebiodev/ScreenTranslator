"""Executa tarefas em background sem travar a interface do Tkinter."""
import threading


def run_in_background(root, target, on_done, on_error=None):
    """Roda `target()` em uma thread separada.

    `on_done(result)` é chamado de volta na thread principal do Tkinter
    (via root.after) quando `target` terminar com sucesso.
    """

    def worker():
        try:
            result = target()
        except Exception as exc:  # noqa: BLE001
            if on_error is not None:
                root.after(0, lambda: on_error(exc))
            return
        root.after(0, lambda: on_done(result))

    threading.Thread(target=worker, daemon=True).start()
