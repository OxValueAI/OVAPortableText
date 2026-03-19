from __future__ import annotations

from .content import TextBlock
from .document import Document, DocumentMeta


def create_document(*, title: str, language: str, **meta_fields) -> Document:
    meta = DocumentMeta(title=title, language=language, **meta_fields)
    return Document(meta=meta)


def paragraph(text: str, *, style: str = "normal") -> TextBlock:
    return TextBlock.paragraph(text, style=style)
