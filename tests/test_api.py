"""Tests for the pdfstract HTTP API."""

from __future__ import annotations

import io
from pathlib import Path

import pytest

from pdfstract.api import create_app


@pytest.fixture
def app(tmp_path: Path):
    return create_app(
        upload_folder=tmp_path / "uploads",
        output_dir=tmp_path / "output",
    )


@pytest.fixture
def client(app):
    app.config["TESTING"] = True
    return app.test_client()


def _post_pdf(client, filename: str, content: bytes) -> object:
    return client.post(
        "/api/extract",
        data={"file": (io.BytesIO(content), filename)},
        content_type="multipart/form-data",
    )


def test_extract_without_file_returns_400(client) -> None:
    response = client.post("/api/extract")
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_extract_with_non_pdf_returns_400(client) -> None:
    response = _post_pdf(client, "nota.txt", b"conteudo qualquer")
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_extract_valid_pdf_returns_markdown(client, sample_pdf: Path) -> None:
    response = _post_pdf(client, "relatorio.pdf", sample_pdf.read_bytes())
    assert response.status_code == 200
    assert "text/markdown" in response.content_type
    assert "This is page one with enough text." in response.get_data(as_text=True)


def test_get_result_existing_file_returns_200(app, client, tmp_path: Path) -> None:
    output_dir = Path(app.config["OUTPUT_DIR"])
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "resultado.md").write_text("# resultado", encoding="utf-8")

    response = client.get("/api/result/resultado.md")
    assert response.status_code == 200
    assert "resultado" in response.get_data(as_text=True)


def test_get_result_missing_file_returns_404(client) -> None:
    response = client.get("/api/result/nao-existe.md")
    assert response.status_code == 404
    assert response.get_json() == {"error": "Arquivo não encontrado"}


def test_health_returns_ok(client) -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}
