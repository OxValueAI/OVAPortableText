from ova_portable_text import (
    attachment_asset,
    background_asset_url,
    create_document,
    icon_asset_url,
    logo_asset_url,
    metric_dataset,
    metric_value,
)


def test_extended_registries_are_serialized_and_resolvable():
    report = create_document(title="Registry Demo", language="en")
    report.add_logo_asset(logo_asset_url(id="logo-main", url="https://example.com/logo.svg", alt="Main Logo"))
    report.add_background_asset(background_asset_url(id="bg-cover", url="https://example.com/cover.png"))
    report.add_icon_asset(icon_asset_url(id="icon-star", url="https://example.com/star.svg", alt="Star"))
    report.add_attachment_asset(
        attachment_asset(id="att-appendix", src="https://example.com/appendix.pdf", file_name="appendix.pdf")
    )
    report.add_metric_dataset(
        metric_dataset(
            id="metric-overview",
            values=[
                metric_value(key="revenue", label="Revenue", value=120.5, unit="USDm"),
                metric_value(key="employees", label="Employees", value=80),
            ],
        )
    )

    data = report.to_dict()
    resolver = report.build_resolver()

    assert data["assets"]["logos"][0]["id"] == "logo-main"
    assert data["assets"]["attachments"][0]["fileName"] == "appendix.pdf"
    assert data["datasets"]["metrics"][0]["values"][0]["key"] == "revenue"
    assert resolver.resolve_xref(target_type="logo_asset", target_id="logo-main") is not None
    assert resolver.resolve_xref(target_type="attachment", target_id="att-appendix") is not None
    assert resolver.resolve_xref(target_type="metric", target_id="metric-overview") is not None
    assert resolver.resolve_xref(target_type="asset", target_id="logo-main") is not None
    assert resolver.get_by_anchor("logo-main") is not None
