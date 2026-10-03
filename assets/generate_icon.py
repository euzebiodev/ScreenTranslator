"""Gera o ícone do Screen Translator (assets/icon.ico e assets/icon.png).

Desenho: globo verde (idêntico à paleta usada nas janelas do app) com um
símbolo de "traduzir" (duas setas formando um ciclo) sobreposto, em um
fundo quadrado arredondado escuro. Rode novamente após qualquer ajuste
de cores para regenerar os arquivos finais.
"""
import math
import os

from PIL import Image, ImageDraw

BG = (24, 24, 32, 255)        # mesmo "BG" das janelas (#181820)
ACCENT = (0, 200, 83, 255)    # mesmo "ACCENT" das janelas (#00c853)
WHITE = (232, 232, 240, 255)  # mesmo "TEXT_FG" das janelas (#e8e8f0)

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
SIZE = 256  # desenhado em alta resolução; o .ico reduz para os demais tamanhos


def _rounded_square(size, radius, fill):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=fill)
    return img


def _draw_globe(draw, cx, cy, r):
    r = int(r)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=ACCENT)

    # "meridianos" (linhas de longitude) como elipses mais estreitas
    line_width = max(2, r // 22)
    for scale in (0.5, 1.0):
        dx = int(r * scale)
        draw.ellipse(
            [cx - dx, cy - r, cx + dx, cy + r],
            outline=BG, width=line_width,
        )
    # "paralelo" (linha de latitude) horizontal
    draw.line([cx - r, cy, cx + r, cy], fill=BG, width=line_width)


def _draw_translate_arrows(draw, cx, cy, r):
    """Duas setas curvas formando um ciclo, símbolo universal de tradução."""
    width = max(3, int(r) // 10)

    def arc_with_arrowhead(bbox, start, end, color):
        draw.arc(bbox, start=start, end=end, fill=color, width=width)
        end_rad = math.radians(end)
        ax = (bbox[0] + bbox[2]) / 2 + (bbox[2] - bbox[0]) / 2 * math.cos(end_rad)
        ay = (bbox[1] + bbox[3]) / 2 + (bbox[3] - bbox[1]) / 2 * math.sin(end_rad)
        tangent = end_rad + math.pi / 2
        size = width * 1.8
        p1 = (ax + size * math.cos(tangent), ay + size * math.sin(tangent))
        p2 = (ax - size * math.cos(end_rad + 0.5), ay - size * math.sin(end_rad + 0.5))
        p3 = (ax - size * math.cos(end_rad - 0.5), ay - size * math.sin(end_rad - 0.5))
        draw.polygon([p1, p2, p3], fill=color)

    badge_r = r * 0.62
    bbox = [int(cx - badge_r), int(cy - badge_r), int(cx + badge_r), int(cy + badge_r)]
    arc_with_arrowhead(bbox, 200, 340, WHITE)
    arc_with_arrowhead(bbox, 20, 160, WHITE)


def build_icon():
    size = SIZE
    radius = size // 5
    img = _rounded_square(size, radius, BG)
    draw = ImageDraw.Draw(img)

    cx, cy = size // 2, int(size * 0.46)
    globe_r = size * 0.34
    _draw_globe(draw, cx, cy, globe_r)

    # selo branco no canto inferior direito com as setas de "traduzir"
    badge_cx, badge_cy = int(size * 0.74), int(size * 0.76)
    badge_r = int(size * 0.22)
    draw.ellipse(
        [badge_cx - badge_r, badge_cy - badge_r, badge_cx + badge_r, badge_cy + badge_r],
        fill=BG, outline=WHITE, width=max(2, size // 64),
    )
    _draw_translate_arrows(draw, badge_cx, badge_cy, badge_r * 0.78)

    return img


def main():
    icon = build_icon()
    png_path = os.path.join(OUT_DIR, "icon.png")
    ico_path = os.path.join(OUT_DIR, "icon.ico")

    icon.save(png_path)
    sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    icon.save(ico_path, format="ICO", sizes=sizes)
    print(f"Gerado: {png_path}")
    print(f"Gerado: {ico_path}")


if __name__ == "__main__":
    main()
