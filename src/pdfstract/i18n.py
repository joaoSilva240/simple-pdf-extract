"""Internationalization messages for pdfstract."""

from __future__ import annotations


MESSAGES: dict[str, dict[str, str]] = {
    "pt": {
        "start_extraction": "[INFO] Extraindo: {path}",
        "page_processed_native": "[INFO] Página {number}: texto nativo ✓",
        "page_processed_ocr": "[INFO] Página {number}: OCR aplicado ✓ (página escaneada)",
        "page_ocr_error": "[ERRO] Página {number}: falha no OCR — {error}",
        "file_generated": "[OK] Arquivo gerado: {path} ({pages} páginas)",
        "file_not_found": "[ERRO] Arquivo não encontrado em {data_dir}: {filename}",
        "available_files": "Arquivos disponíveis:",
        "empty_data_dir": "[AVISO] A pasta {data_dir} está vazia ou não existe. Adicione PDFs ou execute `pdfstract ajuda`.",
        "ocr_not_available": "[ERRO] OCR indisponível. Verifique se Tesseract OCR e Poppler estão instalados.",
        "password_protected": "[ERRO] PDF protegido por senha: {path}",
        "processing_summary": "[INFO] Resumo: {native} páginas nativas, {ocr} páginas com OCR",
        "no_pdfs_found": "Nenhum PDF encontrado em {data_dir}.",
        "help_header": "pdfstract — extrai texto de PDFs",
        "help_commands": """
Comandos disponíveis:
  pdfstract extrair <arquivo>          Extrai um PDF da pasta data/
  pdfstract extrair tudo               Processa todos os PDFs da pasta data/
  pdfstract extrair --com-ocr <arquivo> Força OCR no arquivo
  pdfstract listar                     Lista PDFs disponíveis em data/
  pdfstract ajuda                      Mostra esta ajuda

Opções globais:
  --idioma pt|en                       Idioma da interface (padrão: pt)
  --idioma-ocr por|eng                 Idioma do OCR (padrão: por)
  --formato md|txt                     Formato de saída (padrão: md)
  --output-dir PATH                    Pasta de saída (padrão: output)
  --data-dir PATH                      Pasta de entrada (padrão: data)

Exemplos:
  pdfstract extrair relatorio.pdf
  pdfstract extrair relatorio.pdf --formato txt
  pdfstract extrair --com-ocr scan.pdf
  pdfstract extrair scan.pdf --idioma-ocr eng
  pdfstract extrair tudo --formato txt
""",
    },
    "en": {
        "start_extraction": "[INFO] Extracting: {path}",
        "page_processed_native": "[INFO] Page {number}: native text ✓",
        "page_processed_ocr": "[INFO] Page {number}: OCR applied ✓ (scanned page)",
        "page_ocr_error": "[ERROR] Page {number}: OCR failed — {error}",
        "file_generated": "[OK] File generated: {path} ({pages} pages)",
        "file_not_found": "[ERROR] File not found in {data_dir}: {filename}",
        "available_files": "Available files:",
        "empty_data_dir": "[WARNING] The {data_dir} folder is empty or does not exist. Add PDFs or run `pdfstract help`.",
        "ocr_not_available": "[ERROR] OCR unavailable. Please verify that Tesseract OCR and Poppler are installed.",
        "password_protected": "[ERROR] Password-protected PDF: {path}",
        "processing_summary": "[INFO] Summary: {native} native pages, {ocr} OCR pages",
        "no_pdfs_found": "No PDFs found in {data_dir}.",
        "help_header": "pdfstract — extract text from PDFs",
        "help_commands": """
Available commands:
  pdfstract extract <file>             Extract a PDF from the data/ folder
  pdfstract extract all                Process all PDFs in the data/ folder
  pdfstract extract --com-ocr <file>   Force OCR on the file
  pdfstract list                       List available PDFs in data/
  pdfstract help                       Show this help

Global options:
  --idioma pt|en                       Interface language (default: pt)
  --idioma-ocr por|eng                 OCR language (default: por)
  --formato md|txt                     Output format (default: md)
  --output-dir PATH                    Output folder (default: output)
  --data-dir PATH                      Input folder (default: data)

Examples:
  pdfstract extract report.pdf
  pdfstract extract report.pdf --formato txt
  pdfstract extract --com-ocr scan.pdf
  pdfstract extract scan.pdf --idioma-ocr eng
  pdfstract extract all --formato txt
""",
    },
}


def get_message(key: str, lang: str = "pt", **kwargs: str | int | Path) -> str:
    """Return a translated message, falling back to Portuguese."""
    template = MESSAGES.get(lang, MESSAGES["pt"]).get(key, key)
    return template.format(**kwargs)
