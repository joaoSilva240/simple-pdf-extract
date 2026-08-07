"""Command-line interface for pdfstract."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from typing_extensions import Annotated

from pdfstract.domain.config import (
    DEFAULT_DATA_DIR,
    DEFAULT_FORMAT,
    DEFAULT_OCR_LANGUAGE,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_UI_LANGUAGE,
)
from pdfstract.domain.models import ExtractedDocument
from pdfstract.domain.pipeline import ExtractionPipeline
from pdfstract.formatters.markdown import MarkdownFormatter
from pdfstract.formatters.plain_text import PlainTextFormatter
from pdfstract.i18n import get_message

app = typer.Typer(
    name="pdfstract",
    help="Extrai texto de PDFs digitais e escaneados.",
    no_args_is_help=True,
    add_completion=False,
)


def _list_pdf_files(data_dir: Path) -> list[Path]:
    """Return all .pdf files in *data_dir*, sorted."""
    if not data_dir.exists():
        return []
    return sorted(path for path in data_dir.iterdir() if path.suffix.lower() == ".pdf")


def _formatter_for(format_name: str):
    """Return a formatter instance for the requested output format."""
    if format_name == "txt":
        return PlainTextFormatter()
    return MarkdownFormatter()


def _output_path_for(
    source: Path,
    output_dir: Path,
    extension: str,
) -> Path:
    """Build the output file path for a source PDF."""
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir / f"{source.stem}.{extension}"


def _extract_pdf(
    pdf_path: Path,
    output_dir: Path,
    format_name: str,
    ocr_lang: str,
    ui_lang: str,
    force_ocr: bool,
) -> Path | None:
    """Run extraction pipeline and write the output file."""
    pipeline = ExtractionPipeline(
        ocr_lang=ocr_lang,
        ui_lang=ui_lang,
        progress_callback=typer.echo,
    )

    document = pipeline.extract(pdf_path, force_ocr=force_ocr)
    if document is None:
        return None

    formatter = _formatter_for(format_name)
    output_path = _output_path_for(pdf_path, output_dir, formatter.extension())
    formatter.write(document, output_path)

    native_count = sum(1 for p in document.pages if p.method.value == "native")
    ocr_count = len(document.pages) - native_count
    typer.echo(
        get_message(
            "processing_summary",
            ui_lang,
            native=native_count,
            ocr=ocr_count,
        )
    )
    typer.echo(
        get_message(
            "file_generated",
            ui_lang,
            path=output_path,
            pages=len(document.pages),
        )
    )
    return output_path


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    idioma: Annotated[
        str,
        typer.Option(
            "--idioma",
            help="Idioma da interface (pt ou en).",
            show_default=True,
        ),
    ] = DEFAULT_UI_LANGUAGE,
    idioma_ocr: Annotated[
        str,
        typer.Option(
            "--idioma-ocr",
            help="Idioma do OCR (por ou eng).",
            show_default=True,
        ),
    ] = DEFAULT_OCR_LANGUAGE,
    formato: Annotated[
        str,
        typer.Option(
            "--formato",
            help="Formato de saída (md ou txt).",
            show_default=True,
        ),
    ] = DEFAULT_FORMAT,
    output_dir: Annotated[
        Path,
        typer.Option(
            "--output-dir",
            help="Pasta de saída.",
            show_default=True,
        ),
    ] = DEFAULT_OUTPUT_DIR,
    data_dir: Annotated[
        Path,
        typer.Option(
            "--data-dir",
            help="Pasta de entrada.",
            show_default=True,
        ),
    ] = DEFAULT_DATA_DIR,
) -> None:
    """Configurações globais do pdfstract."""
    ctx.ensure_object(dict)
    ctx.obj["idioma"] = idioma
    ctx.obj["idioma_ocr"] = idioma_ocr
    ctx.obj["formato"] = formato
    ctx.obj["output_dir"] = output_dir
    ctx.obj["data_dir"] = data_dir

    if ctx.invoked_subcommand is None:
        typer.echo(get_message("help_header", idioma))
        typer.echo(get_message("help_commands", idioma))


@app.command("extrair")
@app.command("extract")
def extract_command(
    ctx: typer.Context,
    arquivo: Annotated[
        str,
        typer.Argument(help="Nome do PDF em data/ ou 'tudo' para processar todos."),
    ],
    com_ocr: Annotated[
        bool,
        typer.Option("--com-ocr", help="Força OCR ignorando extração nativa."),
    ] = False,
) -> None:
    """Extrai texto de um ou mais PDFs."""
    config = ctx.obj
    ui_lang = config["idioma"]
    ocr_lang = config["idioma_ocr"]
    format_name = config["formato"]
    output_dir = config["output_dir"]
    data_dir = config["data_dir"]

    if arquivo.lower() in ("tudo", "all"):
        pdf_files = _list_pdf_files(data_dir)
        if not pdf_files:
            typer.echo(get_message("empty_data_dir", ui_lang, data_dir=data_dir))
            raise typer.Exit(code=1)

        for pdf_path in pdf_files:
            _extract_pdf(
                pdf_path,
                output_dir,
                format_name,
                ocr_lang,
                ui_lang,
                force_ocr=com_ocr,
            )
        return

    pdf_path = data_dir / arquivo
    if not pdf_path.exists():
        typer.echo(get_message("file_not_found", ui_lang, data_dir=data_dir, filename=arquivo))
        available = _list_pdf_files(data_dir)
        if available:
            typer.echo(get_message("available_files", ui_lang))
            for path in available:
                typer.echo(f"  - {path.name}")
        raise typer.Exit(code=1)

    _extract_pdf(
        pdf_path,
        output_dir,
        format_name,
        ocr_lang,
        ui_lang,
        force_ocr=com_ocr,
    )


@app.command("listar")
@app.command("list")
def list_command(ctx: typer.Context) -> None:
    """Lista os PDFs disponíveis em data/."""
    config = ctx.obj
    ui_lang = config["idioma"]
    data_dir = config["data_dir"]

    pdf_files = _list_pdf_files(data_dir)
    if not pdf_files:
        typer.echo(get_message("empty_data_dir", ui_lang, data_dir=data_dir))
        return

    typer.echo(get_message("available_files", ui_lang))
    for path in pdf_files:
        typer.echo(f"  - {path.name}")


@app.command("ajuda")
@app.command("help")
def help_command(ctx: typer.Context) -> None:
    """Mostra a ajuda com comandos disponíveis."""
    ui_lang = ctx.obj["idioma"]
    typer.echo(get_message("help_header", ui_lang))
    typer.echo(get_message("help_commands", ui_lang))


if __name__ == "__main__":
    app()
