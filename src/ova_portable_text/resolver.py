from __future__ import annotations

"""
Document resolver / index builder for OVAPortableText.
OVAPortableText 的文档解析索引器。

The protocol requires that future reference-like abilities can resolve targets
consistently across the whole document.
协议要求未来凡是类似“引用 / 跳转 / 目录”的能力，都能在整份文档范围内稳定解析目标。

Step 8 adds richer target metadata and lightweight summary helpers, so the
resolver is useful not only for validation, but also for debugging and test logs.
第 8 步补充了更丰富的 target 元数据和轻量摘要 helper，
使 resolver 不只适合校验，也更适合调试和测试日志输出。
"""

from collections import Counter, defaultdict

from pydantic import Field

from .base import OvaBaseModel
from .block_objects import CalloutBlock, ChartBlock, ImageBlock, MathBlock, TableBlock
from .content import ContentItem
from .document import Document
from .section import Section, SubsectionItem


class ResolvedTarget(OvaBaseModel):
    """
    One globally resolvable target.
    一个全局可解析目标。

    Extra fields are intentionally included to make downstream validation output
    more actionable.
    这里刻意加入了一些额外字段，使后续校验输出更具可操作性。
    """

    id: str
    targetType: str
    anchor: str | None = None
    location: str
    sourceLayer: str
    sectionId: str | None = None
    sectionTitle: str | None = None

    def to_text(self) -> str:
        """
        Render the target into one compact debug line.
        将 target 渲染成一行紧凑的调试文本。
        """
        parts = [f"{self.targetType}:{self.id}"]
        if self.anchor:
            parts.append(f"anchor={self.anchor}")
        if self.sectionId:
            if self.sectionTitle:
                parts.append(f"section={self.sectionId} ({self.sectionTitle})")
            else:
                parts.append(f"section={self.sectionId}")
        parts.append(f"location={self.location}")
        return " | ".join(parts)


class DocumentResolver(OvaBaseModel):
    """
    Global resolver / index for a document.
    文档的全局解析器 / 索引器。

    Main responsibilities / 主要职责：
    1. collect all resolvable targets / 收集所有可解析目标
    2. detect duplicate IDs / 发现重复 ID
    3. detect duplicate anchors / 发现重复 anchor
    4. resolve `xref` target types through a consistent alias mapping
       通过统一别名映射解析 `xref.targetType`
    5. provide quick summaries for debugging / 提供便于调试的摘要
    """

    targetsById: dict[str, ResolvedTarget] = Field(default_factory=dict)
    targetsByType: dict[str, dict[str, ResolvedTarget]] = Field(default_factory=dict)
    targetsByAnchor: dict[str, ResolvedTarget] = Field(default_factory=dict)
    duplicates: dict[str, list[ResolvedTarget]] = Field(default_factory=dict)
    duplicateAnchors: dict[str, list[ResolvedTarget]] = Field(default_factory=dict)

    @classmethod
    def from_document(cls, document: Document) -> "DocumentResolver":
        """
        Build a resolver index from the whole document.
        从整份文档构建 resolver 索引。
        """
        bucket: dict[str, list[ResolvedTarget]] = defaultdict(list)
        anchor_bucket: dict[str, list[ResolvedTarget]] = defaultdict(list)
        type_bucket: dict[str, dict[str, ResolvedTarget]] = defaultdict(dict)

        def add_target(
            *,
            id: str,
            target_type: str,
            anchor: str | None,
            location: str,
            source_layer: str,
            section_id: str | None = None,
            section_title: str | None = None,
        ) -> None:
            target = ResolvedTarget(
                id=id,
                targetType=target_type,
                anchor=anchor,
                location=location,
                sourceLayer=source_layer,
                sectionId=section_id,
                sectionTitle=section_title,
            )
            bucket[id].append(target)
            if anchor:
                anchor_bucket[anchor].append(target)

        def add_type_alias(*, alias_type: str, target: ResolvedTarget) -> None:
            type_bucket[alias_type][target.id] = ResolvedTarget(
                id=target.id,
                targetType=alias_type,
                anchor=target.anchor,
                location=target.location,
                sourceLayer=target.sourceLayer,
                sectionId=target.sectionId,
                sectionTitle=target.sectionTitle,
            )

        def walk_section(section: Section, path: str) -> None:
            add_target(
                id=section.id,
                target_type="section",
                anchor=section.anchor,
                location=path,
                source_layer="body",
                section_id=section.id,
                section_title=section.title,
            )
            for body_index, item in enumerate(section.body):
                item_path = f"{path}.body[{body_index}]"
                if isinstance(item, ContentItem):
                    for block_index, block in enumerate(item.blocks):
                        block_path = f"{item_path}.blocks[{block_index}]"
                        common = dict(
                            location=block_path,
                            source_layer="body",
                            section_id=section.id,
                            section_title=section.title,
                        )
                        if isinstance(block, ImageBlock):
                            add_target(id=block.id, target_type="image", anchor=block.anchor, **common)
                        elif isinstance(block, ChartBlock):
                            add_target(id=block.id, target_type="chart", anchor=block.anchor, **common)
                        elif isinstance(block, TableBlock):
                            add_target(id=block.id, target_type="table", anchor=block.anchor, **common)
                        elif isinstance(block, MathBlock):
                            add_target(id=block.id, target_type="math_block", anchor=block.anchor, **common)
                        elif isinstance(block, CalloutBlock):
                            add_target(id=block.id, target_type="callout", anchor=block.anchor, **common)
                elif isinstance(item, SubsectionItem):
                    walk_section(item.section, f"{item_path}.section")

        for index, section in enumerate(document.sections):
            walk_section(section, f"sections[{index}]")

        for index, asset in enumerate(document.assets.images):
            add_target(id=asset.id, target_type="image_asset", anchor=asset.anchor, location=f"assets.images[{index}]", source_layer="assets")
        for index, asset in enumerate(document.assets.logos):
            add_target(id=asset.id, target_type="logo_asset", anchor=asset.anchor, location=f"assets.logos[{index}]", source_layer="assets")
        for index, asset in enumerate(document.assets.backgrounds):
            add_target(id=asset.id, target_type="background_asset", anchor=asset.anchor, location=f"assets.backgrounds[{index}]", source_layer="assets")
        for index, asset in enumerate(document.assets.icons):
            add_target(id=asset.id, target_type="icon_asset", anchor=asset.anchor, location=f"assets.icons[{index}]", source_layer="assets")
        for index, asset in enumerate(document.assets.attachments):
            add_target(id=asset.id, target_type="attachment_asset", anchor=asset.anchor, location=f"assets.attachments[{index}]", source_layer="assets")
        for index, chart in enumerate(document.datasets.charts):
            add_target(id=chart.id, target_type="chart_dataset", anchor=chart.anchor, location=f"datasets.charts[{index}]", source_layer="datasets")
        for index, table in enumerate(document.datasets.tables):
            add_target(id=table.id, target_type="table_dataset", anchor=table.anchor, location=f"datasets.tables[{index}]", source_layer="datasets")
        for index, metric in enumerate(document.datasets.metrics):
            add_target(id=metric.id, target_type="metric_dataset", anchor=metric.anchor, location=f"datasets.metrics[{index}]", source_layer="datasets")
        for index, item in enumerate(document.bibliography):
            add_target(id=item.id, target_type="bibliography_item", anchor=item.anchor, location=f"bibliography[{index}]", source_layer="registry")
        for index, item in enumerate(document.footnotes):
            add_target(id=item.id, target_type="footnote", anchor=item.anchor, location=f"footnotes[{index}]", source_layer="registry")
        for index, item in enumerate(document.glossary):
            add_target(id=item.id, target_type="glossary_term", anchor=item.anchor, location=f"glossary[{index}]", source_layer="registry")

        targets_by_id: dict[str, ResolvedTarget] = {}
        duplicates: dict[str, list[ResolvedTarget]] = {}
        for id_value, items in bucket.items():
            if len(items) == 1:
                targets_by_id[id_value] = items[0]
            else:
                duplicates[id_value] = items

        targets_by_anchor: dict[str, ResolvedTarget] = {}
        duplicate_anchors: dict[str, list[ResolvedTarget]] = {}
        for anchor_value, items in anchor_bucket.items():
            if len(items) == 1:
                targets_by_anchor[anchor_value] = items[0]
            else:
                duplicate_anchors[anchor_value] = items

        for target in targets_by_id.values():
            canonical = cls._canonical_target_type(target.targetType)
            type_bucket[canonical][target.id] = ResolvedTarget(
                id=target.id,
                targetType=canonical,
                anchor=target.anchor,
                location=target.location,
                sourceLayer=target.sourceLayer,
                sectionId=target.sectionId,
                sectionTitle=target.sectionTitle,
            )

            if canonical in {"image", "chart", "image_asset"}:
                add_type_alias(alias_type="figure", target=target)
            if canonical in {"image_asset", "logo_asset", "background_asset", "icon_asset", "attachment_asset"}:
                add_type_alias(alias_type="asset", target=target)
            if canonical == "math_block":
                add_type_alias(alias_type="equation", target=target)

        return cls(
            targetsById=targets_by_id,
            targetsByType={k: v for k, v in type_bucket.items()},
            targetsByAnchor=targets_by_anchor,
            duplicates=duplicates,
            duplicateAnchors=duplicate_anchors,
        )

    def get(self, id_value: str) -> ResolvedTarget | None:
        """
        Resolve by global unique ID only.
        仅按全局唯一 ID 解析目标。
        """
        return self.targetsById.get(id_value)

    def get_by_anchor(self, anchor_value: str) -> ResolvedTarget | None:
        """
        Resolve by globally unique anchor.
        按全局唯一 anchor 解析目标。

        If the anchor is duplicated, this returns `None` and callers should inspect
        `duplicateAnchors` instead.
        如果 anchor 存在重复，这里会返回 `None`，调用方应查看 `duplicateAnchors`。
        """
        return self.targetsByAnchor.get(anchor_value)

    def resolve_xref(self, *, target_type: str, target_id: str) -> ResolvedTarget | None:
        """
        Resolve an xref target by type alias and id.
        按 target type 别名 + id 解析 xref 目标。
        """
        canonical = self._canonical_target_type(target_type)
        return self.targetsByType.get(canonical, {}).get(target_id)

    def counts_by_type(self) -> dict[str, int]:
        """
        Count unique resolved targets grouped by canonical type.
        按 canonical type 统计唯一已解析目标数量。
        """
        return dict(sorted((key, len(value)) for key, value in self.targetsByType.items()))

    def counts_by_layer(self) -> dict[str, int]:
        """
        Count targets grouped by source layer, such as body / assets / datasets.
        按 source layer 统计目标数量，例如 body / assets / datasets。
        """
        counter = Counter(target.sourceLayer for target in self.targetsById.values())
        return dict(sorted(counter.items()))

    def debug_summary(self) -> str:
        """
        Build a compact multi-line resolver summary.
        生成适合调试输出的 resolver 多行摘要。
        """
        lines = [
            "OVAPortableText resolver summary:",
            f"unique_targets={len(self.targetsById)}",
            f"duplicate_ids={len(self.duplicates)}",
            f"duplicate_anchors={len(self.duplicateAnchors)}",
            f"type_counts={self.counts_by_type()}",
            f"layer_counts={self.counts_by_layer()}",
        ]
        return "\n".join(lines)

    @classmethod
    def is_supported_target_type(cls, target_type: str) -> bool:
        """
        Check whether a target type is known to this resolver.
        检查某个 target type 是否为当前 resolver 已知类型。
        """
        normalized = target_type.strip().lower().replace("-", "_")
        return normalized in cls._target_aliases()

    @classmethod
    def supported_target_types(cls) -> set[str]:
        """
        Return all accepted external target type names.
        返回当前接受的全部外部 target type 名称。
        """
        return set(cls._target_aliases().keys())

    @classmethod
    def _canonical_target_type(cls, target_type: str) -> str:
        normalized = target_type.strip().lower().replace("-", "_")
        return cls._target_aliases().get(normalized, normalized)

    @staticmethod
    def _target_aliases() -> dict[str, str]:
        """
        Central alias mapping used by the resolver.
        resolver 使用的统一 target type 别名表。
        """
        return {
            "section": "section",
            "figure": "figure",
            "image": "image",
            "chart": "chart",
            "table": "table",
            "equation": "equation",
            "math": "math_block",
            "math_block": "math_block",
            "callout": "callout",
            "bibliography": "bibliography_item",
            "bibliography_item": "bibliography_item",
            "reference": "bibliography_item",
            "citation": "bibliography_item",
            "footnote": "footnote",
            "glossary": "glossary_term",
            "glossary_term": "glossary_term",
            "term": "glossary_term",
            "asset": "asset",
            "image_asset": "image_asset",
            "logo_asset": "logo_asset",
            "background_asset": "background_asset",
            "icon_asset": "icon_asset",
            "attachment": "attachment_asset",
            "attachment_asset": "attachment_asset",
            "chart_dataset": "chart_dataset",
            "table_dataset": "table_dataset",
            "metric": "metric_dataset",
            "metric_dataset": "metric_dataset",
        }
