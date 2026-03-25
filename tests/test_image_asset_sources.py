import base64

import pytest

from ova_portable_text import (
    ImageAsset,
    ImageSourceEmbedded,
    ImageSourceUrl,
    image_asset,
    image_asset_embedded,
    image_asset_from_file,
    image_asset_url,
)


def test_image_asset_url_helper_populates_image_source():
    asset = image_asset_url(
        id="img-cover",
        url="https://example.com/cover.png",
        alt="Cover",
        mimeType="image/png",
    )

    assert isinstance(asset.imageSource, ImageSourceUrl)
    assert asset.imageSource.kind == "url"
    assert asset.imageSource.url == "https://example.com/cover.png"


def test_image_asset_embedded_helper_populates_image_source_without_src():
    data = base64.b64encode(b"png-bytes").decode("ascii")
    asset = image_asset_embedded(
        id="img-qr",
        data_base64=data,
        mime_type="image/png",
        alt="QR",
    )

    dumped = asset.to_dict()
    assert "src" not in dumped
    assert asset.mimeType == "image/png"
    assert isinstance(asset.imageSource, ImageSourceEmbedded)
    assert asset.imageSource.kind == "embedded"
    assert asset.imageSource.encoding == "base64"
    assert asset.imageSource.data == data


def test_image_asset_can_be_created_from_image_source_only():
    asset = image_asset(
        id="img-local",
        image_source={"kind": "url", "url": "assets/images/local.png"},
        alt="Local image",
    )

    assert isinstance(asset.imageSource, ImageSourceUrl)
    assert asset.imageSource.url == "assets/images/local.png"


def test_legacy_src_is_rejected_in_pure_protocol_mode():
    with pytest.raises(Exception):
        ImageAsset(
            id="img-legacy",
            src="https://example.com/legacy.png",
            alt="Legacy",
            imageSource=ImageSourceUrl(kind="url", url="https://example.com/legacy.png"),
        )


def test_image_asset_from_file_embed_true(tmp_path):
    path = tmp_path / "qr.png"
    path.write_bytes(b"fake-png-content")

    asset = image_asset_from_file(
        id="img-file",
        path=path,
        alt="From file",
        embed=True,
    )

    expected = base64.b64encode(b"fake-png-content").decode("ascii")
    assert asset.mimeType == "image/png"
    assert isinstance(asset.imageSource, ImageSourceEmbedded)
    assert asset.imageSource.data == expected


def test_image_asset_from_file_embed_false_uses_url_source(tmp_path):
    path = tmp_path / "diagram.png"
    path.write_bytes(b"fake-diagram")

    asset = image_asset_from_file(
        id="img-file-url",
        path=path,
        alt="Diagram",
        embed=False,
    )

    assert isinstance(asset.imageSource, ImageSourceUrl)
    assert asset.imageSource.url.endswith("diagram.png")


def test_embedded_image_requires_mime_type():
    with pytest.raises(ValueError, match="mimeType"):
        ImageAsset(
            id="img-bad",
            imageSource=ImageSourceEmbedded(kind="embedded", encoding="base64", data="abc"),
        )
