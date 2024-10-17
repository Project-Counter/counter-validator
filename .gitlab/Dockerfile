FROM ubuntu:24.04

RUN apt update &&  \
    apt upgrade -y  &&  \
    apt install -y curl nodejs npm pipx && \
    pipx install poetry

RUN npm install -g corepack

RUN mkdir -p /builds/big-dig-data/counter-validation-tool/

COPY pyproject.toml /builds/big-dig-data/counter-validation-tool/pyproject.toml
COPY poetry.lock /builds/big-dig-data/counter-validation-tool/poetry.lock

RUN \
  export PATH="$PATH:/root/.local/bin" && \
  cd /builds/big-dig-data/counter-validation-tool/ && \
	poetry config virtualenvs.in-project true && \
	poetry config virtualenvs.options.no-setuptools true && \
	poetry install --no-root

COPY frontend/package.json /builds/big-dig-data/counter-validation-tool/frontend/package.json

RUN cd /builds/big-dig-data/counter-validation-tool/frontend && corepack enable && yarn install
