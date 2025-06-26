FROM ubuntu:24.04

RUN apt update &&  \
  apt upgrade -y  &&  \
  apt install -y curl nodejs npm pipx libmagic1t64 && \
  pipx install poetry

RUN npm install -g corepack

RUN mkdir -p /builds/big-dig-data/counter-validator/

COPY pyproject.toml /builds/big-dig-data/counter-validator/pyproject.toml
COPY poetry.lock /builds/big-dig-data/counter-validator/poetry.lock

RUN \
  export PATH="$PATH:/root/.local/bin" && \
  cd /builds/big-dig-data/counter-validator/ && \
  poetry config virtualenvs.in-project true && \
  poetry install --no-root

COPY frontend/package.json /builds/big-dig-data/counter-validator/frontend/package.json

RUN cd /builds/big-dig-data/counter-validator/frontend && corepack enable && yarn install
