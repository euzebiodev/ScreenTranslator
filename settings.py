"""Preferências de interface persistidas localmente (ex: tamanho da fonte).

Guardadas em um JSON simples ao lado do banco de dados, separado de
`config.py` (que é editado manualmente pelo usuário).
"""
import json
import os

import config

SETTINGS_PATH = os.path.join(os.path.dirname(config.DB_PATH), "ui_settings.json")

DEFAULT_FONT_SIZE = 13
MIN_FONT_SIZE = 9
MAX_FONT_SIZE = 24


def _load():
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save(data):
    os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f)


def get_font_size():
    return _load().get("font_size", DEFAULT_FONT_SIZE)


def set_font_size(size):
    size = max(MIN_FONT_SIZE, min(MAX_FONT_SIZE, size))
    data = _load()
    data["font_size"] = size
    _save(data)
    return size
