from copy import deepcopy
from pathlib import Path

import pytest
from pydantic import ValidationError

import ova_portable_text as o

FIXTURE = Path(__file__).resolve().parents[1] / "docs/protocol/v1.6-example.json"


def payload():
    return {
        "schemaVersion": "report.v1.6",
        "theme": {"page": {"orientation": "portrait"}},
        "datasets": {
            "tables": [
                {
                    "id": "data",
                    "tableType": "record",
                    "columns": [{"key": "value", "header": "Value"}],
                    "rows": [{"value": 3}],
                }
            ]
        },
        "sections": [
            {
                "id": "s",
                "level": 1,
                "title": "Section",
                "body": [
                    {
                        "itemType": "content",
                        "blocks": [{"_type": "table", "id": "t", "tableRef": "data"}],
                    }
                ],
            }
        ],
    }


def blocks(d):
    return d["sections"][0]["body"][0]["blocks"]


def caption(target="t", side="before", style="table_caption"):
    return {
        "_type": "block",
        "style": style,
        "caption": {"targetRef": target, "position": side},
        "children": [{"_type": "span", "text": "Caption", "marks": []}],
    }


def report(d):
    return o.validate_document_payload(d)


def test_full_fixture_roundtrip_and_global_resolution(tmp_path):
    d = o.Document.load_json(FIXTURE)
    assert d.validate().is_valid
    assert isinstance(d.theme, o.PageThemeConfig)
    assert d.theme.page.orientation == "portrait"
    exported = d.to_dict()
    assert o.Document.from_json(d.to_json()).to_dict() == exported
    p = d.save_json(tmp_path / "roundtrip.json")
    assert o.Document.load_json(p).to_dict() == exported
    flow = d.sections[1].body[0]
    captions = flow.captions_for("financial-instance")
    assert [c.caption.position for c in captions] == ["before", "after"]
    resolver = d.build_resolver()
    for c in captions:
        target = resolver.resolve_caption(c, flow)
        assert target.id == "financial-instance" and target.sourceLayer == "body"
    assert resolver.resolve_caption(captions[0], d.sections[0].body[0]) is None


def test_authoring_helpers_explicit_two_sided_group():
    d = o.create_document(
        schema_version="report.v1.6", theme=o.PageThemeConfig(page=o.page_settings())
    )
    t = o.record_table_dataset(
        id="data",
        columns=[o.table_column(key="n", header="N")],
        rows=[{"n": 1}],
        layout=o.table_layout(
            o.table_column_spec_weight(2, align="right", header=o.cell_alignment(align="center")),
            cell_defaults=o.cell_alignment(vertical_align="middle"),
            header_defaults=o.cell_alignment(align="center"),
        ),
    )
    d.add_table_dataset(t)
    s = d.new_section(id="s", title="S", level=1, page=o.page_settings())
    child = s.new_subsection(id="sub", title="Sub", page={"orientation": "landscape"})
    child.append_object_with_captions(
        o.table_block(
            id="t",
            table_ref="data",
            page=o.page_settings("landscape"),
            pagination=o.object_pagination(page_break_before="always", page_break_after="always"),
        ),
        before="Title",
        after="Notes",
        before_layout={"textAlign": "center"},
    )
    assert d.validate().is_valid
    assert len(child.body[0].captions_for("t", position="before")) == 1
    assert len(child.body[0].captions_for("t", position="after")) == 1
    assert o.Document.from_dict(d.to_dict()).validate().is_valid
    assert (
        o.section(id="other", level=1, title="Other", page=o.page_settings()).page.orientation
        == "portrait"
    )


@pytest.mark.parametrize(
    "model,kwargs",
    [
        (o.PageSettings, {"orientation": "horizontal"}),
        (o.PageSettings, {}),
        (o.PageSettings, {"orientation": None}),
        (o.PageSettings, {"orientation": "portrait", "size": "A4"}),
        (o.ObjectPagination, {"pageBreakBefore": True}),
        (o.ObjectPagination, {"pageBreakAfter": "never"}),
        (o.ObjectPagination, {"pageBreakAfter": None}),
        (o.CellAlignment, {"align": "justify"}),
        (o.CellAlignment, {"verticalAlign": "center"}),
        (o.CellAlignment, {"align": None}),
        (o.CaptionBinding, {"targetRef": " ", "position": "before"}),
        (o.CaptionBinding, {"targetRef": "t"}),
        (o.CaptionBinding, {"targetRef": "t", "position": "top"}),
        (o.TableColumnSpec, {"align": "right"}),
        (o.TableColumnSpec, {"width": {"mode": "auto"}, "header": {"width": {"mode": "auto"}}}),
        (o.TableLayout, {"cellOverrides": []}),
        (o.SectionPagination, {"pageBreakAfter": "always"}),
    ],
)
def test_rejected_field_contracts(model, kwargs):
    with pytest.raises(ValidationError):
        model.model_validate(kwargs)


@pytest.mark.parametrize("field", ["page", "pagination"])
def test_object_explicit_null_rejected(field):
    d = payload()
    blocks(d)[0][field] = None
    r = report(d)
    assert not r.is_valid
    assert any(field in (i.path or "") for i in r.issues)


@pytest.mark.parametrize(
    "where", ["theme", "section", "caption", "cellDefaults", "headerDefaults", "columnHeader"]
)
def test_other_new_nulls_rejected(where):
    d = payload()
    if where == "theme":
        d["theme"]["page"] = None
    elif where == "section":
        d["sections"][0]["page"] = None
    elif where == "caption":
        blocks(d).append({"_type": "block", "caption": None})
    elif where == "columnHeader":
        d["datasets"]["tables"][0]["layout"] = {
            "columnSpecs": [{"width": {"mode": "auto"}, "header": None}]
        }
    else:
        d["datasets"]["tables"][0]["layout"] = {where: None}
    assert not report(d).is_valid


@pytest.mark.parametrize(
    "version",
    [
        "report.v1",
        "report.v1.0",
        "report.v1.1",
        "report.v1.2",
        "report.v1.3",
        "report.v1.4",
        "report.v1.5",
    ],
)
@pytest.mark.parametrize("feature", ["page", "pagination", "caption", "alignment"])
def test_old_versions_reject_typed_new_fields(version, feature):
    d = payload()
    d["schemaVersion"] = version
    d["theme"] = {}
    if feature == "page":
        blocks(d)[0]["page"] = {"orientation": "landscape"}
    elif feature == "pagination":
        blocks(d)[0]["pagination"] = {}
    elif feature == "caption":
        blocks(d).insert(0, caption())
    else:
        d["datasets"]["tables"][0]["layout"] = {"headerDefaults": {}}
    r = report(d)
    assert not r.is_valid and "protocol.version_mismatch" in r.codes()


def test_historical_theme_extension_is_preserved_not_reinterpreted():
    old = {
        "schemaVersion": "report.v1.5",
        "theme": {"page": {"custom": True, "orientation": "custom"}},
    }
    d = o.Document.from_dict(old)
    assert d.to_dict()["theme"] == old["theme"] | {"blockStyleDefaults": {}}
    assert d.validate().is_valid
    with pytest.raises(ValidationError):
        o.Document.from_dict({**old, "schemaVersion": "report.v1.6"})
    with pytest.raises(ValidationError):
        o.create_document(theme=o.PageThemeConfig(page=o.page_settings()))


@pytest.mark.parametrize(
    "scenario,code",
    [
        ("dataset", "caption.invalid_target"),
        ("anchor", "caption.invalid_target"),
        ("cross_content", "caption.invalid_target"),
        ("missing", "caption.invalid_target"),
        ("wrong_side", "caption.invalid_position"),
        ("gap", "caption.invalid_position"),
        ("wrong_style", "caption.invalid_type"),
        ("list", "caption.invalid_type"),
        ("duplicates", "duplicate_id"),
    ],
)
def test_caption_failures(scenario, code):
    d = payload()
    b = blocks(d)
    c = caption()
    b.insert(0, c)
    if scenario == "dataset":
        c["caption"]["targetRef"] = "data"
    elif scenario == "anchor":
        b[1]["anchor"] = "alias"
        c["caption"]["targetRef"] = "alias"
    elif scenario == "cross_content":
        b.remove(c)
        d["sections"][0]["body"].append({"itemType": "content", "blocks": [c]})
    elif scenario == "missing":
        c["caption"]["targetRef"] = "missing"
    elif scenario == "wrong_side":
        c["caption"]["position"] = "after"
    elif scenario == "gap":
        b.insert(1, {"_type": "block", "children": []})
    elif scenario == "wrong_style":
        c["style"] = "figure_caption"
    elif scenario == "list":
        c["listItem"] = "bullet"
        c["level"] = 1
    elif scenario == "duplicates":
        b.append(deepcopy(b[1]))
    r = report(d)
    assert not r.is_valid and code in r.codes(), r.to_text()


def test_two_sided_multiblock_caption_groups_and_implicit_boundaries():
    d = payload()
    b = blocks(d)
    b[:0] = [caption(), caption()]
    b += [caption(side="after"), caption(side="after")]
    assert report(d).is_valid
    grid = o.GridTableDataset(
        id="grid", columnCount=1, rows=[o.GridTableRow(cells=[o.GridTableCell(text="A")])]
    )
    doc = o.create_document(schema_version="report.v1.6")
    doc.add_table_dataset(grid)
    s = doc.new_section(id="s", level=1, title="S")
    s.append_blocks(
        o.figure_block(id="old", layout_ref="grid"),
        o.paragraph("Legacy", style="figure_caption"),
        o.caption_block("Next", target_ref="new", position="before"),
        o.figure_block(id="new", layout_ref="grid"),
        o.caption_block("Notes", target_ref="new", position="after"),
    )
    flow = s.body[0]
    assert doc.validate().is_valid
    assert len(flow.figure_captions("old")) == 1
    assert len(flow.figure_captions("new")) == 2
    assert len(flow.figure_captions("missing")) == 0


@pytest.mark.parametrize(
    "field,value",
    [("page", {"orientation": "landscape"}), ("pagination", {"pageBreakBefore": "always"})],
)
def test_cell_objects_cannot_control_pages(field, value):
    d = payload()
    d["assets"] = {
        "images": [
            {"id": "img", "imageSource": {"kind": "url", "url": "https://example.com/a.png"}}
        ]
    }
    d["datasets"]["tables"].append(
        {
            "id": "grid",
            "tableType": "grid",
            "columnCount": 1,
            "rows": [
                {"cells": [{"blocks": [{"_type": "image", "imageRef": "img", field: value}]}]}
            ],
        }
    )
    r = report(d)
    assert "layout.invalid_location" in r.codes(), r.to_text()


def test_cell_and_callout_captions_rejected():
    d = payload()
    d["datasets"]["tables"].append(
        {
            "id": "grid",
            "tableType": "grid",
            "columnCount": 1,
            "rows": [{"cells": [{"blocks": [caption()]}]}],
        }
    )
    blocks(d).append({"_type": "callout", "blocks": [caption()]})
    r = report(d)
    assert sum(i.code == "caption.invalid_location" for i in r.issues) == 2


@pytest.mark.parametrize("change", ["page", "pagination", "caption", "align", "null", "version"])
def test_mutation_is_revalidated(change):
    d = o.Document.from_dict(payload())
    b = d.sections[0].body[0].blocks[0]
    if change == "page":
        b.page = {"orientation": "bad"}
    elif change == "pagination":
        b.pagination = {"pageBreakAfter": "bad"}
    elif change == "caption":
        d.sections[0].body[0].blocks.insert(
            0,
            o.caption_block("Bad", target_ref="unknown", position="before", style="table_caption"),
        )
    elif change == "align":
        layout = o.table_layout(header_defaults=o.cell_alignment(align="center"))
        d.datasets.tables[0].layout = layout
        layout.headerDefaults.align = "bad"
    elif change == "null":
        b.page = None
    else:
        b.page = o.page_settings()
        d.schemaVersion = "report.v1.5"
    assert not d.validate().is_valid


def test_stable_defaults_and_legacy_caption_helper_unchanged():
    d = o.create_document()
    assert d.schemaVersion == "report.v1.5"
    s = d.new_section(id="s", level=1, title="S")
    s.append_table_with_caption(id="t", table_ref="data", caption="Legacy")
    assert s.body[0].blocks[1].caption is None
    assert "page" not in s.to_dict()
    assert "caption" not in s.body[0].blocks[1].to_dict()
    with pytest.raises(ValueError, match="report.v1.6"):
        d.new_section(id="new", title="New", level=1, page=o.page_settings())


def test_mutable_caption_dictionary_cannot_bypass_reference_validation():
    d = o.Document.from_dict(payload())
    c = o.paragraph("Caption", style="table_caption")
    c.caption = {"targetRef": "missing", "position": "before"}
    d.sections[0].body[0].blocks.insert(0, c)
    assert "caption.invalid_target" in d.validate().codes()


def test_theme_null_through_helper_is_not_silently_omitted():
    with pytest.raises(ValidationError):
        o.create_document(schema_version="report.v1.6", theme={"page": None})
    r = report({**payload(), "theme": {"page": {"orientation": "bad"}}})
    assert any((issue.path or "").startswith("theme.page") for issue in r.issues)


def test_downgrade_requires_removing_new_fields_before_export():
    d = o.Document.load_json(FIXTURE)
    d.schemaVersion = "report.v1.5"
    with pytest.raises(ValueError, match="report.v1.6"):
        d.to_json()


def test_new_layout_fields_in_extension_friendly_assets_are_diagnosed():
    d = payload()
    d["assets"] = {
        "images": [
            {
                "id": "image",
                "imageSource": {"kind": "url", "url": "https://example.com/a.png"},
                "page": {"orientation": "landscape"},
            }
        ]
    }
    assert "layout.invalid_location" in report(d).codes()


@pytest.mark.parametrize("name", ["image", "chart", "table", "figure"])
def test_block_and_section_helpers_forward_page_fields(name):
    refs = {
        "image": {"image_ref": "asset"},
        "chart": {"chart_ref": "chart-data"},
        "table": {"table_ref": "table-data"},
        "figure": {"layout_ref": "grid-data"},
    }
    settings = {
        "page": o.page_settings("landscape"),
        "pagination": o.object_pagination(page_break_after="always"),
    }
    block = getattr(o, name + "_block")(id="obj", **refs[name], **settings)
    s = o.section(id="s", level=1, title="S")
    getattr(s, "append_" + name)(id="obj", **refs[name], **settings)
    assert s.body[0].blocks[0].to_dict() == block.to_dict()


def test_multiple_explicit_captions_do_not_add_numbered_targets():
    from ova_portable_text.numbering import DocumentNumbering

    d = o.Document.load_json(FIXTURE)
    numbered = DocumentNumbering.from_document(d)
    assert "financial-instance" in numbered.itemsById
    assert all("caption" not in target.category for target in numbered.itemsById.values())
