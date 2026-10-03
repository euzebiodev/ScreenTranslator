# Screen Translator

Ferramenta para Windows que permite selecionar qualquer parte da tela com
um atalho de teclado + mouse, extrair o texto por OCR e traduzir
automaticamente de inglês para português. Todas as traduções ficam
registradas em um banco de dados local (SQLite).

## Como funciona

1. Pressione o atalho global (padrão: `Ctrl+Alt+T`).
2. A tela escurece levemente; arraste o mouse para selecionar a área
   desejada (funciona com uma palavra, uma frase ou um parágrafo inteiro).
3. Um botão **🌐 Traduzir** aparece no canto da seleção.
4. Ao clicar, abre uma janela mostrando o texto original em inglês e,
   logo abaixo, a tradução em português.
5. O par (original + tradução) é salvo automaticamente em
   `data/translations.db`.
6. Pelo ícone na bandeja do sistema (system tray) você também pode abrir
   o **Histórico de traduções** ou **Sair** da aplicação.

## Pré-requisitos

### 1. Python 3.10+
Já disponível neste ambiente (`python --version`).

### 2. Tesseract OCR (motor de reconhecimento de texto)
O `pytesseract` é apenas um wrapper — é necessário instalar o executável:

- Baixe o instalador em: https://github.com/UB-Mannheim/tesseract/wiki
- Instale normalmente (padrão: `C:\Program Files\Tesseract-OCR\`).
- Se instalar em outro caminho, ajuste `TESSERACT_CMD` em [config.py](config.py).

### 3. Dependências Python

```powershell
pip install -r requirements.txt
```

## Executando

```powershell
python main.py
```

O processo fica rodando em segundo plano (ícone na bandeja do sistema).
Pressione `Ctrl+Alt+T` em qualquer lugar da tela para iniciar uma seleção.

> **Observação:** a lib `keyboard`, usada para o atalho global, pode exigir
> que o terminal seja executado **como Administrador** em alguns sistemas
> Windows para capturar teclas globalmente.

## Configurações

Edite [config.py](config.py) para ajustar:

- `HOTKEY` — combinação de teclas (padrão `ctrl+alt+t`).
- `TESSERACT_CMD` — caminho do executável do Tesseract.
- `SOURCE_LANG` / `TARGET_LANG` — idiomas de origem/destino (`en` → `pt`).
- `LIBRETRANSLATE_URL` — endereço do seu servidor LibreTranslate local, usado
  como fallback (padrão `http://localhost:5000/`). Coloque `None` para desativar.
- `DB_PATH` — local do banco SQLite.
- `BUTTON_TIMEOUT` — tempo (segundos) que o botão de tradução fica visível.

## Tradução com fallback automático

A tradução tenta os serviços nesta ordem, passando para o próximo
automaticamente se o anterior falhar (rate limit, sem internet, servidor fora
do ar):

1. **Google Translate** (via `deep-translator`, gratuito, sem configuração).
2. **MyMemory** — gratuito, sem servidor próprio necessário.
3. **LibreTranslate local** — usa o servidor configurado em
   `LIBRETRANSLATE_URL`. Não precisa de API key se seu servidor rodar com
   autenticação desativada. Fica por último porque o modelo local (pelo
   menos o padrão do LibreTranslate self-hosted) traduz mal texto em CAIXA
   ALTA/Title Case — muito comum em capturas de tela (títulos, botões) —
   chegando a descartar palavras (ex: "FUTURE BOY" virava só "FUTURO"). Por
   isso, ao usar esse serviço o texto é traduzido em minúsculas e o padrão
   de caixa original é reaplicado no resultado.

Se todos falharem, a janela de erro mostra o motivo de cada um.

## Banco de dados

As traduções ficam em `data/translations.db`, um banco **SQLite padrão**.
Pode ser consultado por qualquer ferramenta compatível, por exemplo:

- [DB Browser for SQLite](https://sqlitebrowser.org/) (interface gráfica)
- `sqlite3 data/translations.db` (linha de comando)

Tabela `translations`:

| coluna           | descrição                              |
|------------------|-----------------------------------------|
| id               | identificador único                     |
| original_text    | texto extraído via OCR (inglês)         |
| translated_text  | texto traduzido (português)             |
| source_lang      | idioma de origem (ex: `en`)              |
| target_lang      | idioma de destino (ex: `pt`)             |
| created_at       | data/hora da tradução                   |

A própria aplicação também tem um visualizador simples de histórico
(menu da bandeja → "Histórico de traduções"), com busca por texto.

## Estrutura do projeto

```
ScreenTranslator/
├── main.py                 # ponto de entrada, atalho global, tray icon
├── config.py                # configurações (atalho, idiomas, caminhos)
├── screen_selector.py       # overlay de seleção de área da tela
├── capture.py                # captura de imagem da área selecionada
├── ocr.py                    # extração de texto via Tesseract
├── translator.py             # tradução via Google Translate
├── database.py               # persistência em SQLite
├── ui/
│   ├── floating_button.py    # botão "Traduzir" que aparece na seleção
│   ├── translation_window.py # janela com original + tradução
│   ├── history_window.py     # consulta ao histórico salvo
│   └── thread_utils.py       # roda OCR/tradução sem travar a interface
└── data/
    └── translations.db       # gerado automaticamente na primeira execução
```

## Gerando o instalador Windows (.exe)

O projeto pode ser empacotado como um instalador Windows autossuficiente —
não exige Python nem Tesseract instalados na máquina de destino, tudo vai
embutido.

Pré-requisitos (só na máquina que vai **gerar** o instalador):

```powershell
pip install pyinstaller
winget install UB-Mannheim.TesseractOCR
winget install JRSoftware.InnoSetup
```

Gerar o instalador:

```powershell
powershell -ExecutionPolicy Bypass -File packaging\build_installer.ps1
```

O script faz tudo automaticamente:
1. Empacota `main.py` + todas as dependências Python com PyInstaller
   (`dist\ScreenTranslator\`).
2. Copia o Tesseract OCR (apenas os arquivos necessários para OCR em
   inglês — reduzido de ~239 MB para ~120 MB) para dentro dessa pasta.
3. Compila `packaging\installer.iss` com o Inno Setup, gerando
   `packaging\output\ScreenTranslator-Setup-<versão>.exe`.

No computador do usuário final, o instalador cria atalhos no Menu Iniciar
(e, opcionalmente, na Área de Trabalho) e um desinstalador. O app rodando
via instalador salva o banco de dados e preferências em
`%APPDATA%\ScreenTranslator\` (em vez da pasta `data/` do projeto, usada
apenas em modo desenvolvimento).

## Possíveis evoluções futuras

- Suporte a outros pares de idiomas (a lib `deep-translator` já suporta
  dezenas de idiomas — bastaria expor a escolha na interface).
- Tradução 100% offline com [argos-translate](https://github.com/argosopentech/argos-translate),
  sem depender do Google Translate.
- Atalho configurável pela interface, sem editar `config.py`.
