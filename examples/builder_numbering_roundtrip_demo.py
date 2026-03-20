"""
Step 6 demo: builder API + numbering + round-trip.
第 6 步示例：builder API + 编号辅助 + round-trip。
"""

from ova_portable_text import NumberingConfig, create_document


report = create_document(
    title="Step 6 Demo",
    language="en",
    reportType="valuation",
    clientName="Demo Client",
    theme={
        "name": "corporate-blue",
        "styleTemplate": "clean-report",
    },
)

intro = report.new_section(id="sec-1", level=1, title="Executive Summary")
intro.append_paragraph("This section demonstrates the improved builder API.")
intro.append_image_with_caption(
    id="fig-overview",
    image_ref="img-overview",
    caption="Figure: Overview diagram",
)

background = intro.new_subsection(id="sec-1-1", title="Background")
background.append_paragraph("Child sections can now be created directly from a parent section.")
background.append_math_with_caption(
    id="eq-core",
    latex=r"V = \sum_{t=1}^{n} \frac{CF_t}{(1+r)^t}",
    caption="Equation: Core DCF formula",
)

numbering = report.build_numbering(NumberingConfig(figureMode="section", equationMode="section"))
print("Section sec-1 =>", numbering.get_display_number("sec-1"))
print("Section sec-1-1 =>", numbering.get_display_number("sec-1-1"))
print("Figure fig-overview =>", numbering.get_display_number("fig-overview"))
print("Equation eq-core =>", numbering.get_display_number("eq-core"))

payload = report.to_json()
print(payload)

rebuilt = report.from_json(payload)
print("Round-trip title =>", rebuilt.meta.title)
