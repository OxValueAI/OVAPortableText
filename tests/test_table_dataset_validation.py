import pytest

from ova_portable_text import table_column, table_dataset


def test_table_dataset_rejects_duplicate_column_keys():
    with pytest.raises(ValueError):
        table_dataset(
            id="table-1",
            columns=[
                table_column(key="year", header="Year"),
                table_column(key="year", header="Year Duplicate"),
            ],
            rows=[],
        )


def test_table_dataset_rejects_unknown_row_keys():
    with pytest.raises(ValueError):
        table_dataset(
            id="table-1",
            columns=[table_column(key="year", header="Year")],
            rows=[{"unknown": "value"}],
        )
