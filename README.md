# pdfstract

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Typer](https://img.shields.io/badge/Typer-CLI-000000?style=for-the-badge)
![Flask](https://img.shields.io/badge/Flask-API-000000?style=for-the-badge&logo=flask&logoColor=white)
![pypdf](https://img.shields.io/badge/pypdf-extra%C3%A7%C3%A3o%20nativa-FF6B6B?style=for-the-badge)
![pypdfium2](https://img.shields.io/badge/pypdfium2-PDF%20para%20imagem-2196F3?style=for-the-badge)
![rapidocr](https://img.shields.io/badge/rapidocr-OCR-4CAF50?style=for-the-badge)
![uv](https://img.shields.io/badge/uv-depend%C3%AAncias-29BFF6?style=for-the-badge)
![pytest](https://img.shields.io/badge/pytest-testes-C21325?style=for-the-badge&logo=pytest&logoColor=white)
![ruff](https://img.shields.io/badge/ruff-lint-D7FF64?style=for-the-badge&logo=ruff&logoColor=black)

Ferramenta para extrair texto de PDFs digitais e escaneados, salvando o resultado em Markdown (`.md`) ou texto puro (`.txt`). Roda 100% localmente e tenta primeiro a extração nativa com `pypdf`; se uma página tiver pouco texto, aplica OCR automaticamente com `pypdfium2` + `rapidocr` — **100% Python, sem binários externos** (sem Tesseract/Poppler). Oferece **CLI** (Typer) e **API HTTP** (Flask).

## Instalação

```bash
uv sync
```

## Uso — CLI

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
| `--idioma-ocr por\|eng` | `por` | Idioma do OCR (mantido por compatibilidade; o RapidOCR é multilíngue) |
| `--formato md\|txt` | `md` | Formato do arquivo de saída |
| `--output-dir PATH` | `output` | Pasta onde os arquivos extraídos são salvos |
| `--data-dir PATH` | `data` | Pasta de entrada dos PDFs |

## API HTTP (Flask)

### Como rodar

```bash
uv run pdfstract-api
```

O servidor sobe em `http://127.0.0.1:5000`.

### Rotas

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/api/extract` | Envia um PDF e recebe o resultado extraído como arquivo `.md` (ou `.txt`) |
| `GET` | `/api/result/<arquivo>` | Baixa um arquivo extraído anteriormente da pasta `output/` |
| `GET` | `/api/health` | Verifica se o servidor está no ar |

### POST /api/extract

Recebe o PDF via `multipart/form-data` no campo `file`. Campos opcionais:

| Campo | Padrão | Descrição |
|---|---|---|
| `formato` | `md` | Formato de saída: `md` ou `txt` |
| `idioma_ocr` | `por` | Idioma do OCR: `por` ou `eng` |
| `com_ocr` | `false` | `true` força OCR ignorando extração nativa |
| `paginas` | — | Páginas a extrair, ex.: `1,3,5-8` |

**Resposta de sucesso**: `200` com o arquivo extraído como download (`Content-Disposition: attachment`).

**Erros**: `400` (arquivo ausente, extensão inválida, formato/páginas inválidos), `413` (arquivo acima de 100 MB), `500` (falha na extração).

**Exemplos de uso:**

```bash
# Extrair um PDF e baixar o .md
curl -F "file=@data/Zombiecide.pdf" http://127.0.0.1:5000/api/extract

# Extrair como texto puro
curl -F "file=@data/Zombiecide.pdf" -F "formato=txt" http://127.0.0.1:5000/api/extract

# Forçar OCR
curl -F "file=@data/Zombiecide.pdf" -F "com_ocr=true" http://127.0.0.1:5000/api/extract

# Extrair apenas páginas específicas
curl -F "file=@data/Zombiecide.pdf" -F "paginas=1,3,5-8" http://127.0.0.1:5000/api/extract
```

### GET /api/result/<arquivo>

Baixa um arquivo já gerado na pasta `output/`:

```bash
curl -O http://127.0.0.1:5000/api/result/Zombiecide.md
```

### GET /api/health

```bash
curl http://127.0.0.1:5000/api/health
# {"status": "ok"}
```

## Estrutura do projeto

```
simple-pdf-stract/
├── pyproject.toml
├── uv.lock
├── README.md
├── ANALISE_REQUISITOS.md
├── data/                     # PDFs de entrada
├── output/                   # Arquivos extraídos
├── uploads/                  # Uploads temporários da API
├── src/
│   └── pdfstract/
│       ├── __init__.py
│       ├── cli.py            # Interface de linha de comando (Typer)
│       ├── i18n.py           # Mensagens em pt/en
│       ├── api/
│       │   ├── __init__.py   # create_app() e entrypoint da API
│       │   └── routes.py     # Rotas /api/extract, /api/result, /api/health
│       ├── domain/
│       │   ├── models.py     # Page, ExtractedDocument, ExtractionMethod
│       │   ├── config.py     # Constantes
│       │   ├── pages.py      # parse_pages, pages_suffix
│       │   ├── service.py    # extract_text() reutilizável (CLI + API)
│       │   └── pipeline.py   # Orquestração nativo → OCR
│       ├── extractors/
│       │   ├── native.py     # Extração com pypdf
│       │   └── ocr.py        # OCR com pypdfium2 + rapidocr
│       └── formatters/
│           ├── base.py
│           ├── markdown.py
│           └── plain_text.py
└── tests/
    ├── conftest.py
    ├── test_api.py
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

# Subir a API
uv run pdfstract-api
```

## Limitações

- A extração é linear/textual: tabelas complexas, colunas múltiplas e formatação rica não são preservadas.
- A detecção de página escaneada usa uma heurística simples (menos de 10 caracteres por página).
- O OCR usa modelos ONNX embutidos (RapidOCR), sem binários externos — funciona em qualquer sistema com `uv sync`.
- PDFs protegidos por senha são reportados como erro e ignorados.
- A API é síncrona: a requisição `POST /api/extract` só responde após a extração terminar.

## Licença

MIT