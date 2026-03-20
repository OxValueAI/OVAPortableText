from __future__ import annotations

"""
Base model infrastructure for OVAPortableText.
OVAPortableText 的基础模型设施。

This module contains the common base class used by almost all public models.
本模块包含几乎所有公开模型都会继承的公共基类。
"""

from pathlib import Path
from typing import Any, TypeVar

from pydantic import BaseModel, ConfigDict

ModelT = TypeVar("ModelT", bound="OvaBaseModel")


class OvaBaseModel(BaseModel):
    """
    Common base model for all OVAPortableText models.
    OVAPortableText 所有模型共用的基础类。

    Design goals / 设计目标：
    1. Forbid unexpected fields by default, so protocol mistakes are caught early.
       默认禁止未声明字段，尽早暴露协议拼写或结构错误。
    2. Allow population by alias, because Portable Text uses `_type`.
       允许通过别名赋值，因为 Portable Text 使用 `_type` 这类字段。
    3. Provide convenient export helpers for dict / JSON output.
       提供统一的 dict / JSON 导出辅助方法。
    4. Provide round-trip helpers used by this package's document-builder workflow.
       提供 round-trip 辅助方法，便于本包的“生成 → 导出 → 读回”工作流。
    """

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    def to_dict(self, *, exclude_none: bool = True) -> dict[str, Any]:
        """
        Export the model as a plain Python dictionary.
        将模型导出为普通 Python 字典。

        Args:
            exclude_none:
                Whether to omit fields whose value is None.
                是否忽略值为 None 的字段。

        Returns:
            A JSON-serializable dictionary using protocol aliases.
            一个可直接 JSON 序列化、并使用协议别名字段的字典。
        """
        return self.model_dump(by_alias=True, exclude_none=exclude_none)

    def to_json(
        self,
        *,
        indent: int | None = 2,
        exclude_none: bool = True,
    ) -> str:
        """
        Export the model as a JSON string.
        将模型导出为 JSON 字符串。

        Args:
            indent:
                JSON indentation width.
                JSON 缩进宽度。
            exclude_none:
                Whether to omit fields whose value is None.
                是否忽略值为 None 的字段。

        Returns:
            A JSON string using protocol aliases.
            一个使用协议别名字段的 JSON 字符串。
        """
        return self.model_dump_json(by_alias=True, exclude_none=exclude_none, indent=indent)

    def save_json(
        self,
        path: str | Path,
        *,
        indent: int | None = 2,
        exclude_none: bool = True,
        encoding: str = "utf-8",
    ) -> Path:
        """
        Save the current model as a JSON file.
        将当前模型保存为 JSON 文件。

        Why add file I/O at the base-model layer?
        为什么把文件读写能力放在基础模型层？
        Because package users often need a very practical workflow:
        因为本包用户经常需要一个非常实用的工作流：
        - build the document in Python / 在 Python 中构建文档
        - save the JSON to disk / 把 JSON 落盘
        - hand the file to Java or inspect it manually / 交给 Java 或手工检查
        - reload it later for debugging or regression tests / 后续再读回做调试或回归测试

        Args:
            path:
                Output file path.
                输出文件路径。
            indent:
                JSON indentation width.
                JSON 缩进宽度。
            exclude_none:
                Whether to omit fields whose value is None.
                是否忽略值为 None 的字段。
            encoding:
                Text encoding used when writing the file.
                写文件时使用的文本编码。

        Returns:
            The normalized ``Path`` object that was written.
            实际写入的标准化 ``Path`` 对象。
        """
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            self.to_json(indent=indent, exclude_none=exclude_none),
            encoding=encoding,
        )
        return target

    @classmethod
    def load_json(
        cls: type[ModelT],
        path: str | Path,
        *,
        encoding: str = "utf-8",
    ) -> ModelT:
        """
        Read a JSON file from disk and rebuild the model.
        从磁盘读取 JSON 文件并重建模型。

        This is the file-based counterpart of ``from_json``.
        这是 ``from_json`` 的文件版对应方法。
        """
        source = Path(path)
        return cls.from_json(source.read_text(encoding=encoding))

    @classmethod
    def from_dict(cls: type[ModelT], data: dict[str, Any]) -> ModelT:
        """
        Rebuild a model object from a Python dictionary.
        从 Python 字典重建模型对象。

        Why provide this helper when Pydantic already has `model_validate`?
        为什么在已有 `model_validate` 的情况下还要封装这个 helper？
        Because package users often think in terms of:
        因为本包用户更容易按下面的心智理解：
        - `to_dict()` / 导出 dict
        - `from_dict()` / 再从 dict 读回

        This makes the round-trip API more discoverable.
        这样 round-trip API 会更直观、更容易发现。
        """
        return cls.model_validate(data)

    @classmethod
    def from_json(cls: type[ModelT], json_text: str | bytes | bytearray) -> ModelT:
        """
        Rebuild a model object from a JSON string / bytes payload.
        从 JSON 字符串 / 字节串重建模型对象。
        """
        return cls.model_validate_json(json_text)
