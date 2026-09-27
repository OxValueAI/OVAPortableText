"""Semantic values for the report.v1.5 valuation-result banner."""

from typing import Annotated, Literal

from pydantic import Field, model_validator

from .chart_features import Number, V14Component, fail


class ValuationPoint(V14Component):
    kind: Literal["point"] = "point"
    value: Number


class ValuationRange(V14Component):
    kind: Literal["range"] = "range"
    low: Number
    high: Number

    @model_validator(mode="after")
    def ordered(self):
        if self.low > self.high:
            fail("high", "Valuation low must be <= high.")
        return self


ValuationAmount = Annotated[ValuationPoint | ValuationRange, Field(discriminator="kind")]
