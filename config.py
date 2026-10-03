"""Configurações globais do Screen Translator."""
import os
import sys

FROZEN = getattr(sys, "frozen", False)

if FROZEN:
    # Executável empacotado (PyInstaller/instalador): dados do usuário ficam
    # em %APPDATA%, já que a pasta de instalação (Program Files) normalmente
    # não é gravável sem privilégios de administrador.
    BASE_DIR = os.path.join(os.environ["APPDATA"], "ScreenTranslator")
    # Tesseract vem embutido ao lado do .exe (pasta "tesseract").
    TESSERACT_CMD = os.path.join(os.path.dirname(sys.executable), "tesseract", "tesseract.exe")
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # Caminho do executável do Tesseract OCR no Windows em modo desenvolvimento.
    # Baixe em: https://github.com/UB-Mannheim/tesseract/wiki
    # Ajuste este caminho se instalar em outro diretório.
    TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Atalho global para iniciar a seleção de área da tela.
# Sintaxe conforme a lib `keyboard` (ex: "ctrl+alt+t", "ctrl+shift+q").
HOTKEY = "ctrl+alt+t"

# Idiomas padrão de tradução (código ISO usado pelo deep-translator).
SOURCE_LANG = "en"
TARGET_LANG = "pt"

# Servidor local do LibreTranslate, usado como alternativa (fallback)
# quando o Google Translate falhar (rate limit, sem internet, etc).
# Precisa terminar com "/". Deixe None para desativar esse fallback.
LIBRETRANSLATE_URL = "http://localhost:5000/"

# Banco de dados local (SQLite) onde todas as traduções ficam gravadas.
DB_PATH = os.path.join(BASE_DIR, "data", "translations.db")

# Tempo (segundos) que o botão flutuante de tradução fica visível
# na tela antes de desaparecer sozinho, caso o usuário não clique.
BUTTON_TIMEOUT = 8
