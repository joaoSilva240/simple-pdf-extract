# Análise de Requisitos — pdf-stract

Este documento consolida a análise de requisitos do produto **pdf-stract**, uma ferramenta CLI simples para extrair texto de PDFs e exportá-lo em Markdown (.md) ou Texto (.txt). O objetivo é definir escopo, funcionalidades, arquitetura, interface de comandos, decisões de design e critérios de aceite do MVP, servindo de referência para a implementação. A ferramenta entrega uma forma simples de transformar PDFs digitais e escaneados em texto editável, atendendo a usuários finais não técnicos que não querem lidar com a complexidade de PDF e OCR.

## 1. Visão Geral do Produto
O **pdf-stract** é uma ferramenta de linha de comando que extrai texto de PDFs e o salva em arquivos Markdown (.md) ou Texto (.txt). É voltado ao usuário final não técnico que deseja transformar PDFs em texto editável, incluindo PDFs escaneados (páginas-imagem) por meio de OCR automático. O valor entregue está na automatização do processo: o usuário informa comandos curtos em português (ou inglês) e obtém o texto consolidado em uma pasta de saída, sem precisar conhecer detalhes técnicos de extração ou reconhecimento óptico.

## 2. Escopo

### 2.1 Dentro do Escopo (MVP)

1. Extração de texto de PDFs digitais (camada de texto nativa) usando pypdf.
2. OCR de PDFs escaneados (páginas-imagem) usando pdf2image (conversão página → imagem) + pytesseract (reconhecimento), com suporte a português (por) e inglês (eng).
3. Estratégia automática em cascata: tentar pypdf primeiro; se o texto extraído for insuficiente (heurística: página com menos de ~10 caracteres de texto), aplicar OCR nessa página automaticamente.
4. Exportação dos resultados em Markdown (.md) ou Texto (.txt), por escolha do usuário (padrão: markdown).
5. Modo "processar todos os arquivos da pasta data/" de uma vez.
6. Modo "forçar OCR" em um arquivo específico, ignorando a extração nativa.
7. Interface de linha de comando com comandos em linguagem natural em PORTUGUÊS (ver seção 5), com suporte a inglês.
8. Mensagens de progresso/erro no idioma selecionado (pt ou en), selecionável por flag ou comando.
9. Ambiente gerenciado por uv (pyproject.toml, uv.lock, ambiente virtual isolado).

### 2.2 Fora do Escopo (fases futuras)

- Interface gráfica (GUI) e interface web.
- Processamento em lote paralelo/assíncrono de alta performance.
- Preservação de layout complexo (tabelas, colunas múltiplas, formatação rica) — extração é linear/textual.
- Idiomas adicionais além de português e inglês.
- Assinatura digital, anotação, edição ou geração de PDFs.
- Extração de imagens embutidas ou metadados (exceto dados simples de texto).

### 2.3 Requisitos Funcionais (RF)

| ID | Descrição |
|----|-----------|
| RF-01 | Extrair texto nativo de um PDF digital informado. |
| RF-02 | Extrair texto via OCR de um PDF escaneado (por ou eng). |
| RF-03 | Detectar automaticamente quando uma página precisa de OCR (fallback automático). |
| RF-04 | Exportar resultado em formato .md ou .txt. |
| RF-05 | Processar todos os PDFs da pasta data/. |
| RF-06 | Listar os arquivos PDF disponíveis na pasta data/. |
| RF-07 | Exibir ajuda com a lista de comandos disponíveis. |
| RF-08 | Selecionar idioma da interface (pt/en). |
| RF-09 | Selecionar idioma do OCR (por/eng; padrão: por). |
| RF-10 | Informar caminho do arquivo de saída gerado ao final do processamento. |

### 2.4 Requisitos Não Funcionais (RNF)

| ID | Categoria | Descrição |
|----|-----------|-----------|
| RNF-01 | Portabilidade | Funcionar em Windows (alvo principal do dev) e com caminhos preparados para Linux/macOS. |
| RNF-02 | Isolamento | Toda dependência gerenciada via uv; nenhuma dependência global exigida além de uv + Tesseract OCR instalado no sistema. |
| RNF-03 | Usabilidade | Comandos curtos e intuitivos em português; feedback claro de progresso e erros. |
| RNF-04 | Performance | Processamento de um PDF típico (até ~50 páginas) em tempo aceitável; sem requisitos de tempo real. |
| RNF-05 | Manutenibilidade | Código modular (CLI, extração, OCR, exportação, i18n), testes com pytest. |
| RNF-06 | Confiabilidade | Erros de arquivo (corrompido, protegido por senha, não-PDF) tratados com mensagem clara sem travar o processo. |
| RNF-07 | Segurança | Sem envio de dados para a rede; processamento 100% local. |

### 2.5 Dependências Externas de Sistema

- Tesseract OCR instalado no sistema (obrigatório para OCR). No Windows: instalável via instalador UB-Mannheim (tesseract-ocr-w64-setup) com pacotes de idioma `por` e `eng`; no Linux: `sudo apt install tesseract-ocr tesseract-ocr-por tesseract-ocr-eng`; macOS: `brew install tesseract tesseract-lang`.
- Poppler (via pdf2image): no Windows o pdf2image usa o binário `poppler` (poppler-utils); documentar que é necessário ou registrar a alternativa usando `pypdfium2` (pura Python, sem binário externo) — decisão registrada em 6.2.

## 3. Stack de Tecnologias

| Tecnologia | Papel | Justificativa |
|------------|-------|---------------|
| Python 3.14 | Linguagem | Ecossistema maduro para PDF/OCR. |
| uv | Gerenciador de ambiente/dependências | Isolamento do projeto, velocidade, pyproject.toml + uv.lock. |
| pypdf | Extração de texto nativo de PDFs digitais | Simples, pura Python, sem dependência binária. |
| pdf2image | Conversão de páginas PDF em imagens (para OCR) | Integra diretamente com Pillow/pytesseract. |
| Pillow | Manipulação das imagens das páginas | Pré-processamento leve (escala, cinza) para melhorar o OCR. |
| pytesseract | Wrapper Python do Tesseract OCR | OCR com suporte a `por` e `eng`. |
| Tesseract OCR | Engine de OCR (binário do sistema) | Engine padrão de OCR de código aberto. |
| Typer | Framework de CLI | Comandos tipados e documentação automática de ajuda; mantém comandos nomeados em português. |
| pytest | Testes | Garantia de regressão nos módulos de extração/exportação. |
| Ruff | Lint/format | Qualidade de código. |

## 4. Arquitetura e Fluxo de Processamento

### 4.1 Estrutura de pastas prevista

```
simple-pdf-stract/
├── pyproject.toml
├── uv.lock
├── README.md
├── ANALISE_REQUISITOS.md
├── src/
│   └── pdfstract/
│       ├── __init__.py
│       ├── cli.py            # comandos Typer em pt/en
│       ├── extractor.py      # extração nativa com pypdf
│       ├── ocr.py            # OCR com pdf2image + pytesseract
│       ├── pipeline.py       # lógica em cascata (nativo → OCR)
│       ├── exporter.py       # geração .md/.txt
│       ├── i18n.py           # mensagens pt/en
│       └── config.py         # constantes (pastas, idiomas, heurística)
├── data/                     # PDFs de entrada (criada pelo usuário)
├── output/                   # arquivos extraídos
└── tests/
    └── test_extractor.py
```

### 4.2 Fluxo em cascata

```
[1] usuário executa comando
        |
[2] localizar PDF(s) na pasta data
        |
[3] para cada página: tentar extração nativa (pypdf)  → suficiente? → [5]
        |_ insuficiente (heurística <10 caracteres na página)
        |
[4]   converter página para imagem (pdf2image)
      → pré-processar (escala 2x, tons de cinza)
      → OCR (pytesseract, idioma selecionado)
        |
[5] consolidar texto por página
        |
[6] exportar para .md/.txt em output/
        |
[7] reportar caminho do arquivo e resumo (páginas processadas, método usado por página)
```

## 5. Interface de Comandos

### 5.1 Filosofia
Comandos em linguagem natural em português, no imperativo, curtos e sem ambiguidade. O padrão é: verbo de ação + alvo + opções opcionais. Todos os comandos têm equivalente em inglês. Um único comando de entrada `pdfstract` (nome do binário) recebe o subcomando.

### 5.2 Tabela de comandos em português

| Comando (pt) | Comando equivalente (en) | Ação | Exemplo |
|--------------|--------------------------|------|---------|
| `extrair ARQUIVO` | `extract FILE` | Extrai texto de um PDF específico da pasta data/ (usa a cascata automática) | `pdfstract extrair relatorio.pdf` |
| `extrair tudo` | `extract all` | Processa todos os PDFs da pasta data/ | `pdfstract extrair tudo` |
| `extrair com ocr ARQUIVO` | `extract with ocr FILE` | Força OCR mesmo em PDF digital | `pdfstract extrair com ocr scan.pdf` |
| `listar` | `list` | Lista os PDFs disponíveis em data/ | `pdfstract listar` |
| `ajuda` | `help` | Mostra todos os comandos e exemplos | `pdfstract ajuda` |
| `salvar como txt` | `save as txt` | Define formato de saída .txt (padrão é .md) | `pdfstract extrair x.pdf --formato txt` (ver nota) |
| `idioma en` | `language en` | Alterna mensagens da interface para inglês | `pdfstract idioma en` |

Nota de design: `salvar como ...` é implementado como uma flag global `--formato md|txt` aplicável aos comandos de extração (ex.: `pdfstract extrair x.pdf --formato txt`), e também é aceito como subcomando `salvar como txt` que define o padrão para a sessão/arquivo de config.

### 5.3 Exemplos de uso

```
# Extrair um arquivo específico (saída em output/relatorio.md)
pdfstract extrair relatorio.pdf

# Extrair todos os PDFs da pasta data
pdfstract extrair tudo

# Forçar OCR em um arquivo escaneado
pdfstract extrair com ocr contrato-escaneado.pdf

# Extrair e salvar como .txt
pdfstract extrair relatorio.pdf --formato txt

# Escolher o idioma do OCR (padrão: por)
pdfstract extrair com ocr doc.pdf --idioma-ocr eng

# Listar PDFs disponíveis
pdfstract listar

# Ajuda em inglês
pdfstract help

# Trocar o idioma da interface
pdfstract idioma en
```

### 5.4 Exemplo de saída esperada no terminal

```
[INFO] Extraindo: data/relatorio.pdf
[INFO] Página 1: texto nativo ✓
[INFO] Página 2: OCR aplicado ✓ (página escaneada)
[INFO] Página 3: texto nativo ✓
[OK] Arquivo gerado: output/relatorio.md (3 páginas)
```

### 5.5 Regras de interpretação

- Se ARQUIVO não for encontrado em data/, exibir a lista dos arquivos disponíveis e uma mensagem de erro amigável.
- Se a pasta data/ não existir ou estiver vazia, avisar e sugerir `pdfstract ajuda`.
- O prefixo `extrair com ocr` tem precedência sobre a cascata automática.
- Formato de saída padrão: .md (markdown); .txt gera texto puro sem marcação.
- Em markdown, incluir cabeçalho por página (ex.: `## Página 1`) para organização.

## 6. Decisões de Design e Alternativas

### 6.1 CLI: Typer com subcomandos em português vs. parser de linguagem natural completo
- **Decisão:** Typer com subcomandos nomeados em português (curto, previsível, documentável, autocompletável).
- **Alternativa descartada:** parser de frase livre completo (ex.: "pega o arquivo tal e salva em txt") — alta complexidade de NLP para baixo benefício no MVP; pode ser evoluído depois.

### 6.2 pdf2image+Poppler vs. pypdfium2 (renderização para OCR)
- **Decisão:** pdf2image como padrão (ecossistema conhecido, alinhado ao pedido do usuário).
- **Alternativa:** pypdfium2 (renderização pura em Python, sem binário Poppler externo) — registrada como opção de fallback para Windows sem Poppler, facilmente trocável no módulo ocr.py.

### 6.3 Heurística de detecção de página escaneada
- **Decisão:** limiar simples — página com menos de 10 caracteres extraídos via pypdf é considerada escaneada → OCR.
- **Alternativa futura:** detectar a presença de imagens na página via pypdf para decidir o OCR antes da extração (mais precisa, porém mais código).

### 6.4 Idioma do OCR
- **Decisão:** padrão `por`; flag `--idioma-ocr eng|por`; tentativa automática `por` → se a saída estiver vazia, tenta `eng` (configurável).

## 7. Plano de Implementação (Fases)

| Fase | Entrega | Escopo |
|------|---------|--------|
| Fase 0 | Fundação | Criar projeto uv (`uv init`), pyproject.toml, estrutura src/, config.py, i18n.py base. |
| Fase 1 | Extração nativa | extractor.py com pypdf + comando `extrair` funcionando para PDF digital. |
| Fase 2 | OCR | ocr.py (pdf2image + pytesseract), pré-processamento, comando `extrair com ocr`, fallback automático. |
| Fase 3 | Exportação | exporter.py (.md/.txt), comando `salvar como`, flag `--formato`. |
| Fase 4 | Operações em lote | `extrair tudo`, `listar`, `ajuda`, `idioma`. |
| Fase 5 | Qualidade | pytest, Ruff, README, testes manuais com PDFs de exemplo. |

## 8. Riscos e Mitigações

| Risco | Impacto | Mitigação |
|-------|---------|-----------|
| Tesseract/Poppler não instalados no Windows | OCR indisponível | Detectar no primeiro uso de OCR e exibir instrução de instalação clara; documentar no README. |
| PDFs protegidos por senha | Falha de extração | Tratar com mensagem clara (pypdf lança exceção específica) e continuar processando outros arquivos. |
| Qualidade do OCR baixa em scans ruins | Texto com erros | Pré-processamento (escala/cinza) + sugerir DPI maior; documentar as limitações. |
| Arquivos não-PDF na pasta data | Erros | Filtrar por extensão .pdf na listagem e no processamento. |

## 9. Critérios de Aceite (MVP)

- [ ] `pdfstract extrair arquivo_digital.pdf` gera output/arquivo_digital.md com o texto completo.
- [ ] `pdfstract extrair com ocr arquivo_escaneado.pdf` extrai texto de um scan em português com erros toleráveis.
- [ ] Fallback automático: um PDF com páginas mistas (digital + scan) é extraído corretamente.
- [ ] `--formato txt` gera arquivo .txt sem marcação markdown.
- [ ] `extrair tudo` processa a pasta data/ inteira e reporta um resumo por arquivo.
- [ ] Comandos funcionam em português e em inglês.
- [ ] `uv run pdfstract ajuda` exibe ajuda sem erros em ambiente recém-clonado.
- [ ] Não há nenhuma dependência instalada fora do ambiente uv (exceto Tesseract/Poppler do sistema, documentados).

## 10. Glossário

- **OCR (Optical Character Recognition):** reconhecimento óptico de caracteres; converte imagem de texto em texto digital.
- **PDF digital (ou "com camada de texto"):** PDF cujo texto pode ser selecionado/copiado diretamente.
- **PDF escaneado:** PDF formado por imagens das páginas, sem camada de texto; exige OCR.
- **Cascata:** estratégia de tentar primeiro o método mais barato (nativo) e só então o mais caro (OCR).
- **pypdf:** biblioteca Python para ler/extrair texto de PDFs.
- **pdf2image:** biblioteca que converte páginas de PDF em imagens (depende de Poppler).
- **pytesseract:** wrapper Python para o binário Tesseract OCR.
- **uv:** gerenciador de projetos e dependências Python (pip/venv/poetry em um só).
- **Typer:** framework para construir CLIs em Python sobre o Click.