"""Layout diagnostics for opt-in v1.6, including mutable authoring models."""

from collections import defaultdict

from pydantic import BaseModel, TypeAdapter, ValidationError

from .base import OvaBaseModel
from .page_layout import CaptionBinding, LayoutComponent


def walk_models(value, path=""):
    """Walk declared fields only; historical extension metadata stays opaque."""
    if isinstance(value, OvaBaseModel):
        yield value, path
        for name in type(value).model_fields:
            yield from walk_models(getattr(value, name), f"{path}.{name}" if path else name)
    elif isinstance(value, list):
        for i, child in enumerate(value):
            yield from walk_models(child, f"{path}[{i}]")
    elif isinstance(value, dict):
        for name, child in value.items():
            yield from walk_models(child, f"{path}.{name}")


def version_layout_issues(document):
    if document.schemaVersion == "report.v1.6":
        return
    for node, path in walk_models(document):
        for field in node._v16_fields:
            if getattr(node, field) is not None or field in node.model_fields_set:
                yield (
                    f"{path}.{field}",
                    "This layout field requires schemaVersion=report.v1.6; no implicit upgrade is performed.",
                )
    # Raw historical theme extensions remain opaque; newly constructed typed values do not.
    for name, value in (document.theme.model_extra or {}).items():
        if isinstance(value, LayoutComponent):
            yield f"theme.{name}", "Typed layout settings require schemaVersion=report.v1.6."


def content_flows(document):
    from .content import ContentItem
    from .section import SubsectionItem

    def walk(section, path):
        for i, item in enumerate(section.body):
            p = f"{path}.body[{i}]"
            if isinstance(item, ContentItem):
                yield item, p
            elif isinstance(item, SubsectionItem):
                yield from walk(item.section, p + ".section")

    for i, section in enumerate(document.sections):
        yield from walk(section, f"sections[{i}]")


def validate_v16(document, report):
    from .block_objects import ChartBlock, FigureBlock, ImageBlock, TableBlock
    from .text import TextBlock
    from .theme import PageThemeConfig
    from .v14_validation import add_model_errors

    if document.schemaVersion != "report.v1.6":
        return
    # Models are intentionally mutable: validate only the new contracts again.
    theme = document.theme.model_dump(by_alias=True, exclude_none=True)
    if "page" in document.theme.model_fields_set and getattr(document.theme, "page", None) is None:
        theme["page"] = None
    try:
        PageThemeConfig.model_validate(theme)
    except ValidationError as error:
        add_model_errors(report, error, prefix="theme", layout_mode=True)
    for node, path in walk_models(document):
        if path == "theme":
            continue
        for name in node.model_extra or {}:
            if name in {
                "page",
                "pagination",
                "caption",
                "cellDefaults",
                "headerDefaults",
            } and not path.startswith("meta"):
                report.add_issue(
                    code="layout.invalid_location",
                    path=f"{path}.{name}",
                    message="This layout field is not defined on this object.",
                )
        for name in node._v16_fields:
            value = getattr(node, name)
            if value is None and name not in node.model_fields_set:
                continue
            if value is None:
                report.add_issue(
                    code="layout.invalid_value",
                    path=f"{path}.{name}",
                    message="Omit optional layout fields instead of supplying null.",
                )
                continue
            raw = (
                value.model_dump(by_alias=True, exclude_none=True)
                if isinstance(value, BaseModel)
                else value
            )
            # Preserve explicitly assigned nulls in new component objects.
            if isinstance(value, LayoutComponent):
                for key in value.model_fields_set:
                    if getattr(value, key, None) is None:
                        raw[key] = None
            try:
                TypeAdapter(type(node).model_fields[name].annotation).validate_python(raw)
            except ValidationError as error:
                add_model_errors(report, error, prefix=f"{path}.{name}", layout_mode=True)

    allowed = (ImageBlock, ChartBlock, TableBlock, FigureBlock)
    top_paths = set()
    for content, path in content_flows(document):
        targets = defaultdict(list)
        groups = defaultdict(list)
        for i, block in enumerate(content.blocks):
            top_paths.add(f"{path}.blocks[{i}]")
            if isinstance(block, allowed) and block.id:
                targets[block.id].append(i)
        for i, block in enumerate(content.blocks):
            if not isinstance(block, TextBlock) or block.caption is None:
                continue
            try:
                raw = (
                    block.caption.model_dump()
                    if isinstance(block.caption, BaseModel)
                    else block.caption
                )
                binding = CaptionBinding.model_validate(raw)
            except ValidationError:
                # Field diagnostics were emitted above; do not dereference malformed data.
                continue
            p = f"{path}.blocks[{i}].caption"
            if block.listItem is not None:
                report.add_issue(
                    code="caption.invalid_type",
                    path=p,
                    message="List items cannot carry explicit captions.",
                )
            candidates = targets.get(binding.targetRef, [])
            if len(candidates) != 1:
                report.add_issue(
                    code="caption.invalid_target",
                    path=p + ".targetRef",
                    message="Caption must reference one object id in the same content.blocks, not an anchor or dataset.",
                )
                continue
            target = candidates[0]
            expected = (
                "table_caption"
                if isinstance(content.blocks[target], TableBlock)
                else "figure_caption"
            )
            if block.style != expected:
                report.add_issue(
                    code="caption.invalid_type",
                    path=p,
                    message=f"Expected style={expected} for this target.",
                )
            groups[(target, binding.position)].append(i)
        for (target, side), positions in groups.items():
            expected = (
                list(range(target - len(positions), target))
                if side == "before"
                else list(range(target + 1, target + 1 + len(positions)))
            )
            if side not in ("before", "after") or positions != expected:
                report.add_issue(
                    code="caption.invalid_position",
                    path=f"{path}.blocks[{positions[0]}].caption.position",
                    message="Each caption group must be contiguous and immediately on its declared side of the target.",
                )
    for node, path in walk_models(document):
        if isinstance(node, allowed) and path not in top_paths:
            for name in ("page", "pagination"):
                if getattr(node, name) is not None:
                    report.add_issue(
                        code="layout.invalid_location",
                        path=f"{path}.{name}",
                        message="Page settings are only allowed on top-level body instances, not cell contents.",
                    )
        if isinstance(node, TextBlock) and node.caption is not None and path not in top_paths:
            report.add_issue(
                code="caption.invalid_location",
                path=path + ".caption",
                message="Explicit captions must be in section content.blocks.",
            )
