FROM python:3.13-slim-bookworm AS base

LABEL org.opencontainers.image.source="https://github.com/petrus-v/band-management" 
LABEL org.opencontainers.image.authors="Pierre Verkest <pierre@verkest.fr>"

ENV VIRTUAL_ENV=/anyblok
ENV PATH=/anyblok/bin:$PATH

# not sure we needs pg repo as pg release should be pushed in debian repos
#  curl https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - \
#     && echo "deb http://apt.postgresql.org/pub/repos/apt pgdg main" > /etc/apt/sources.list.d/pgdg.list \
#     &&
RUN apt update \
    && apt install -y --no-install-recommends       \
        gettext-base                                \
        ca-certificates                             \
        less                                        \
        nano                                        \
        gosu                                        \
        postgresql-client                           \
    && apt -y clean                                 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
ENV UV_PROJECT_ENVIRONMENT=$VIRTUAL_ENV
ENV UV_LINK_MODE=copy
ENV UV_COMPILE_BYTECODE=1
ENV UV_CACHE_DIR=/opt/uv-cache/



FROM base AS dependencies

# Install git and other build tools.
RUN set -e \
  && apt update \
  && apt -y install --no-install-recommends \
       git \
       python3-dev \
       build-essential \
       libpq-dev \
  && apt -y clean \
  && rm -rf /var/lib/apt/lists/*

# Install the locked dependencies in the virtual environment,
# but not the project
RUN --mount=type=cache,target=$UV_CACHE_DIR \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-editable



FROM base AS runtime

COPY --from=dependencies $VIRTUAL_ENV $VIRTUAL_ENV

# Install the app
COPY . /app
WORKDIR /app

RUN python -m compileall .
RUN --mount=type=cache,target=$UV_CACHE_DIR \
    uv sync --no-dev --frozen