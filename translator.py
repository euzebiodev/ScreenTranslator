"""Tradução de texto com fallback entre múltiplos serviços.

Ordem de tentativa: Google Translate -> MyMemory -> LibreTranslate local.
Se um serviço falhar (rate limit, sem internet, servidor fora do ar), o
próximo da lista é tentado automaticamente antes de reportar erro.
"""
import truststore
truststore.inject_into_ssl()  # usa o repositório de certificados do Windows
                               # (necessário quando antivírus/proxy fazem
                               # inspeção SSL, ex: Norton Web/Mail Shield)

from deep_translator import GoogleTranslator, LibreTranslator, MyMemoryTranslator

import config

# O MyMemory não aceita códigos ISO simples ("en", "pt"), apenas nomes
# completos ou códigos regionais (ex: "en-GB", "pt-BR").
_MYMEMORY_LANG_MAP = {"en": "en-GB", "pt": "pt-BR"}


def _restore_case(original, translated):
    """Reaplica o padrão de caixa do texto original no texto traduzido."""
    if not translated:
        return translated
    if original.isupper():
        return translated.upper()
    if original.istitle():
        return translated.title()
    return translated


class _CaseNormalizedEngine:
    """Contorna modelos que traduzem mal texto em CAIXA ALTA/Title Case —
    muito comum em capturas de tela (títulos, botões). O modelo local do
    LibreTranslate, por exemplo, chega a descartar palavras nesses casos
    ("FUTURE BOY" -> "FUTURO"). Aqui traduzimos em minúsculas e reaplicamos
    o padrão de caixa original no resultado.
    """

    def __init__(self, engine):
        self._engine = engine

    def translate(self, text):
        result = self._engine.translate(text.lower())
        return _restore_case(text, result)


def _build_engines(source, target):
    """Monta a lista de motores de tradução, na ordem de prioridade."""
    engines = [("Google Translate", GoogleTranslator(source=source, target=target))]

    try:
        mymemory_source = _MYMEMORY_LANG_MAP.get(source, source)
        mymemory_target = _MYMEMORY_LANG_MAP.get(target, target)
        engines.append((
            "MyMemory",
            MyMemoryTranslator(source=mymemory_source, target=mymemory_target),
        ))
    except Exception:  # noqa: BLE001
        pass

    if config.LIBRETRANSLATE_URL:
        try:
            libre = LibreTranslator(
                source=source,
                target=target,
                api_key="not-needed",
                custom_url=config.LIBRETRANSLATE_URL,
            )
            engines.append(("LibreTranslate (local)", _CaseNormalizedEngine(libre)))
        except Exception:  # noqa: BLE001
            pass  # se não conseguir configurar, apenas segue sem esse fallback

    return engines


def _translate_paragraph(engines, paragraph):
    errors = []
    for name, engine in engines:
        try:
            result = engine.translate(paragraph)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{name}: {exc}")
            continue
        if result:
            return result
        # Alguns serviços retornam vazio/None quando o texto já está no
        # idioma de destino ou é curto demais para traduzir de fato.
        errors.append(f"{name}: resposta vazia")
    raise RuntimeError(
        "Todos os serviços de tradução falharam:\n" + "\n".join(errors)
    )


def translate_text(text, source=None, target=None):
    source = source or config.SOURCE_LANG
    target = target or config.TARGET_LANG
    text = text.strip()
    if not text:
        return ""

    engines = _build_engines(source, target)

    # Enviamos o texto inteiro de uma vez (e não linha a linha) para que o
    # tradutor tenha o contexto completo da frase — capturas de tela
    # costumam quebrar linha no meio de uma frase, e traduzir cada linha
    # isoladamente perde essa continuação (ex: "...through\nthe continuum"
    # vira uma tradução truncada se "through" for traduzido sem saber o que
    # vem a seguir).
    return _translate_paragraph(engines, text)
