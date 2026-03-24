"""Image-source demo / 图片来源模型示例。"""

from __future__ import annotations

from ova_portable_text import create_document, image_asset_embedded, image_asset_url, image_block, logo_asset, background_asset, icon_asset

# 1x1 transparent PNG / 1x1 透明 PNG
TINY_PNG_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVQIHWP4////fwAJ+wP9KobjigAAAABJRU5ErkJggg=="
)


def main() -> None:
    report = create_document(
        title="Image Sources Demo",
        language="en",
        documentType="valuationReport",
        strict_ids=True,
    )

    report.add_image_asset(
        image_asset_url(
            id="img-overview",
            url="https://example.com/assets/overview.png",
            alt="Overview image",
            mimeType="image/png",
            width=1200,
            height=800,
        )
    )

    report.add_image_asset(
        image_asset_embedded(
            id="img-embedded",
            data_base64=TINY_PNG_BASE64,
            mime_type="image/png",
            alt="Embedded 1x1 PNG",
            width=1,
            height=1,
        )
    )

    report.add_logo_asset(
        logo_asset(
            id="logo-main",
            data_base64=TINY_PNG_BASE64,
            alt="Main logo",
            mimeType="image/png",
            width=32,
            height=32,
        )
    )

    report.add_background_asset(
        background_asset(
            id="bg-cover",
            url="https://example.com/assets/cover-bg.png",
            mimeType="image/png",
            width=1600,
            height=900,
        )
    )

    report.add_icon_asset(
        icon_asset(
            id="icon-growth",
            data_base64=TINY_PNG_BASE64,
            alt="Growth icon",
            mimeType="image/png",
            width=16,
            height=16,
        )
    )

    sec = report.new_section(id="sec-images", level=1, title="Body")
    sec.append_paragraph("This section demonstrates URL and embedded imageSource payloads.")
    sec.append_image_with_caption(
        id="fig-overview",
        image_ref="img-overview",
        caption="Figure: URL-backed image asset.",
    )
    sec.append_image_with_caption(
        id="fig-embedded",
        image_ref="img-embedded",
        caption="Figure: Embedded image asset.",
    )

    report.assert_valid()
    print(report.to_json(indent=2))


if __name__ == "__main__":
    main()
