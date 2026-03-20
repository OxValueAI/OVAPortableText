from __future__ import annotations

"""
Theme-related models for OVAPortableText.
OVAPortableText 的主题相关模型。

The protocol explicitly says `theme` is currently only a placeholder and should
not be over-specified yet.
协议明确指出当前版本的 `theme` 仍是占位层，不应过度细化。

So this module provides:
因此本模块提供：
1. a small typed core for the most obvious fields
   一小组最明显的强类型字段
2. extension-friendly behaviour for future renderer-specific additions
   面向未来渲染器扩展的宽松扩展能力
"""

from pydantic import ConfigDict

from .base import OvaBaseModel


class ThemeConfig(OvaBaseModel):
    """
    Lightweight typed model for the top-level `theme` object.
    顶层 `theme` 对象的轻量强类型模型。

    The protocol currently treats `theme` as a placeholder.
    协议当前把 `theme` 视作占位层。

    Therefore this model is intentionally permissive:
    因此这个模型刻意保持较宽松：
    - it gives common fields typed names
      为常见字段提供强类型名字
    - it still allows extra keys
      但仍允许额外字段存在
    """

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    name: str | None = None
    styleTemplate: str | None = None
    pageTemplateFamily: str | None = None
    brandAssetRefs: list[str] | None = None
    coverTemplateRef: str | None = None
