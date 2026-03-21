from ova_portable_text import create_document, image_asset, image_block, section


def test_resolver_debug_summary_and_counts() -> None:
    report = create_document(title="Resolver Demo", language="en")
    report.add_image_asset(image_asset(id="img-1", src="https://example.com/a.png"))

    sec = section(id="sec-1", level=1, title="Intro")
    sec.append_block(image_block(id="fig-1", image_ref="img-1"))
    report.append_section(sec)

    resolver = report.build_resolver()

    assert resolver.counts_by_layer()["assets"] == 1
    assert resolver.counts_by_layer()["body"] >= 2
    assert resolver.counts_by_type()["section"] == 1
    assert resolver.counts_by_type()["image"] == 1
    assert resolver.counts_by_type()["image_asset"] == 1

    summary = resolver.debug_summary()
    assert "unique_targets=" in summary
    assert "layer_counts=" in summary

    target = resolver.get("fig-1")
    assert target is not None
    assert target.sectionId == "sec-1"
    assert target.sectionTitle == "Intro"
