"""Janela simples para consultar as traduções salvas no banco local."""
import tkinter as tk
from tkinter import ttk

import database


def show_history_window(root):
    win = tk.Toplevel(root)
    win.title("Histórico de Traduções")
    win.geometry("760x420")
    win.attributes("-topmost", True)

    search_frame = tk.Frame(win)
    search_frame.pack(fill="x", padx=10, pady=(10, 5))

    tk.Label(search_frame, text="Buscar:").pack(side="left")
    search_var = tk.StringVar()
    entry = tk.Entry(search_frame, textvariable=search_var)
    entry.pack(side="left", fill="x", expand=True, padx=(6, 6))

    columns = ("data", "original", "traducao")
    tree = ttk.Treeview(win, columns=columns, show="headings")
    tree.heading("data", text="Data")
    tree.heading("original", text="Original (EN)")
    tree.heading("traducao", text="Tradução (PT-BR)")
    tree.column("data", width=140, anchor="w")
    tree.column("original", width=280, anchor="w")
    tree.column("traducao", width=280, anchor="w")
    tree.pack(fill="both", expand=True, padx=10, pady=5)

    def reload(term=""):
        for row in tree.get_children():
            tree.delete(row)
        rows = database.search_translations(term) if term else database.list_translations()
        for _id, original, translated, _src, _tgt, created_at in rows:
            original_preview = original.replace("\n", " ")[:80]
            translated_preview = translated.replace("\n", " ")[:80]
            tree.insert("", "end", values=(created_at, original_preview, translated_preview))

    def on_search(*_args):
        reload(search_var.get().strip())

    search_var.trace_add("write", on_search)

    tk.Button(win, text="Fechar", command=win.destroy).pack(pady=(0, 10))

    reload()
    win.lift()
    win.focus_force()
    return win
