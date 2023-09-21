FROM python:3.9-buster AS production-environment

ENV PYTHONDONTWRITEBYTECODE=true \
    PYTHONIOENCODING=UTF-8 \
    POETRY_VERSION=1.3.2 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false

ENV PATH="${POETRY_HOME}/bin:${PATH}"

WORKDIR /usr/src/app

RUN apt-get update && \
    apt-get install -y vim-tiny less && \
    ln -s /usr/bin/vim.tiny /usr/bin/vim && \
    rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 -

COPY poetry.lock pyproject.toml ./
RUN poetry install --without dev --no-root --no-interaction

FROM production-environment AS dataops-image

COPY . .
ENTRYPOINT ["python3", "-m", "dataops"]

FROM production-environment AS development-environment

RUN poetry install --no-root --no-interaction

FROM development-environment AS alembic-image

ENV ALEMBIC_CONFIG=migrations/alembic.ini

COPY . .
ENTRYPOINT ["python3", "-m", "alembic"]

CMD ["upgrade", "head"]
