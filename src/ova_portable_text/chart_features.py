"""Typed semantic components introduced by report.v1.4."""

from __future__ import annotations

import calendar
import re
from datetime import date
from typing import Annotated, Literal

from pydantic import AfterValidator, BeforeValidator, Field, StrictStr, model_validator
from pydantic_core import PydanticCustomError

from .base import OvaBaseModel


def fail(path: str, message: str, code: str = "chart.invalid_value"):
    raise PydanticCustomError(code, "{path}: {message}", {"path": path, "message": message})


def nonblank(value: str) -> str:
    if not value.strip():
        raise ValueError("Expected a non-empty string.")
    return value


def number(value):
    import math

    if type(value) not in (int, float):
        raise ValueError("Expected a finite JSON number, not a string or boolean.")
    try:
        finite = math.isfinite(value)
    except OverflowError:
        finite = False
    if not finite:
        raise ValueError("Expected a finite JSON number.")
    return value


Key = Annotated[StrictStr, AfterValidator(nonblank)]
Number = Annotated[int | float, BeforeValidator(number)]
LanguageText = Annotated[dict[Key, Key], Field(min_length=1)]
DataRole = Literal["observed", "estimated", "forecast"]
DataBasis = Literal["evidence_based", "illustrative"]


class V14Component(OvaBaseModel):
    @model_validator(mode="before")
    @classmethod
    def omit_optional_nulls(cls, data):
        if isinstance(data, dict):
            for key, value in data.items():
                if value is None:
                    fail(key, "Omit optional fields instead of supplying null.")
        return data


class PartialDate(V14Component):
    value: StrictStr
    precision: Literal["year", "month", "day"]

    @model_validator(mode="after")
    def valid_date(self):
        patterns = {"year": r"\d{4}", "month": r"\d{4}-\d{2}", "day": r"\d{4}-\d{2}-\d{2}"}
        if not re.fullmatch(patterns[self.precision], self.value, flags=re.ASCII):
            fail("value", "Date format must match precision.")
        self.bounds()
        return self

    def bounds(self) -> tuple[date, date]:
        parts = [int(x) for x in self.value.split("-")]
        year = parts[0]
        month = parts[1] if len(parts) > 1 else 1
        day = parts[2] if len(parts) > 2 else 1
        start = date(year, month, day)
        if self.precision == "year":
            return start, date(year, 12, 31)
        if self.precision == "month":
            return start, date(year, month, calendar.monthrange(year, month)[1])
        return start, start


class TimelineEvent(V14Component):
    key: Key
    start: PartialDate
    label: LanguageText
    end: PartialDate | None = None
    description: LanguageText | None = None
    eventType: Key | None = None
    status: Literal["occurred", "ongoing", "planned", "cancelled"] | None = None

    @model_validator(mode="after")
    def interval(self):
        if self.end and (
            self.start.precision != self.end.precision or self.end.value < self.start.value
        ):
            fail("end", "End must have the same precision and not precede start.")
        return self


class Stage(V14Component):
    key: Key
    label: LanguageText
    description: LanguageText | None = None
    status: Literal["not_started", "in_progress", "completed", "blocked", "skipped"] | None = None


class FlowGroup(V14Component):
    key: Key
    label: LanguageText
    description: LanguageText | None = None


class FlowNode(FlowGroup):
    role: Literal["input", "process", "output"] | None = None
    groupKey: Key | None = None


class FlowEdge(V14Component):
    key: Key
    sourceKey: Key
    targetKey: Key
    label: LanguageText | None = None


class FunnelStage(FlowGroup):
    value: Number | None = None

    @model_validator(mode="after")
    def nonnegative(self):
        if self.value is not None and self.value < 0:
            fail("value", "Value must be nonnegative.")
        return self


class RangePoint(V14Component):
    key: Key
    categoryKey: Key
    low: Number
    high: Number
    center: Number | None = None
    label: LanguageText | None = None
    description: LanguageText | None = None
    dataRole: DataRole | None = None

    @model_validator(mode="after")
    def interval(self):
        if self.low > self.high:
            fail("high", "low must be <= high.")
        if self.center is not None and not self.low <= self.center <= self.high:
            fail("center", "center must lie within [low, high].")
        return self


class RangeSeries(V14Component):
    key: Key
    points: list[RangePoint] = Field(min_length=1)
    label: LanguageText | None = None
    description: LanguageText | None = None
    dataRole: DataRole | None = None


class AxisDomain(V14Component):
    min: Number
    max: Number

    @model_validator(mode="after")
    def ordered(self):
        if self.min >= self.max:
            fail("max", "domain.min must be < domain.max.")
        return self


class AxisTick(V14Component):
    value: Number
    label: LanguageText


class ReferenceLine(V14Component):
    key: Key
    axis: Literal["x", "y"]
    value: Number
    role: Literal["threshold", "target", "baseline"]
    label: LanguageText | None = None


class AxisBand(V14Component):
    key: Key
    axis: Literal["x", "y"]
    from_: Number = Field(alias="from")
    to: Number
    role: Literal["stage", "forecast", "assessment"]
    label: LanguageText | None = None

    @model_validator(mode="after")
    def ordered(self):
        if self.from_ >= self.to:
            fail("to", "band.from must be < band.to.")
        return self


class LineMarkerTarget(V14Component):
    seriesKey: Key
    pointKey: Key


class BarMarkerTarget(V14Component):
    seriesKey: Key
    categoryKey: Key


class RangeMarkerTarget(LineMarkerTarget):
    anchor: Literal["low", "high", "center"]


class ChartMarker(V14Component):
    key: Key
    target: LineMarkerTarget | BarMarkerTarget | RangeMarkerTarget
    role: Literal["current_position", "highlight"]
    label: LanguageText | None = None
    description: LanguageText | None = None


class ChartAnnotations(V14Component):
    referenceLines: list[ReferenceLine] | None = None
    bands: list[AxisBand] | None = None
    markers: list[ChartMarker] | None = None


class DoughnutCenterContent(V14Component):
    primary: LanguageText
    secondary: LanguageText | None = None


class ExtendedChartComponent(OvaBaseModel):
    """Strictness is scoped to added fields, never to every legacy field."""

    @model_validator(mode="before")
    @classmethod
    def validate_added_fields(cls, data):
        if not isinstance(data, dict):
            return data
        if "series" in data:
            from .chart_semantics import validate_cartesian_input

            validate_cartesian_input(data)
        if "dataRole" in data:
            for field in ("value", "yValue"):
                if field in data:
                    number(data[field])
        new_fields = {
            "dataRole",
            "dataBasis",
            "annotations",
            "normalization",
            "centerContent",
            "domain",
            "ticks",
        }
        for key in new_fields & data.keys():
            if data[key] is None:
                fail(key, "Omit optional fields instead of supplying null.")
        return data
