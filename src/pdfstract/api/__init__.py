"""HTTP API for pdfstract."""

from __future__ import annotations

from pathlib import Path

from flask import Flask, jsonify

from pdfstract.api.routes import api_bp
from pdfstract.domain.config import DEFAULT_OUTPUT_DIR

MAX_CONTENT_LENGTH = 100 * 1024 * 1024
DEFAULT_UPLOAD_FOLDER = Path("uploads")


def create_app(
    upload_folder: Path | str = DEFAULT_UPLOAD_FOLDER,
    output_dir: Path | str = DEFAULT_OUTPUT_DIR,
) -> Flask:
    """Create and configure the Flask application."""
    upload_folder_path = Path(upload_folder).resolve()
    output_dir_path = Path(output_dir).resolve()
    upload_folder_path.mkdir(parents=True, exist_ok=True)

    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH
    app.config["UPLOAD_FOLDER"] = str(upload_folder_path)
    app.config["OUTPUT_DIR"] = str(output_dir_path)
    app.register_blueprint(api_bp)

    @app.errorhandler(413)
    def request_too_large(error) -> tuple[dict, int]:
        return jsonify({"error": "Arquivo muito grande (máximo de 100 MB)"}), 413

    return app


def main() -> None:
    """Run the pdfstract API server on 127.0.0.1:5000."""
    create_app().run(host="127.0.0.1", port=5000)
