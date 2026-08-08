# syntax=docker/dockerfile:1

# ---------- Stage: build ----------
# Imagem oficial do uv 0.12.3 com Python 3.12 (base bookworm-slim).
FROM ghcr.io/astral-sh/uv:0.12.3-python3.12-bookworm-slim AS build

WORKDIR /app

# Compila bytecode e copia pacotes do cache (necessário com cache mount).
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Instala apenas dependências de produção (sem extras dev), congeladas no lock.
# README.md é necessário porque o hatchling valida o campo `readme` do pyproject.
COPY pyproject.toml uv.lock README.md ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# Adiciona o código-fonte e instala o pacote (cria o entrypoint pdfstract-api).
COPY src ./src
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# ---------- Stage: runtime ----------
FROM python:3.12-slim-bookworm AS runtime

# libgomp1: exigida pelo onnxruntime (OpenMP).
# libgl1, libglib2.0-0, libsm6, libxext6, libxrender1: exigidas pelo
# opencv-python (dependência do rapidocr) no Debian slim.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libgomp1 \
        libgl1 \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV PATH="/app/.venv/bin:$PATH" \
    PDFSTRACT_HOST=0.0.0.0 \
    PDFSTRACT_PORT=5000

# Copia o ambiente virtual e o código do stage de build.
COPY --from=build /app/.venv ./.venv
COPY --from=build /app/src ./src

# Diretórios persistidos via volumes (uploads temporários e resultados).
RUN mkdir -p uploads output

EXPOSE 5000

CMD ["pdfstract-api"]