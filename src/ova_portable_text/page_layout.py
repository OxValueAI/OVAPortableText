"""Opt-in report.v1.6 layout contracts; no physical page layout is performed here."""

from typing import Literal

from pydantic import model_validator

from .base import OvaBaseModel
from .chart_features import Key, fail


class LayoutComponent(OvaBaseModel):
    @model_validator(mode="before")
    @classmethod
    def reject_nulls(cls, value):
        if isinstance(value, dict):
            for key, item in value.items():
                if item is None:
                    fail(
                        key,
                        "Omit optional layout fields instead of supplying null.",
                        "layout.invalid_value",
                    )
        return value


class PageSettings(LayoutComponent):
    orientation: Literal["portrait", "landscape"]


class ObjectPagination(LayoutComponent):
    pageBreakBefore: Literal["auto", "always"] = "auto"
    pageBreakAfter: Literal["auto", "always"] = "auto"


class CellAlignment(LayoutComponent):
    align: Literal["left", "center", "right"] | None = None
    verticalAlign: Literal["top", "middle", "bottom"] | None = None


class CaptionBinding(LayoutComponent):
    targetRef: Key
    position: Literal["before", "after"]


def page_settings(orientation: str = "portrait") -> PageSettings:
    return PageSettings(orientation=orientation)


def object_pagination(
    *, page_break_before: str = "auto", page_break_after: str = "auto"
) -> ObjectPagination:
    return ObjectPagination(pageBreakBefore=page_break_before, pageBreakAfter=page_break_after)


def cell_alignment(*, align: str | None = None, vertical_align: str | None = None) -> CellAlignment:
    return CellAlignment(
        **{
            k: v
            for k, v in {"align": align, "verticalAlign": vertical_align}.items()
            if v is not None
        }
    )


def caption_binding(*, target_ref: str, position: str) -> CaptionBinding:
    return CaptionBinding(targetRef=target_ref, position=position)
