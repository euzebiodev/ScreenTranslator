"""Captura de imagem de uma região da tela."""
from PIL import ImageGrab


def capture_region(bbox):
    """bbox = (x1, y1, x2, y2) em coordenadas absolutas de tela."""
    return ImageGrab.grab(bbox=bbox, all_screens=True)
