FROM python:3.12-alpine

RUN apk add --no-cache \
    docker-cli \
    docker-cli-compose

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --upgrade pip \
    && pip install .

ENTRYPOINT ["devenv-doctor"]
CMD ["check", "."]