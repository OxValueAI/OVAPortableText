from ova_portable_text import ValidationReport


def test_validation_report_exposes_python_friendly_is_valid_alias():
    report = ValidationReport()
    assert report.isValid is True
    assert report.is_valid is True

    report.add_issue(code="demo", message="broken", severity="error")
    assert report.isValid is False
    assert report.is_valid is False
