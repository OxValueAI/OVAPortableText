from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class OvaBaseModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    def to_dict(self, *, exclude_none: bool = True) -> dict:
        return self.model_dump(by_alias=True, exclude_none=exclude_none)

    def to_json(self, *, indent: int | None = 2, exclude_none: bool = True) -> str:
        return self.model_dump_json(by_alias=True, exclude_none=exclude_none, indent=indent)
