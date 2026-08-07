# pdfstract

CLI simples para extrair texto de PDFs digitais e escaneados, salvando o resultado em Markdown (`.md`) ou texto puro (`.txt`). A ferramenta roda 100% localmente e tenta primeiro a extração nativa com `pypdf`; se uma página tiver pouco texto, aplica OCR automaticamente com `pdf2image` + `pytesseract`.

## Pré-requisitos

- [uv](https://docs.astral.sh/uv/) instalado.
- Python 3.10 ou superior (o projeto usa `>=3.10`).
- Tesseract OCR instalado no sistema (somente para OCR):
  - **Windows**: [tesseract-ocr-w64-setup](https://github.com/UB-Mannheim/tesseract/wiki) com pacotes `por` e `eng`.
  - **Linux**: `sudo apt install tesseract-ocr tesseract-ocr-por tesseract-ocr-eng`.
  - **macOS**: `brew install tesseract tesseract-lang`.
- Poppler (usado pelo `pdf2image`):
  - **Windows**: instale o [poppler-windows](https://github.com/oschwartz10612/poppler-windows/releases) e adicione `bin/` ao `PATH`.
  - **Linux**: `sudo apt install poppler-utils`.
  - **macOS**: `brew install poppler`.

## Instalação

```bash
uv sync
```

## Uso

### Comandos principais

| Português | Inglês | Descrição |
|---|---|---|
| `pdfstract extrair <arquivo>` | `pdfstract extract <file>` | Extrai um PDF da pasta `data/` |
| `pdfstract extrair tudo` | `pdfstract extract all` | Processa todos os PDFs da pasta `data/` |
| `pdfstract extrair --com-ocr <arquivo>` | `pdfstract extract --com-ocr <file>` | Força OCR no arquivo |
| `pdfstract listar` | `pdfstract list` | Lista PDFs disponíveis em `data/` |
| `pdfstract ajuda` | `pdfstract help` | Mostra a ajuda |

> **Nota:** a sintaxe multi-palavra `extrair com ocr` é modelada como a flag `--com-ocr` para manter a compatibilidade com o Typer.

### Exemplos

```bash
# Extrair um PDF digital
uv run pdfstract extrair relatorio.pdf

# Extrair e salvar como texto puro
uv run pdfstract extrair relatorio.pdf --formato txt

# Forçar OCR em um arquivo escaneado
uv run pdfstract extrair --com-ocr scan.pdf

# Processar todos os PDFs da pasta data/
uv run pdfstract extrair tudo --formato txt

# Listar PDFs disponíveis
uv run pdfstract listar

# Ajuda em inglês
uv run pdfstract help --idioma en
```

### Opções globais

| Opção | Padrão | Descrição |
|---|---|---|
| `--idioma pt\|en` | `pt` | Idioma das mensagens da interface |
| `--idioma-ocr por\|eng` | `por` | Idioma do Tesseract OCR |
| `--formato md\|txt` | `md` | Formato do arquivo de saída |
| `--output-dir PATH` | `output` | Pasta onde os arquivos extraídos são salvos |
| `--data-dir PATH` | `data` | Pasta de entrada dos PDFs |

## Estrutura do projeto

```
simple-pdf-stract/
├── pyproject.toml
├── uv.lock
├── README.md
├── ANALISE_REQUISITOS.md
├── data/                     # PDFs de entrada
├── output/                   # Arquivos extraídos
├── src/
│   └── pdfstract/
│       ├── __init__.py
│       ├── cli.py            # Interface de linha de comando (Typer)
│       ├── i18n.py           # Mensagens em pt/en
│       ├── domain/
│       │   ├── models.py     # Page, ExtractedDocument, ExtractionMethod
│       │   ├── config.py     # Constantes
│       │   └── pipeline.py   # Orquestração nativo → OCR
│       ├── extractors/
│       │   ├── base.py
│       │   ├── native.py     # Extração com pypdf
│       │   └── ocr.py        # OCR com pdf2image + pytesseract
│       └── formatters/
│           ├── base.py
│           ├── markdown.py
│           └── plain_text.py
└── tests/
    ├── conftest.py
    ├── test_extractors.py
    ├── test_formatters.py
    └── test_pipeline.py
```

## Testes e qualidade

```bash
# Sincronizar dependências
uv sync

# Lint
uv run ruff check .

# Testes
uv run pytest

# Verificar a CLI
uv run pdfstract ajuda
```

## Limitações

- A extração é linear/textual: tabelas complexas, colunas múltiplas e formatação rica não são preservadas.
- A detecção de página escaneada usa uma heurística simples (menos de 10 caracteres por página).
- OCR depende de Tesseract e Poppler instalados corretamente no sistema.
- Apenas os idiomas `por` e `eng` são suportados no OCR do MVP.
- PDFs protegidos por senha são reportados como erro e ignorados.

## Licença

MIT
