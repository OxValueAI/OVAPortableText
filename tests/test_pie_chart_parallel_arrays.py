from ova_portable_text import pie_chart_from_parallel_arrays


def test_parallel_array_helper_converts_and_sorts_descending_by_value():
    chart = pie_chart_from_parallel_arrays(
        id="chart-1",
        area_en=["Finance", "Technology", "Healthcare"],
        area_zh=["金融", "技术", "医疗"],
        value=[31.2, 42.5, 26.3],
        description_en=["B", "A", "C"],
        description_zh=["乙", "甲", "丙"],
    )

    data = chart.to_dict()
    assert data["chartType"] == "pie"
    assert [item["key"] for item in data["slices"]] == ["technology", "finance", "healthcare"]
    assert [item["value"] for item in data["slices"]] == [42.5, 31.2, 26.3]
