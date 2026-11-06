FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    TZ=America/Sao_Paulo \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# uv instala as dependências exatas do uv.lock.
RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev --python 3.12

# Código do app
COPY app.py ./
COPY evcomx_app ./evcomx_app
COPY scripts ./scripts
COPY .streamlit ./.streamlit

# Dados e artefatos usados em runtime
COPY data ./data
COPY models ./models
COPY dados-bootcamp/data/processed ./dados-bootcamp/data/processed
COPY dados-bootcamp/data/external ./dados-bootcamp/data/external
COPY projeto-bootcamp/data/raw ./projeto-bootcamp/data/raw
COPY projeto-bootcamp/relatorios_complementares ./projeto-bootcamp/relatorios_complementares
COPY projeto-bootcamp/models ./projeto-bootcamp/models

# Usuário sem privilégios
RUN useradd --create-home --uid 10001 appuser \
    && chown -R appuser:appuser /app
ENV HOME=/home/appuser
USER appuser

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8501/_stcore/health', timeout=3).read()" || exit 1

CMD ["streamlit", "run", "app.py", \
     "--server.address=0.0.0.0", \
     "--server.port=8501", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false"]
