from __future__ import annotations

"""
Display-number helper layer for OVAPortableText.
OVAPortableText 的显示编号辅助层。

Important boundary / 重要边界：
The protocol separates:
协议明确分离了以下三层：
- stable system ID / 稳定系统 ID
- anchor / 锚点
- display number / 面向读者的显示编号

This module only computes helper-side display numbers.
本模块只负责计算 helper 层的显示编号。
It does NOT write display numbers back into the protocol JSON.
它不会把显示编号直接写回协议 JSON。
"""

from typing import TYPE_CHECKING, Literal

from pydantic import Field

from .base import OvaBaseModel
from .block_objects import ChartBlock, ImageBlock, MathBlock, TableBlock
from .content import ContentItem
from .section import Section, SubsectionItem

if TYPE_CHECKING:
    from .document import Document

ObjectNumberingMode = Literal["global", "section"]


class NumberingConfig(OvaBaseModel):
    """
    Configuration for helper-side display numbering.
    helper 层显示编号的配置对象。

    Current default / 当前默认值：
    - sections: always hierarchical by tree structure
      section 始终按章节树层级推导
    - figure / table / equation: global continuous numbering
      figure / table / equation 默认全局连续编号

    Why not freeze one universal rule in the protocol?
    为什么不把这些规则直接冻结进协议本体？
    Because the protocol intentionally leaves those renderer-facing choices open.
    因为协议本身刻意没有把这些更偏渲染侧的策略写死。
    """

    figureMode: ObjectNumberingMode = "global"
    tableMode: ObjectNumberingMode = "global"
    equationMode: ObjectNumberingMode = "global"


class NumberedTarget(OvaBaseModel):
    """
    One computed display-number entry.
    一条计算得到的显示编号记录。
    """

    id: str
    category: Literal["section", "figure", "table", "equation"]
    displayNumber: str | None = None
    anchor: str | None = None
    path: str


class DocumentNumbering(OvaBaseModel):
    """
    Computed numbering snapshot for one whole document.
    整份文档的一次编号快照。

    This object is intentionally read-only in spirit.
    这个对象在设计意图上是“只读快照”。
    You compute it from a document, then query it.
    它由 document 计算出来，然后供调用方查询。
    """

    config: NumberingConfig = Field(default_factory=NumberingConfig)
    itemsById: dict[str, NumberedTarget] = Field(default_factory=dict)

    @classmethod
    def from_document(
        cls,
        document: Document,
        config: NumberingConfig | None = None,
    ) -> "DocumentNumbering":
        """
        Compute a numbering snapshot from the given document.
        从给定 document 计算一份编号快照。
        """
        config = config or NumberingConfig()
        items: dict[str, NumberedTarget] = {}
        global_counts = {"figure": 0, "table": 0, "equation": 0}

        def allocate_object_number(
            *,
            category: Literal["figure", "table", "equation"],
            section_path_numbers: list[int],
            local_counts: dict[str, int],
        ) -> str:
            mode: ObjectNumberingMode
            if category == "figure":
                mode = config.figureMode
            elif category == "table":
                mode = config.tableMode
            else:
                mode = config.equationMode

            if mode == "section":
                local_counts[category] += 1
                prefix = ".".join(str(x) for x in section_path_numbers)
                return f"{prefix}-{local_counts[category]}"

            global_counts[category] += 1
            return str(global_counts[category])

        def walk_section(section: Section, *, path: str, structural_numbers: list[int]) -> None:
            section_display_number = ".".join(str(x) for x in structural_numbers) if section.numbering == "auto" else None
            items[section.id] = NumberedTarget(
                id=section.id,
                category="section",
                displayNumber=section_display_number,
                anchor=section.anchor,
                path=path,
            )

            local_counts = {"figure": 0, "table": 0, "equation": 0}

            for body_index, item in enumerate(section.body):
                item_path = f"{path}.body[{body_index}]"
                if isinstance(item, ContentItem):
                    for block_index, block in enumerate(item.blocks):
                        block_path = f"{item_path}.blocks[{block_index}]"
                        if isinstance(block, (ImageBlock, ChartBlock)):
                            items[block.id] = NumberedTarget(
                                id=block.id,
                                category="figure",
                                displayNumber=allocate_object_number(
                                    category="figure",
                                    section_path_numbers=structural_numbers,
                                    local_counts=local_counts,
                                ),
                                anchor=block.anchor,
                                path=block_path,
                            )
                        elif isinstance(block, TableBlock):
                            items[block.id] = NumberedTarget(
                                id=block.id,
                                category="table",
                                displayNumber=allocate_object_number(
                                    category="table",
                                    section_path_numbers=structural_numbers,
                                    local_counts=local_counts,
                                ),
                                anchor=block.anchor,
                                path=block_path,
                            )
                        elif isinstance(block, MathBlock):
                            items[block.id] = NumberedTarget(
                                id=block.id,
                                category="equation",
                                displayNumber=allocate_object_number(
                                    category="equation",
                                    section_path_numbers=structural_numbers,
                                    local_counts=local_counts,
                                ),
                                anchor=block.anchor,
                                path=block_path,
                            )
                elif isinstance(item, SubsectionItem):
                    sibling_index = _next_child_index(section=item.section, parent=section)
                    # The actual structural path is already known from array order below.
                    # 真正的结构路径会由下面的顺序遍历统一给出。
                    walk_section(
                        item.section,
                        path=f"{item_path}.section",
                        structural_numbers=structural_numbers + [sibling_index],
                    )

        def walk_section_list(sections: list[Section], *, parent_numbers: list[int], parent_path: str) -> None:
            for index, section in enumerate(sections, start=1):
                walk_section(
                    section,
                    path=f"{parent_path}[{index - 1}]",
                    structural_numbers=parent_numbers + [index],
                )

        def _next_child_index(section: Section, parent: Section) -> int:
            """
            Compute the direct-child index of `section` under `parent`.
            计算 `section` 在 `parent` 下的“直接子章节序号”。

            Why do this by scanning the parent body?
            为什么通过扫描 parent.body 来做？
            Because `body` can interleave content items and subsection items.
            因为 `body` 里可以交错出现 content item 与 subsection item。
            We only count direct subsection items.
            我们这里只统计直接 `subsection` 项。
            """
            count = 0
            for item in parent.body:
                if isinstance(item, SubsectionItem):
                    count += 1
                    if item.section is section:
                        return count
            return count or 1

        walk_section_list(document.sections, parent_numbers=[], parent_path="sections")
        return cls(config=config, itemsById=items)

    def get(self, id_value: str) -> NumberedTarget | None:
        """
        Return the numbering record of one target by ID.
        通过 ID 返回某个目标的编号记录。
        """
        return self.itemsById.get(id_value)

    def get_display_number(self, id_value: str) -> str | None:
        """
        Return only the display number string of one target.
        仅返回某个目标的显示编号字符串。
        """
        item = self.get(id_value)
        return item.displayNumber if item else None
