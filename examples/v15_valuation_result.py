"""Run from the project root. Creates a native report.v1.5 valuation banner."""

from pathlib import Path

import ova_portable_text as o


def build_report():
    report = o.create_document(title="Valuation result", language="en")
    result = o.valuation_result_chart_dataset(
        id="valuation-result",
        subject={"en": "Clean Food Group Limited"},
        title={"en": "Valuation range"},
        valuation=o.valuation_range(20_100_000, 28_400_000),
        currency="GBP",
        value_basis="equity_value",
        capital_basis="pre_money",
        as_of="2026-08-05",
        data_basis="illustrative",
        display_scale="million",
        display_precision=1,
        notes={"en": "Illustrative design sample; not an independently verified valuation."},
    )
    report.add_chart_dataset(result)
    sec = report.new_section(id="summary", level=1, title="Valuation conclusion")
    sec.append_to_last_content(o.ChartBlock(id="valuation-banner", chartRef=result.id))
    # A banner need not have a caption. Add one only when the report requires it.
    validation = report.validate()
    assert validation.is_valid and not validation.issues, validation
    assert o.Document.from_json(report.to_json()).to_dict() == report.to_dict()
    return report


if __name__ == "__main__":
    build_report().save_json(Path("v15_valuation_result.json"))
