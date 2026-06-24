from __future__ import annotations

from urllib.parse import urlparse

from app.services import storage


def test_presigned_get_url_uses_public_endpoint(monkeypatch) -> None:
    public_client = storage._session.client(
        "s3",
        endpoint_url="http://127.0.0.1:19000",
        config=storage.Config(signature_version="s3v4"),
    )
    monkeypatch.setattr(storage, "_presign_s3", public_client)

    url = storage.presigned_get_url("library/usul-harb-al-rif.pdf")

    parsed = urlparse(url)
    assert f"{parsed.scheme}://{parsed.netloc}" == "http://127.0.0.1:19000"
    assert parsed.path == "/documents/library/usul-harb-al-rif.pdf"
