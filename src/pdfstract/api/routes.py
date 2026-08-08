"""API routes for pdfstract."""

from __future__ import annotations

import uuid
from pathlib import Path

from flask import Blueprint, Response, current_app, jsonify, request, send_file, send_from_directory
from werkzeug.exceptions import NotFound
from werkzeug.utils import secure_filename

from pdfstract.domain.pages import parse_pages
from pdfstract.domain.service import extract_text

api_bp = Blueprint("api", __name__)

ALLOWED_FORMATS = ("md", "txt")


def _as_bool(value: str) -> bool:
    return value.strip().lower() in ("true", "1", "yes", "on")


@api_bp.post("/api/extract")
def extract() -> tuple[dict, int] | Response:
    """Extract text from an uploaded PDF and return the result file."""
    upload = request.files.get("file")
    if upload is None or upload.filename == "":
        return jsonify({"error": "Nenhum arquivo enviado"}), 400

    if not upload.filename.lower().endswith(".pdf"):
        return jsonify({"error": "O arquivo deve ser um PDF (extensão .pdf)"}), 400

    format_name = request.form.get("formato", "md")
    if format_name not in ALLOWED_FORMATS:
        return jsonify({"error": "formato inválido (use md ou txt)"}), 400

    ocr_lang = request.form.get("idioma_ocr", "por")
    force_ocr = _as_bool(request.form.get("com_ocr", "false"))

    pages: set[int] | None = None
    pages_spec = request.form.get("paginas", "")
    if pages_spec:
        try:
            pages = parse_pages(pages_spec)
        except ValueError:
            return jsonify({"error": f"paginas inválido: {pages_spec}"}), 400

    upload_id = uuid.uuid4().hex
    upload_path = Path(current_app.config["UPLOAD_FOLDER"]) / f"{upload_id}.pdf"
    upload.save(str(upload_path))

    try:
        text = extract_text(
            upload_path,
            format_name=format_name,
            ocr_lang=ocr_lang,
            force_ocr=force_ocr,
            pages=pages,
        )
    except Exception:
        text = None
    finally:
        upload_path.unlink(missing_ok=True)

    if text is None:
        return jsonify({"error": "Falha na extração do PDF"}), 500

    extension = "txt" if format_name == "txt" else "md"
    output_path = Path(current_app.config["OUTPUT_DIR"]) / f"{upload_id}.{extension}"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")

    original_stem = Path(secure_filename(upload.filename)).stem or "arquivo"
    mimetype = "text/plain" if extension == "txt" else "text/markdown"
    return send_file(
        output_path,
        mimetype=mimetype,
        as_attachment=True,
        download_name=f"{original_stem}.{extension}",
    )


@api_bp.get("/api/result/<arquivo>")
def result(arquivo: str) -> tuple[dict, int] | Response:
    """Download a previously generated extraction result."""
    output_dir = current_app.config["OUTPUT_DIR"]
    try:
        return send_from_directory(output_dir, arquivo)
    except (NotFound, OSError):
        return jsonify({"error": "Arquivo não encontrado"}), 404


@api_bp.get("/api/health")
def health() -> Response:
    """Health check endpoint."""
    return jsonify({"status": "ok"}), 200
