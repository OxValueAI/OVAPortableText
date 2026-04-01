import pytest

from ova_portable_text import (
    grid_table_dataset,
    grid_table_row,
    record_table_dataset,
    table_column,
    table_column_spec_auto,
    table_column_spec_weight,
    table_layout,
)


def test_record_table_layout_column_specs_length_matches_columns():
    table = record_table_dataset(
        id="table-1",
        columns=[table_column(key="a", header="A"), table_column(key="b", header="B")],
        rows=[{"a": "1", "b": "2"}],
        layout=table_layout(table_column_spec_auto(), table_column_spec_weight(2)),
    )
    assert len(table.layout.columnSpecs) == 2


def test_record_table_layout_rejects_wrong_length():
    with pytest.raises(ValueError, match="columnSpecs"):
        record_table_dataset(
            id="table-1",
            columns=[table_column(key="a", header="A"), table_column(key="b", header="B")],
            rows=[],
            layout=table_layout(table_column_spec_auto()),
        )


def test_grid_table_weight_requires_positive_value():
    with pytest.raises(ValueError, match="> 0"):
        table_column_spec_weight(0)


def test_grid_table_layout_rejects_wrong_column_count():
    with pytest.raises(ValueError, match="columnSpecs"):
        grid_table_dataset(
            id="grid-1",
            column_count=2,
            rows=[grid_table_row()],
            layout=table_layout(table_column_spec_auto()),
        )
