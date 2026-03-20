from ova_portable_text import create_document, section, xref


def test_chart_body_instance_can_be_resolved_as_figure_xref():
    report = create_document(title="Resolver Demo", language="en")

    intro = section(id="sec-1", level=1, title="Intro")
    intro.append_paragraph("See ", xref(target_type="figure", target_id="fig-share"), ".")
    intro.append_chart(id="fig-share", chart_ref="chart-data-1")
    report.append_section(intro)

    validation = report.validate()
    codes = {issue.code for issue in validation.issues}

    assert validation.isValid is False
    assert "unresolved_xref" not in codes
    assert "unresolved_chart_ref" in codes
