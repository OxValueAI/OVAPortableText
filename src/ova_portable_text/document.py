from __future__ import annotations

from typing import Any

from pydantic import Field

from .base import OvaBaseModel
from .section import Section


class DocumentMeta(OvaBaseModel):
    title: str | None = None
    subtitle: str | None = None
    language: str | None = None
    author: str | None = None
    date: str | None = None
    reportNumber: str | None = None
    documentType: str | None = None
    confidentiality: str | None = None
    generatedBy: str | None = None
    generatedAt: str | None = None
    clientId: str | None = None
    projectId: str | None = None


class AssetsRegistry(OvaBaseModel):
    images: list[dict[str, Any]] = Field(default_factory=list)
    logos: list[dict[str, Any]] = Field(default_factory=list)
    backgrounds: list[dict[str, Any]] = Field(default_factory=list)
    icons: list[dict[str, Any]] = Field(default_factory=list)
    attachments: list[dict[str, Any]] = Field(default_factory=list)


class DatasetsRegistry(OvaBaseModel):
    charts: list[dict[str, Any]] = Field(default_factory=list)
    tables: list[dict[str, Any]] = Field(default_factory=list)
    metrics: list[dict[str, Any]] = Field(default_factory=list)


class Document(OvaBaseModel):
    schemaVersion: str = "report.v1"
    meta: DocumentMeta = Field(default_factory=DocumentMeta)
    theme: dict[str, Any] = Field(default_factory=dict)
    assets: AssetsRegistry = Field(default_factory=AssetsRegistry)
    datasets: DatasetsRegistry = Field(default_factory=DatasetsRegistry)
    bibliography: list[dict[str, Any]] = Field(default_factory=list)
    footnotes: list[dict[str, Any]] = Field(default_factory=list)
    glossary: list[dict[str, Any]] = Field(default_factory=list)
    sections: list[Section] = Field(default_factory=list)

    def append_section(self, section: Section) -> "Document":
        self.sections.append(section)
        return self
