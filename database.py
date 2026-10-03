"""Camada de acesso ao banco de dados local (SQLite).

O arquivo gerado em `data/translations.db` é um banco SQLite padrão e
pode ser aberto/consultado por qualquer ferramenta compatível, como o
DB Browser for SQLite (https://sqlitebrowser.org/) ou via `sqlite3` no
terminal, sem depender desta aplicação.
"""
import sqlite3
import os
from datetime import datetime

import config


def _connect():
    os.makedirs(os.path.dirname(config.DB_PATH), exist_ok=True)
    conn = sqlite3.connect(config.DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS translations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_text TEXT NOT NULL,
            translated_text TEXT NOT NULL,
            source_lang TEXT NOT NULL,
            target_lang TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    return conn


def init_db():
    conn = _connect()
    conn.close()


def save_translation(original_text, translated_text,
                      source_lang=None, target_lang=None):
    """Grava um registro de tradução e retorna o id inserido."""
    source_lang = source_lang or config.SOURCE_LANG
    target_lang = target_lang or config.TARGET_LANG
    conn = _connect()
    try:
        cur = conn.execute(
            "INSERT INTO translations "
            "(original_text, translated_text, source_lang, target_lang, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (original_text, translated_text, source_lang, target_lang,
             datetime.now().isoformat(timespec="seconds")),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def list_translations(limit=200):
    """Retorna as traduções mais recentes primeiro."""
    conn = _connect()
    try:
        cur = conn.execute(
            "SELECT id, original_text, translated_text, source_lang, "
            "target_lang, created_at FROM translations "
            "ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        return cur.fetchall()
    finally:
        conn.close()


def search_translations(term, limit=200):
    """Busca por trecho no texto original ou traduzido."""
    conn = _connect()
    try:
        like = f"%{term}%"
        cur = conn.execute(
            "SELECT id, original_text, translated_text, source_lang, "
            "target_lang, created_at FROM translations "
            "WHERE original_text LIKE ? OR translated_text LIKE ? "
            "ORDER BY id DESC LIMIT ?",
            (like, like, limit),
        )
        return cur.fetchall()
    finally:
        conn.close()
