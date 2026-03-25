from ova_portable_text import (
    attachment_asset,
    background_asset,
    create_document,
    icon_asset,
    logo_asset,
    metric_dataset,
    metric_value,
)

report = create_document(title="Extended Registries Demo", language="en", reportType="valuation")

report.add_logo_asset(logo_asset(id="logo-main", url="https://example.com/assets/logo.svg", alt="Main brand logo", variant="light"))
report.add_background_asset(background_asset(id="bg-cover", url="https://example.com/assets/cover.png", usage="cover"))
report.add_icon_asset(icon_asset(id="icon-growth", url="https://example.com/assets/growth.svg", alt="Growth icon", family="outline"))
report.add_attachment_asset(attachment_asset(id="att-appendix-a", url="https://example.com/appendix-a.pdf", file_name="appendix-a.pdf", description="Supporting appendix PDF"))
report.add_metric_dataset(metric_dataset(id="metric-overview", values=[metric_value(key="revenue", label="Revenue", value=128.4, unit="USDm"), metric_value(key="employees", label="Employees", value=96), metric_value(key="profitable", label="Profitable", value=True)], label="Company snapshot"))

print(report.to_json())
