# pdfstract

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Typer](https://img.shields.io/badge/Typer-CLI-000000?style=for-the-badge)
![pypdf](https://img.shields.io/badge/pypdf-extra%C3%A7%C3%A3o%20nativa-FF6B6B?style=for-the-badge)
![pdf2image](https://img.shields.io/badge/pdf2image-PDF%20para%20imagem-2196F3?style=for-the-badge)
![pytesseract](https://img.shields.io/badge/pytesseract-OCR-4CAF50?style=for-the-badge)
![uv](https://img.shields.io/badge/uv-depend%C3%AAncias-29BFF6?style=for-the-badge)
![pytest](https://img.shields.io/badge/pytest-testes-C21325?style=for-the-badge&logo=pytest&logoColor=white)
![ruff](https://img.shields.io/badge/ruff-lint-D7FF64?style=for-the-badge&logo=ruff&logoColor=black)

CLI simples para extrair texto de PDFs digitais e escaneados, salvando o resultado em Markdown (`.md`) ou texto puro (`.txt`). A ferramenta roda 100% localmente e tenta primeiro a extração nativa com `pypdf`; se uma página tiver pouco texto, aplica OCR automaticamente com `pdf2image` + `pytesseract`.

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

> **Nota:** a sintaxe multi-palavra `extrair com ocr` é modelada como a flag `--com-ocr` para manter a compatibilidade com o Typer. Use `--paginas 1,3,5-8` para extrair apenas páginas específicas.

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
│       │   ├── native.py     # Extração com pypdf
│       │   └── ocr.py        # OCR com pdf2image + pytesseract
│       └── formatters/
│           ├── base.py
│           ├── markdown.py
│           └── plain_text.py
└── tests/
    ├── conftest.py
    ├── test_cli.py
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