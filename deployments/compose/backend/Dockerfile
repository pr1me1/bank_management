ARG PYTHON_VERSION=3.11
ARG UV_VERSION=0.7.2

FROM ghcr.io/astral-sh/uv:${UV_VERSION} AS uv

FROM python:${PYTHON_VERSION} AS builder

COPY --from=uv /uv /uvx /bin/

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    PYTHONBUFFERED=1 \
    UV_PROJECT_ENVIRONMENT=/opt/venv

WORKDIR /app

COPY pyproject.toml uv.lock* ./
COPY app ./app
COPY management ./management
COPY alembic ./alembic
COPY alembic.ini ./

RUN uv sync --no-dev --frozen --no-install-project --all-groups

RUN . /opt/venv/bin/activate && uv pip install -e .

FROM python:${PYTHON_VERSION} AS app

RUN apt-get update && \
    apt-get install -y --no-install-recommends fonts-dejavu && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV PYTHONBUFFERED=1 \
    PYTHONPATH=$PYTHONPATH:/app \
    VIRTUAL_ENV=/opt/venv \
    PATH=/opt/venv/bin:$PATH

COPY --from=builder /opt/venv /opt/venv

COPY ./pyproject.toml ./uv.lock ./
COPY . /app/

COPY ./deployments/compose/backend/celery/worker/start /start-celeryworker
RUN sed -i 's/\r$//g' /start-celeryworker && chmod +x /start-celeryworker

COPY ./deployments/compose/backend/celery/beat/start /start-celerybeat
RUN sed -i 's/\r$//g' /start-celerybeat && chmod +x /start-celerybeat

COPY ./deployments/compose/backend/celery/flower/start /start-flower
RUN sed -i 's/\r$//g' /start-flower && chmod +x /start-flower

COPY ./deployments/compose/backend/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint && chmod +x /entrypoint

COPY ./deployments/compose/backend/start /start
RUN sed -i 's/\r$//g' /start && chmod +x /start

COPY ./deployments/compose/backend/migrate /migrate
RUN sed -i 's/\r$//g' /migrate && chmod +x /migrate

RUN chgrp -R 0 /app && chmod -R g=u /app

ENTRYPOINT ["/entrypoint"]